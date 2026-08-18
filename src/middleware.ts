import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE_SESION, verificar } from "@/lib/sesion";

/**
 * Puerta de acceso al dashboard.
 *
 * Los datos son agregados de una tesis todavía no publicada, así que el sitio
 * no debe quedar abierto. La comprobación va AQUÍ, en el edge, y no en el
 * navegador: el JSON viaja dentro del bundle, de modo que una contraseña en
 * cliente sería decorativa — bastaría abrir el código fuente para leerlo todo.
 *
 * Antes esto era autenticación básica HTTP. Se cambió a sesión con cookie
 * porque la básica no admite cambiar la contraseña: el navegador cachea las
 * credenciales, no existe cerrar sesión, y la clave vivía en una variable de
 * entorno que sólo se puede tocar redesplegando.
 *
 * LA PÁGINA DE ACCESO SE SIRVE DESDE AQUÍ, COMO HTML AUTÓNOMO, Y ESO ES
 * DELIBERADO. Si fuese una ruta de Next habría que dejar pasar sin sesión sus
 * archivos de /_next/static, y el dataset completo viaja dentro del chunk de
 * la página: exactamente la fuga que se cerró el 2026-08-18. Sirviéndola con
 * su CSS en línea, no hay que eximir ningún asset y el matcher sigue
 * cubriéndolo todo.
 */

// Único punto abierto sin sesión: el formulario tiene que poder enviarse.
const ABIERTAS = new Set(["/api/entrar"]);

export async function middleware(req: NextRequest) {
  const secreto = process.env.SESION_SECRETO;
  // Sin secreto el sitio queda abierto: así el desarrollo local no pide
  // contraseña. Conviene no desplegar sin él.
  if (!secreto) return NextResponse.next();

  const ruta = req.nextUrl.pathname;
  if (ABIERTAS.has(ruta)) return NextResponse.next();

  if (await verificar(req.cookies.get(COOKIE_SESION)?.value, secreto)) {
    return NextResponse.next();
  }

  // A una llamada de API se le responde JSON, no la página de acceso: si la
  // sesión caduca con el dashboard abierto, el componente necesita distinguir
  // «sesión caducada» de «no hay red». Devolviendo HTML, su `r.json()` falla y
  // el usuario ve un error engañoso.
  if (ruta.startsWith("/api/")) {
    return NextResponse.json(
      { error: "sin_sesion" },
      { status: 401, headers: { "cache-control": "no-store" } },
    );
  }

  const destino = ruta + req.nextUrl.search;
  const fallo = req.nextUrl.searchParams.get("auth") === "error";

  return new NextResponse(paginaAcceso(destino, fallo), {
    status: 401,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/** Escapa para incrustar en un atributo HTML. El destino viene de la URL. */
function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function paginaAcceso(destino: string, fallo: boolean): string {
  return `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Acceso restringido</title>
<style>
  :root{color-scheme:light dark;--page:#f2f0eb;--surface:#faf8f5;--ink:#14140f;
    --ink-2:#52514e;--muted:#898781;--borde:rgb(20 20 15 / .14);--acento:#2a78d6;
    --mal:#c2410c}
  @media (prefers-color-scheme:dark){:root{--page:#0b0d0e;--surface:#16191b;
    --ink:#fff;--ink-2:#c3c2b7;--muted:#898781;--borde:rgb(255 255 255 / .14);
    --acento:#3987e5;--mal:#f97316}}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:grid;place-items:center;padding:1.5rem;
    background:var(--page);color:var(--ink);
    font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
    -webkit-font-smoothing:antialiased}
  main{width:100%;max-width:23rem}
  .marca{font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;
    color:var(--muted);margin:0 0 .9rem}
  h1{font-family:Georgia,"Times New Roman",serif;font-weight:600;
    letter-spacing:-.011em;font-size:1.5rem;line-height:1.2;margin:0 0 .6rem}
  p.sub{margin:0 0 1.6rem;font-size:.86rem;line-height:1.55;color:var(--ink-2)}
  form{background:var(--surface);border:1px solid var(--borde);border-radius:8px;
    padding:1.35rem}
  label{display:block;font-size:.76rem;color:var(--ink-2);margin:0 0 .35rem}
  input{width:100%;padding:.6rem .7rem;font-size:.92rem;color:var(--ink);
    background:transparent;border:1px solid var(--borde);border-radius:5px;
    font-family:inherit}
  input:focus-visible{outline:2px solid var(--acento);outline-offset:1px;
    border-color:transparent}
  .campo+.campo{margin-top:.9rem}
  button{width:100%;margin-top:1.3rem;padding:.65rem;font-size:.9rem;
    font-weight:600;color:#fff;background:var(--acento);border:0;
    border-radius:5px;cursor:pointer;font-family:inherit}
  button:hover{filter:brightness(1.08)}
  .error{margin:0 0 1rem;padding:.6rem .7rem;border-radius:5px;font-size:.8rem;
    line-height:1.45;color:var(--mal);border:1px solid currentColor}
  footer{margin-top:1.4rem;font-size:.7rem;line-height:1.5;color:var(--muted)}
</style>
</head>
<body>
<main>
  <p class="marca">Universidad Nacional de Colombia · Proyecto MSH</p>
  <h1>Foraminíferos y metano en el Caribe colombiano</h1>
  <p class="sub">Datos de una tesis todavía no publicada. El acceso es
    restringido.<br><span style="color:var(--muted)">Unpublished thesis data.
    Access is restricted.</span></p>
  <form method="post" action="/api/entrar">
    ${fallo ? '<p class="error">Usuario o contraseña incorrectos. · Wrong username or password.</p>' : ""}
    <input type="hidden" name="destino" value="${esc(destino)}">
    <div class="campo">
      <label for="usuario">Usuario · Username</label>
      <input id="usuario" name="usuario" autocomplete="username" required autofocus>
    </div>
    <div class="campo">
      <label for="clave">Contraseña · Password</label>
      <input id="clave" name="clave" type="password"
             autocomplete="current-password" required>
    </div>
    <button type="submit">Entrar · Sign in</button>
  </form>
  <footer>Erick F. Mendoza Rivero — Ingeniería Geológica, Facultad de Minas.</footer>
</main>
</body>
</html>`;
}

export const config = {
  // Se protege TODO, incluidos los chunks de /_next/static.
  //
  // Excluirlos parecía inofensivo y no lo era: el dataset viaja dentro del
  // chunk de la página, así que /_next/static/chunks/app/page-*.js servía los
  // datos completos sin pedir credenciales. Verificado contra el despliegue
  // real, no supuesto.
  matcher: ["/((?!favicon.ico).*)"],
};
