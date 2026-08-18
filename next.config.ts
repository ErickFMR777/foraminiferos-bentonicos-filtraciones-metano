import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Export estático puro: el sitio es público y no tiene nada que decidir en
  // servidor. No hay base de datos, ni API, ni consultas en runtime — los
  // datasets (555 KB en data/derived/, de los que ~440 KB llegan al cliente)
  // viajan dentro del bundle y Vercel los sirve desde CDN.
  //
  // Hubo una etapa con contraseña, y entonces esto NO podía llevar
  // output:"export": un export estático no admite middleware y la
  // comprobación tenía que ocurrir en el edge, antes de servir nada. Al
  // abrirlo al público se retiraron middleware, sesión y credenciales, y con
  // ellos desapareció el motivo. Si algún día vuelve a cerrarse, hay que
  // deshacer las dos cosas a la vez: quitar output:"export" Y devolver
  // src/middleware.ts. Sólo una de las dos deja el sitio abierto creyéndolo
  // cerrado.
  output: "export",
  images: { unoptimized: true },
  reactStrictMode: true,
};

export default nextConfig;
