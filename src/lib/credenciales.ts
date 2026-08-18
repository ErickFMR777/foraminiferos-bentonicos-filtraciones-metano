/**
 * credenciales.ts — Dónde vive la contraseña y cómo se comprueba.
 *
 * Se guarda en un almacén Vercel Blob PRIVADO, no en una variable de entorno,
 * porque una variable de entorno es inmutable en ejecución: cambiarla exige
 * un redespliegue y no se puede hacer desde la interfaz.
 *
 * El token del almacén (`BLOB_READ_WRITE_TOKEN`) alcanza SÓLO a este almacén.
 * Se descartó guardar la contraseña en Edge Config o en la propia variable de
 * entorno justamente por eso: escribir en ellas exige un token de la API de
 * Vercel con alcance sobre toda la cuenta, y una fuga comprometería los cinco
 * proyectos, no sólo este dashboard.
 *
 * Nunca se almacena la contraseña: sólo PBKDF2-SHA256 sobre ella, con sal
 * aleatoria por credencial. Se usa PBKDF2 y no bcrypt/argon2 porque es lo que
 * ofrece Web Crypto sin dependencias nativas.
 *
 * Sólo se importa desde manejadores de ruta (runtime Node). El middleware no
 * toca este módulo: valida la firma de la sesión y no necesita el almacén.
 */

import { get, put } from "@vercel/blob";

const RUTA = "auth/credenciales.json";
const ITERACIONES = 210_000;

export const MINIMO_CLAVE = 12;

export type Credenciales = {
  usuario: string;
  salt: string;
  hash: string;
  iteraciones: number;
  actualizado: string;
};

const enc = new TextEncoder();
const aHex = (b: Uint8Array) =>
  [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
const deHex = (s: string) =>
  Uint8Array.from(s.match(/../g) ?? [], (h) => parseInt(h, 16));

async function derivar(
  clave: string,
  salt: Uint8Array,
  iteraciones: number,
): Promise<Uint8Array> {
  const k = await crypto.subtle.importKey("raw", enc.encode(clave), "PBKDF2",
    false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: salt as BufferSource, iterations: iteraciones, hash: "SHA-256" },
    k,
    256,
  );
  return new Uint8Array(bits);
}

/** Comparación en tiempo constante: salir antes en el primer byte distinto
 *  filtra información sobre el hash. */
function iguales(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i];
  return d === 0;
}

export async function nuevas(
  usuario: string,
  clave: string,
): Promise<Credenciales> {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  return {
    usuario,
    salt: aHex(salt),
    hash: aHex(await derivar(clave, salt, ITERACIONES)),
    iteraciones: ITERACIONES,
    actualizado: new Date().toISOString(),
  };
}

async function leer(): Promise<Credenciales | null> {
  try {
    // useCache:false es imprescindible: tras cambiar la contraseña, una
    // lectura cacheada devolvería la anterior y el usuario quedaría fuera.
    const r = await get(RUTA, { access: "private", useCache: false });
    if (!r || r.statusCode !== 200) return null;
    return JSON.parse(await new Response(r.stream).text()) as Credenciales;
  } catch {
    return null;
  }
}

export async function guardar(c: Credenciales): Promise<void> {
  await put(RUTA, JSON.stringify(c), {
    access: "private",
    addRandomSuffix: false,
    allowOverwrite: true,
    contentType: "application/json",
    cacheControlMaxAge: 0,
  });
}

/**
 * Credenciales en vigor. Si el almacén está vacío —primer arranque— se siembra
 * con `DASHBOARD_USUARIO` / `DASHBOARD_CLAVE`. A partir de ahí manda el
 * almacén y esas variables se ignoran.
 *
 * De ahí sale también la vía de recuperación si se olvida la contraseña:
 * borrar el blob `auth/credenciales.json` devuelve el control a las variables
 * de entorno.
 */
export async function vigentes(): Promise<Credenciales | null> {
  const guardadas = await leer();
  if (guardadas) return guardadas;

  const usuario = process.env.DASHBOARD_USUARIO;
  const clave = process.env.DASHBOARD_CLAVE;
  if (!usuario || !clave) return null;

  const sembradas = await nuevas(usuario, clave);
  await guardar(sembradas);
  return sembradas;
}

export async function comprueba(
  c: Credenciales,
  usuario: string,
  clave: string,
): Promise<boolean> {
  const h = await derivar(clave, deHex(c.salt), c.iteraciones);
  // Se comprueban ambos factores siempre, sin cortocircuito, para no revelar
  // por tiempo si el fallo estuvo en el usuario o en la contraseña.
  const usuarioOk = usuario === c.usuario;
  const claveOk = iguales(h, deHex(c.hash));
  return usuarioOk && claveOk;
}
