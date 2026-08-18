import { NextResponse } from "next/server";
import { COOKIE_SESION } from "@/lib/sesion";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  // Al borrar la cookie, el middleware devolverá la página de acceso.
  const res = NextResponse.redirect(new URL("/", req.url), 303);
  res.cookies.set(COOKIE_SESION, "", { path: "/", maxAge: 0 });
  return res;
}
