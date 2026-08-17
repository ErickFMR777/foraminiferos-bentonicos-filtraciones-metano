import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Export estático: el dataset completo son ~140 KB, así que todo se
  // prerenderiza y Vercel lo sirve desde CDN. Sin funciones serverless,
  // sin base de datos, sin latencia de consulta.
  output: "export",
  images: { unoptimized: true },
  reactStrictMode: true,
};

export default nextConfig;
