"use client";

import { useState } from "react";
import estudios from "@datos/estudios.json";
import { useT } from "@/lib/i18n";
import { Nota } from "@/lib/ui";

export default function Referencias() {
  const { tx } = useT();
  const [abierto, setAbierto] = useState(false);
  const orden = [...estudios].sort((a, b) =>
    ((a.autores ?? ["z"])[0] ?? "z").localeCompare((b.autores ?? ["z"])[0] ?? "z"),
  );

  return (
    <div>
      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        aria-expanded={abierto}
        className="text-[0.85rem] underline underline-offset-2 hover:text-(--ink)"
      >
        {abierto ? "− " : "+ "}
        {tx({
          es: "Ver las " + estudios.length + " referencias",
          en: "Show the " + estudios.length + " references",
        })}
      </button>

      {abierto && (
        <ol className="mt-5 space-y-3.5">
          {orden.map((e) => (
            <li key={e.id} className="text-[0.8rem] leading-relaxed">
              <span className="text-(--ink)">
                {(e.autores ?? []).join(", ") ||
                  tx({ es: "(autoría sin resolver)", en: "(authorship unresolved)" })}
                {e.anio ? " (" + e.anio + ")" : ""}.
              </span>{" "}
              <span className="text-(--ink-2)">{e.titulo}.</span>{" "}
              {e.revista && <em className="text-(--ink-2)">{e.revista}. </em>}
              {e.doi && (
                <a
                  href={"https://doi.org/" + e.doi}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-(--pared-hialino) underline underline-offset-2"
                >
                  doi:{e.doi}
                </a>
              )}
              <span className="ml-1 text-(--muted)">
                · {e.localidad ?? tx({ es: "localidad sin determinar", en: "locality undetermined" })}
              </span>
            </li>
          ))}
        </ol>
      )}

      <Nota>
        {tx({
          es: "Las referencias se citan; los documentos no se publican. Los datos primarios de la tesis y del proyecto MSH son inéditos y quedan reservados para su publicación académica.",
          en: "References are cited; the documents are not published. The primary data of the thesis and the MSH project are unpublished and reserved for academic publication.",
        })}
      </Nota>
    </div>
  );
}
