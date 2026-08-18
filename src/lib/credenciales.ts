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
  /**
   * Segunda barrera, y SÓLO para cambiar la contraseña. Es lo que permite
   * enseñarle el dashboard a alguien —dándole la contraseña— sin que pueda
   * dejar al autor fuera de su propio sitio.
   *
   * Opcionales porque el almacén pudo sembrarse antes de que existiera esta
   * barrera; `vigentes()` los rellena al vuelo desde el entorno.
   */
  respuestaSalt?: string;
  respuestaHash?: string;
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

/** La respuesta se compara TAL CUAL: mayúsculas y minúsculas cuentan. Sólo se
 *  recortan los espacios de los extremos, que suelen venir de un copiado y no
 *  son parte de lo que nadie quiso escribir. */
const normalizaRespuesta = (s: string) => s.trim();

export async function nuevas(
  usuario: string,
  clave: string,
  anteriores?: Credenciales,
): Promise<Credenciales> {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  return {
    usuario,
    salt: aHex(salt),
    hash: aHex(await derivar(clave, salt, ITERACIONES)),
    iteraciones: ITERACIONES,
    actualizado: new Date().toISOString(),
    // Cambiar la contraseña NO cambia la respuesta de seguridad: se arrastra
    // tal cual. Si se perdiera aquí, el primer cambio desactivaría la barrera.
    respuestaSalt: anteriores?.respuestaSalt,
    respuestaHash: anteriores?.respuestaHash,
  };
}

async function conRespuesta(
  c: Credenciales,
  respuesta: string,
): Promise<Credenciales> {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  return {
    ...c,
    respuestaSalt: aHex(salt),
    respuestaHash: aHex(
      await derivar(normalizaRespuesta(respuesta), salt, ITERACIONES),
    ),
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
  if (guardadas) {
    // El almacén se sembró antes de que existiera la pregunta de seguridad.
    // Se le añade ahora desde el entorno, sin tocar la contraseña.
    if (!guardadas.respuestaHash && process.env.DASHBOARD_RESPUESTA) {
      const migradas = await conRespuesta(
        guardadas,
        process.env.DASHBOARD_RESPUESTA,
      );
      await guardar(migradas);
      return migradas;
    }
    return guardadas;
  }

  const usuario = process.env.DASHBOARD_USUARIO;
  const clave = process.env.DASHBOARD_CLAVE;
  if (!usuario || !clave) return null;

  let sembradas = await nuevas(usuario, clave);
  if (process.env.DASHBOARD_RESPUESTA) {
    sembradas = await conRespuesta(sembradas, process.env.DASHBOARD_RESPUESTA);
  }
  await guardar(sembradas);
  return sembradas;
}

/**
 * Comprueba la respuesta a la pregunta de seguridad.
 *
 * Si no hay ninguna configurada devuelve `false`, no `true`: ante un fallo de
 * configuración la barrera debe cerrarse, no abrirse. Un almacén sin respuesta
 * bloquea el cambio de contraseña hasta definir `DASHBOARD_RESPUESTA`, que es
 * el lado seguro del error.
 */
export async function compruebaRespuesta(
  c: Credenciales,
  respuesta: string,
): Promise<boolean> {
  if (!c.respuestaSalt || !c.respuestaHash) return false;
  const h = await derivar(
    normalizaRespuesta(respuesta),
    deHex(c.respuestaSalt),
    c.iteraciones,
  );
  return iguales(h, deHex(c.respuestaHash));
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
