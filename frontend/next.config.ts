import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,

  // Configuración para producción con Docker
  output: "standalone",

  // Comprimir assets
  compress: true,

  // Optimización de imágenes
  images: {
    unoptimized: false,
    remotePatterns: [],
  },
};

export default nextConfig;
