/**
 * sesion.ts — Firma y verificación del testigo de sesión.
 *
 * Usa sólo Web Crypto, de modo que el MISMO código corre en el middleware
 * (edge) y en los manejadores de ruta (Node). Nada de `Buffer` ni de `crypto`
 * de Node: en el edge no existen.
 *
 * El testigo va firmado con HMAC-SHA256 y lleva su propia caducidad dentro.
 * Gracias a eso el middleware valida la sesión SIN leer el almacén: sería una
 * petición de red en cada visita, y aquí se comprueba en microsegundos.
 *
 * La contrapartida, y conviene tenerla presente: un testigo ya emitido sigue
 * siendo válido hasta que caduca, aunque se cambie la contraseña. Por eso la
 * duración es corta y el cambio de contraseña reemite el testigo del navegador
 * que lo solicita.
 */

const enc = new TextEncoder();

export const COOKIE_SESION = "sesion";
export const HORAS_SESION = 12;

function aB64url(bytes: Uint8Array): string {
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// El ArrayBuffer se reserva explícitamente: `Uint8Array.from` devuelve
// Uint8Array<ArrayBufferLike>, que Web Crypto no acepta como BufferSource
// porque ese tipo admite también SharedArrayBuffer.
function deB64url(s: string): Uint8Array<ArrayBuffer> {
  const t = s.replace(/-/g, "+").replace(/_/g, "/");
  const bin = atob(t + "=".repeat((4 - (t.length % 4)) % 4));
  const out = new Uint8Array(new ArrayBuffer(bin.length));
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function clave(secreto: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    "raw",
    enc.encode(secreto),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
}

export async function firmar(usuario: string, secreto: string): Promise<string> {
  const cuerpo = aB64url(
    enc.encode(
      JSON.stringify({ u: usuario, exp: Date.now() + HORAS_SESION * 3600_000 }),
    ),
  );
  const firma = new Uint8Array(
    await crypto.subtle.sign("HMAC", await clave(secreto), enc.encode(cuerpo)),
  );
  return `${cuerpo}.${aB64url(firma)}`;
}

/** Devuelve el usuario si el testigo es auténtico y no ha caducado. */
export async function verificar(
  testigo: string | undefined,
  secreto: string,
): Promise<{ usuario: string } | null> {
  if (!testigo) return null;
  const [cuerpo, firma] = testigo.split(".");
  if (!cuerpo || !firma) return null;

  try {
    const valida = await crypto.subtle.verify(
      "HMAC",
      await clave(secreto),
      deB64url(firma),
      enc.encode(cuerpo),
    );
    if (!valida) return null;

    const d = JSON.parse(new TextDecoder().decode(deB64url(cuerpo)));
    if (typeof d?.exp !== "number" || Date.now() > d.exp) return null;
    return { usuario: String(d.u) };
  } catch {
    // Un testigo manipulado puede romper atob o JSON.parse. Es un fallo de
    // autenticación, no un error del servidor.
    return null;
  }
}

/** Opciones de la cookie. `secure` se apaga en local, donde no hay HTTPS. */
export function opcionesCookie(produccion: boolean) {
  return {
    httpOnly: true,
    secure: produccion,
    sameSite: "lax" as const,
    path: "/",
    maxAge: HORAS_SESION * 3600,
  };
}
