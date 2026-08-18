"use client";

import { useEffect, useState } from "react";
import { useApp, useT } from "@/lib/i18n";

export default function Barra() {
  const { idioma, setIdioma } = useApp();
  const { t, tx } = useT();
  const [tema, setTema] = useState<"light" | "dark" | null>(null);

  useEffect(() => {
    const g = localStorage.getItem("tema");
    if (g === "dark" || g === "light") setTema(g);
  }, []);

  const cambiarTema = () => {
    const nuevo = tema === "dark" ? "light" : "dark";
    setTema(nuevo);
    localStorage.setItem("tema", nuevo);
    document.documentElement.dataset.theme = nuevo;
  };

  const btn = "px-2.5 py-1 text-[0.72rem] rounded-[4px] transition-colors";
  const activo = "bg-(--ink) text-(--surface)";
  const inactivo = "text-(--muted) hover:text-(--ink)";

  return (
    <div className="sticky top-0 z-50 border-b border-(--border) bg-(--page)/90 backdrop-blur">
      <div className="mx-auto flex max-w-[68rem] flex-wrap items-center gap-x-5 gap-y-2 px-6 py-2.5">
        <span className="mr-auto text-[0.72rem] font-medium tracking-wide text-(--muted)">
          {tx({
            es: "Foraminíferos bentónicos · Filtraciones de metano",
            en: "Benthic foraminifera · Methane seeps",
          })}
        </span>

        <div className="flex gap-1" role="group" aria-label={t("idioma")}>
          {(["es", "en"] as const).map((i) => (
            <button
              key={i}
              type="button"
              onClick={() => setIdioma(i)}
              aria-pressed={idioma === i}
              className={btn + " " + (idioma === i ? activo : inactivo)}
            >
              {i.toUpperCase()}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={cambiarTema}
          className={btn + " " + inactivo}
          aria-label={t("tema")}
        >
          {tema === "dark" ? "☾" : "☀"}
        </button>
      </div>
    </div>
  );
}
