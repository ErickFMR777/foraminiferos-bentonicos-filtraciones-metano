"use client";

import { useState } from "react";
import estudios from "@datos/estudios.json";
import sinu from "@datos/sinu_2024.json";
import { useT } from "@/lib/i18n";
import { Nota } from "@/lib/ui";

export default function Referencias() {
  const { tx } = useT();
  const [abierto, setAbierto] = useState(false);
  // Barragán-Jacksson y Bernal (2024) NO está en estudios.json a propósito: se
  // mantiene fuera de la base analítica para no llenar con él la celda tropical
  // somera que sostiene el argumento central. Pero es la fuente entera de la
  // sección 05, y quedaba sin aparecer en la única lista de fuentes del
  // dashboard. Una cosa es no analizarlo con los demás y otra no citarlo.
  const orden = [
    ...estudios,
    { id: "sinu2024", autores: sinu.autores, anio: sinu.anio, titulo: sinu.titulo,
      revista: sinu.revista, doi: sinu.doi, localidad: sinu.localidad },
  ].sort((a, b) =>
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
          es: "Ver las " + orden.length + " referencias",
          en: "Show the " + orden.length + " references",
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
          es: "Las referencias se citan; los documentos no se publican. Los datos primarios de la tesis y del proyecto MSH son inéditos y quedan reservados para su publicación académica. Cada obra citada es de sus autores: lo que este dashboard aporta es la curación y la comparación, no los datos ajenos, y quien quiera usar un resultado publicado debe citar el artículo original.",
          en: "References are cited; the documents are not published. The primary data of the thesis and the MSH project are unpublished and reserved for academic publication. Each work cited belongs to its authors: what this dashboard contributes is the curation and the comparison, not other people's data, and anyone using a published result should cite the original article.",
        })}
      </Nota>
    </div>
  );
}
