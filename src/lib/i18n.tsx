"use client";

import { createContext, useContext, useEffect, useState } from "react";

type Idioma = "es" | "en";

/** Cadenas de la interfaz. El contenido largo vive en cada componente como
 *  par {es, en}; aquí sólo lo que se repite. */
const DIC = {
  es: {
    metodo: "Cómo se lee",
    tema: "Tema",
    idioma: "Idioma",
  },
  en: {
    metodo: "How to read this",
    tema: "Theme",
    idioma: "Language",
  },
} as const;

type Clave = keyof typeof DIC.es;

const Ctx = createContext<{
  idioma: Idioma;
  setIdioma: (i: Idioma) => void;
}>({ idioma: "es", setIdioma: () => {} });

export function Proveedor({ children }: { children: React.ReactNode }) {
  const [idioma, setIdiomaEstado] = useState<Idioma>("es");

  useEffect(() => {
    const g = localStorage.getItem("idioma");
    if (g === "es" || g === "en") setIdiomaEstado(g);
  }, []);

  const setIdioma = (i: Idioma) => {
    setIdiomaEstado(i);
    localStorage.setItem("idioma", i);
    document.documentElement.lang = i;
  };

  return (
    <Ctx.Provider value={{ idioma, setIdioma }}>
      {children}
    </Ctx.Provider>
  );
}

export const useApp = () => useContext(Ctx);

export function useT() {
  const { idioma } = useApp();
  const t = (k: Clave) => DIC[idioma][k];
  /** Elige entre un par {es, en}. */
  const tx = (par: { es: string; en: string }) => par[idioma];
  return { t, tx, idioma };
}
