"use client";

import { createContext, useContext, useEffect, useState } from "react";

export type Idioma = "es" | "en";

/** Cadenas de la interfaz. El contenido largo vive en cada componente como
 *  par {es, en}; aquí sólo lo que se repite. */
const DIC = {
  es: {
    modoNarrativa: "Narrativa",
    modoExploracion: "Exploración",
    verTabla: "Ver como tabla",
    ocultarTabla: "Ocultar tabla",
    sinDatos: "sin datos",
    estudios: "estudios",
    estudio: "estudio",
    registros: "registros",
    taxones: "taxones",
    especies: "especies",
    generos: "géneros",
    profundidad: "Profundidad",
    latitud: "Latitud",
    fuente: "Fuente",
    metodo: "Cómo se lee",
    tema: "Tema",
    idioma: "Idioma",
  },
  en: {
    modoNarrativa: "Narrative",
    modoExploracion: "Explore",
    verTabla: "View as table",
    ocultarTabla: "Hide table",
    sinDatos: "no data",
    estudios: "studies",
    estudio: "study",
    registros: "records",
    taxones: "taxa",
    especies: "species",
    generos: "genera",
    profundidad: "Depth",
    latitud: "Latitude",
    fuente: "Source",
    metodo: "How to read this",
    tema: "Theme",
    idioma: "Language",
  },
} as const;

type Clave = keyof typeof DIC.es;

const Ctx = createContext<{
  idioma: Idioma;
  setIdioma: (i: Idioma) => void;
  modo: "narrativa" | "exploracion";
  setModo: (m: "narrativa" | "exploracion") => void;
}>({ idioma: "es", setIdioma: () => {}, modo: "narrativa", setModo: () => {} });

export function Proveedor({ children }: { children: React.ReactNode }) {
  const [idioma, setIdiomaEstado] = useState<Idioma>("es");
  const [modo, setModoEstado] = useState<"narrativa" | "exploracion">("narrativa");

  useEffect(() => {
    const g = localStorage.getItem("idioma");
    if (g === "es" || g === "en") setIdiomaEstado(g);
    const m = localStorage.getItem("modo");
    if (m === "narrativa" || m === "exploracion") setModoEstado(m);
  }, []);

  const setIdioma = (i: Idioma) => {
    setIdiomaEstado(i);
    localStorage.setItem("idioma", i);
    document.documentElement.lang = i;
  };
  const setModo = (m: "narrativa" | "exploracion") => {
    setModoEstado(m);
    localStorage.setItem("modo", m);
  };

  return (
    <Ctx.Provider value={{ idioma, setIdioma, modo, setModo }}>
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
