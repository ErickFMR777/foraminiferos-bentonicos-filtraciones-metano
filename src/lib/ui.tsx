"use client";

import { useState } from "react";
import { useApp, useT } from "./i18n";

/** Nombre científico. Los taxones van SIEMPRE en cursiva: es la convención
 *  taxonómica y un especialista lo nota en el primer segundo. Las entradas de
 *  género abierto («Uvigerina spp.») llevan el calificador en redonda. */
/** Formatea una cifra según el idioma activo: coma decimal en español, punto
 *  en inglés. Existe porque el proyecto tenía tres criterios a la vez —helper
 *  propio en un componente, `.replace(".", ",")` a mano (que dejaba coma
 *  también en inglés) y `.toFixed()` crudo (que dejaba punto también en
 *  español)—, y en producción se veía «H' 3.43» en la versión española. Toda
 *  cifra VISIBLE pasa por aquí; los valores de `style` no, que son CSS. */
export function useNum() {
  const { idioma } = useApp();
  return (v: number, d = 1) =>
    v.toFixed(d).replace(".", idioma === "es" ? "," : ".");
}

export function Taxon({ nombre }: { nombre: string }) {
  const m = nombre.match(/^(.*?)(\s+(?:spp?\.|sp\.))$/);
  return m ? (
    <>
      <i className="taxon">{m[1]}</i>
      {m[2]}
    </>
  ) : (
    <i className="taxon">{nombre}</i>
  );
}

export function Cifra({
  valor,
  etiqueta,
  nota,
}: {
  valor: React.ReactNode;
  etiqueta: string;
  nota?: string;
}) {
  return (
    <div>
      <div className="text-[2.4rem] font-semibold leading-none tabular">{valor}</div>
      <div className="mt-2 text-[0.8rem] leading-snug text-(--muted)">{etiqueta}</div>
      {nota && (
        <div className="mt-1 text-[0.7rem] leading-snug text-(--muted) opacity-80">
          {nota}
        </div>
      )}
    </div>
  );
}

/** Bloque plegable con la explicación de un gráfico. Plegado por defecto:
 *  quien ya sabe leerlo no debería tropezar con él. */
export function ComoSeLee({ children }: { children: React.ReactNode }) {
  const { t } = useT();
  const [abierto, setAbierto] = useState(false);
  return (
    <div className="mt-4">
      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        aria-expanded={abierto}
        className="text-[0.75rem] text-(--muted) underline underline-offset-2 hover:text-(--ink)"
      >
        {abierto ? "− " : "+ "}
        {t("metodo")}
      </button>
      {abierto && (
        <div className="mt-2 max-w-[62ch] border-l-2 border-(--axis) pl-3 text-[0.8rem] leading-relaxed text-(--ink-2)">
          {children}
        </div>
      )}
    </div>
  );
}

export function Seccion({
  n,
  titulo,
  entradilla,
  children,
}: {
  n: string;
  titulo: string;
  entradilla?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="border-t border-(--border) py-14 md:py-20">
      <p className="mb-3 text-[0.72rem] uppercase tracking-[0.16em] text-(--muted)">
        {n}
      </p>
      <h2 className="mb-4 max-w-[24ch] text-[1.75rem] leading-[1.2] md:text-[2.1rem]">
        {titulo}
      </h2>
      {entradilla && (
        <div className="mb-8 max-w-[62ch] text-[1rem] leading-relaxed text-(--ink-2)">
          {entradilla}
        </div>
      )}
      {children}
    </section>
  );
}

export function Nota({ children }: { children: React.ReactNode }) {
  return (
    <p className="mt-4 max-w-[64ch] text-[0.72rem] leading-relaxed text-(--muted)">
      {children}
    </p>
  );
}
