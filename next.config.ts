import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Todas las páginas se prerenderizan en build y Vercel las sirve desde CDN:
  // el dataset completo son ~196 KB y viaja en el bundle, sin base de datos ni
  // consultas en runtime.
  //
  // NO se usa output:"export" porque el sitio va protegido con contraseña, y
  // un export puramente estático no admite middleware: la comprobación tiene
  // que ocurrir en el edge antes de servir nada. Para abrirlo al público
  // basta con quitar src/middleware.ts y devolver output:"export".
  images: { unoptimized: true },
  reactStrictMode: true,
};

export default nextConfig;
