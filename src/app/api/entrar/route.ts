import { NextResponse } from "next/server";
import { COOKIE_SESION, firmar, opcionesCookie } from "@/lib/sesion";
import { comprueba, vigentes } from "@/lib/credenciales";

// Node y no edge: aquí sí se lee el almacén de credenciales.
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Un fallo de contraseña siempre tarda algo. No es defensa seria contra un
 *  atacante decidido, pero encarece el ensayo y error desde un navegador. */
const espera = () => new Promise((r) => setTimeout(r, 700));

/** Sólo se admite volver a una ruta interna: si se aceptara una URL absoluta,
 *  el formulario serviría para redirigir a un sitio ajeno. */
function destinoSeguro(valor: string | null): string {
  if (!valor || !valor.startsWith("/") || valor.startsWith("//")) return "/";
  return valor.split("?")[0] || "/";
}

export async function POST(req: Request) {
  const secreto = process.env.SESION_SECRETO;
  if (!secreto) {
    return NextResponse.json({ error: "sin_secreto" }, { status: 500 });
  }

  const form = await req.formData();
  const usuario = String(form.get("usuario") ?? "");
  const clave = String(form.get("clave") ?? "");
  const destino = destinoSeguro(
    typeof form.get("destino") === "string" ? String(form.get("destino")) : null,
  );

  const credenciales = await vigentes();
  const correcto =
    credenciales !== null && (await comprueba(credenciales, usuario, clave));

  if (!correcto) {
    await espera();
    const url = new URL(destino, req.url);
    url.searchParams.set("auth", "error");
    return NextResponse.redirect(url, 303);
  }

  // 303 para que el navegador cambie el POST por un GET al seguir la redirección.
  const res = NextResponse.redirect(new URL(destino, req.url), 303);
  res.cookies.set(
    COOKIE_SESION,
    await firmar(credenciales.usuario, secreto),
    opcionesCookie(process.env.NODE_ENV === "production"),
  );
  return res;
}
