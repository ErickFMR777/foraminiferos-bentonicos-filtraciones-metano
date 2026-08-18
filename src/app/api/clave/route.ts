import { NextResponse } from "next/server";
import { COOKIE_SESION, firmar, opcionesCookie, verificar } from "@/lib/sesion";
import {
  MINIMO_CLAVE,
  comprueba,
  compruebaRespuesta,
  guardar,
  nuevas,
  vigentes,
} from "@/lib/credenciales";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const espera = () => new Promise((r) => setTimeout(r, 700));

export async function POST(req: Request) {
  const secreto = process.env.SESION_SECRETO;
  if (!secreto) {
    return NextResponse.json({ error: "sin_secreto" }, { status: 500 });
  }

  // El middleware ya exige sesión para llegar aquí. Se vuelve a comprobar de
  // todos modos: un manejador que cambia la contraseña no debe depender de
  // que otra capa haya hecho su trabajo.
  const cookie = req.headers
    .get("cookie")
    ?.split("; ")
    .find((c) => c.startsWith(`${COOKIE_SESION}=`))
    ?.slice(COOKIE_SESION.length + 1);
  const sesion = await verificar(cookie, secreto);
  if (!sesion) {
    return NextResponse.json({ error: "sin_sesion" }, { status: 401 });
  }

  // La cookie es SameSite=Lax, que ya frena el envío entre sitios, pero una
  // petición desde otro origen no debería llegar a ejecutarse.
  const origen = req.headers.get("origin");
  if (origen && new URL(origen).host !== new URL(req.url).host) {
    return NextResponse.json({ error: "origen_ajeno" }, { status: 403 });
  }

  let cuerpo: { actual?: unknown; nueva?: unknown; respuesta?: unknown };
  try {
    cuerpo = await req.json();
  } catch {
    return NextResponse.json({ error: "cuerpo_invalido" }, { status: 400 });
  }

  const actual = typeof cuerpo.actual === "string" ? cuerpo.actual : "";
  const nueva = typeof cuerpo.nueva === "string" ? cuerpo.nueva : "";
  const respuesta =
    typeof cuerpo.respuesta === "string" ? cuerpo.respuesta : "";

  if (nueva.length < MINIMO_CLAVE) {
    return NextResponse.json({ error: "corta" }, { status: 400 });
  }
  if (nueva === actual) {
    return NextResponse.json({ error: "sin_cambio" }, { status: 400 });
  }

  const credenciales = await vigentes();
  if (!credenciales) {
    return NextResponse.json({ error: "sin_credenciales" }, { status: 500 });
  }

  // La pregunta de seguridad va PRIMERO y es independiente de la contraseña:
  // quien recibe el dashboard para verlo conoce la contraseña, y esta barrera
  // es justo lo que le impide cambiarla y dejar fuera al autor.
  if (!(await compruebaRespuesta(credenciales, respuesta))) {
    await espera();
    return NextResponse.json({ error: "respuesta_incorrecta" }, { status: 403 });
  }

  if (!(await comprueba(credenciales, sesion.usuario, actual))) {
    await espera();
    return NextResponse.json({ error: "actual_incorrecta" }, { status: 403 });
  }

  // Se pasan las credenciales anteriores para arrastrar la respuesta de
  // seguridad: cambiar la contraseña no debe desarmar la barrera.
  await guardar(await nuevas(credenciales.usuario, nueva, credenciales));

  // Se reemite el testigo de ESTE navegador para que la sesión siga viva. Los
  // testigos ya emitidos en otros navegadores siguen valiendo hasta caducar:
  // es la contrapartida de validar la sesión sin leer el almacén, y por eso
  // duran pocas horas.
  const res = NextResponse.json({ ok: true });
  res.cookies.set(
    COOKIE_SESION,
    await firmar(credenciales.usuario, secreto),
    opcionesCookie(process.env.NODE_ENV === "production"),
  );
  return res;
}
