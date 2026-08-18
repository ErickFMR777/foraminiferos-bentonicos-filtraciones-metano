import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Puerta de acceso al dashboard.
 *
 * Los datos son agregados de una tesis todavía no publicada, así que el sitio
 * no debe quedar abierto. La comprobación va AQUÍ, en el edge, y no en el
 * navegador: con un export estático el JSON viaja dentro del bundle, de modo
 * que una contraseña en cliente sería decorativa — bastaría abrir el código
 * fuente para leerlo todo.
 *
 * Credenciales en variables de entorno de Vercel:
 *   DASHBOARD_USUARIO, DASHBOARD_CLAVE
 * Si no están definidas, el sitio queda abierto: así el desarrollo local no
 * pide contraseña, pero conviene no desplegar sin ellas.
 */
export function middleware(req: NextRequest) {
  const usuario = process.env.DASHBOARD_USUARIO;
  const clave = process.env.DASHBOARD_CLAVE;
  if (!usuario || !clave) return NextResponse.next();

  const cabecera = req.headers.get("authorization");
  if (cabecera?.startsWith("Basic ")) {
    const [u, c] = atob(cabecera.slice(6)).split(":");
    if (u === usuario && c === clave) return NextResponse.next();
  }

  return new NextResponse("Acceso restringido", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="Dashboard foraminíferos", charset="UTF-8"',
    },
  });
}

export const config = {
  // Se protege TODO, incluidos los chunks de /_next/static.
  //
  // Excluirlos parecía inofensivo y no lo era: el dataset viaja dentro del
  // chunk de la página, así que /_next/static/chunks/app/page-*.js servía los
  // datos completos sin pedir credenciales. Verificado contra el despliegue
  // real, no supuesto.
  //
  // Funciona porque la autenticación básica hace que el navegador reenvíe la
  // cabecera Authorization a todas las peticiones del mismo origen, de modo
  // que los assets cargan con normalidad tras el primer acceso.
  matcher: ["/((?!favicon.ico).*)"],
};
