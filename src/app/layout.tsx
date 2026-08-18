import type { Metadata } from "next";
import { Inter, Source_Serif_4 } from "next/font/google";
import "./globals.css";
import { Proveedor } from "@/lib/i18n";

const sans = Inter({
  subsets: ["latin"],
  variable: "--fuente-sans",
  display: "swap",
});

const serif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--fuente-serif",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Foraminíferos y metano en el Caribe colombiano",
  description:
    "Asociaciones de foraminíferos bentónicos en filtraciones de metano: " +
    "38 estudios en todo el mundo frente a una muestra de la plataforma " +
    "continental del Caribe colombiano.",
  authors: [{ name: "Erick Francisco Mendoza Rivero" }],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <head>
        {/* Aplica el tema antes de pintar para evitar el destello claro.
            Se ejecuta síncrono a propósito. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem("tema");
              if(t==="dark"||t==="light")document.documentElement.dataset.theme=t;
            }catch(e){}})();`,
          }}
        />
      </head>
      <body className={`${sans.variable} ${serif.variable}`}>
        <Proveedor>{children}</Proveedor>
      </body>
    </html>
  );
}
