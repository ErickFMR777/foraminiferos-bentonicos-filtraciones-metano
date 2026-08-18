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
  title: "Foraminíferos bentónicos en filtraciones de metano",
  description:
    "Análisis de las asociaciones de foraminíferos bentónicos en filtraciones " +
    "de metano: comparación entre distintas localidades del mundo y la " +
    "plataforma continental del Caribe colombiano. A partir de la tesis de " +
    "Erick Francisco Mendoza Rivero, Ingeniero Geólogo, Universidad Nacional " +
    "de Colombia, sede Medellín, Facultad de Minas. Proyecto Methane Seep " +
    "Hunting (MSH).",
  authors: [
    {
      name: "Erick Francisco Mendoza Rivero, Ingeniero Geólogo — Universidad Nacional de Colombia, sede Medellín, Facultad de Minas",
    },
  ],
  // El sitio es de acceso restringido: no debe acabar indexado.
  robots: { index: false, follow: false },
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
