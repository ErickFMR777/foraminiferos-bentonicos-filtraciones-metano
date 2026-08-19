"use client";

import { useState } from "react";
import msh from "@datos/msh_bc21.json";
import solape from "@datos/solape.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota, Taxon, useNum } from "@/lib/ui";

const COLOR: Record<string, string> = {
  Hialino: "var(--pared-hialino)",
  Porcelanaceo: "var(--pared-porcelanaceo)",
  Aglutinado: "var(--pared-aglutinado)",
  Monocristalino: "var(--pared-monocristalino)",
};

const ETIQ: Record<string, { es: string; en: string }> = {
  Hialino: { es: "Calcáreo hialino", en: "Hyaline calcareous" },
  Porcelanaceo: { es: "Calcáreo porcelanáceo", en: "Porcelaneous calcareous" },
  Aglutinado: { es: "Aglutinado", en: "Agglutinated" },
  Monocristalino: { es: "Calcáreo monocristalino", en: "Monocrystalline calcareous" },
};

export default function Composicion() {
  const { tx } = useT();
  const num = useNum();
  const [n, setN] = useState(15);
  const esp = msh.especies;
  const max = esp[0].abundancia_rel;
  const compartidos = new Set(
    solape.generos.compartidos.map((g) => g.toLowerCase()),
  );

  return (
    <figure className="m-0">
      <div className="mb-8">
        <div className="mb-2 flex h-8 gap-[2px] overflow-hidden rounded-[4px]">
          {Object.entries(msh.subtipo).map(([k, v]) => (
            <div
              key={k}
              style={{ width: v + "%", background: COLOR[k] }}
              title={k + " " + v + "%"}
            />
          ))}
        </div>
        <div className="flex flex-wrap gap-x-5 gap-y-1.5 text-[0.75rem]">
          {Object.entries(msh.subtipo).map(([k, v]) => (
            <span key={k} className="flex items-center gap-1.5">
              <span
                className="inline-block h-2.5 w-2.5 rounded-[2px]"
                style={{ background: COLOR[k] }}
              />
              <span className="text-(--ink-2)">{tx(ETIQ[k])}</span>
              <span className="tabular text-(--muted)">{num(v)}%</span>
            </span>
          ))}
        </div>
      </div>

      <h3 className="mb-4 text-[0.8rem] uppercase tracking-[0.1em] text-(--muted)">
        {tx({
          es: "Abundancia relativa por especie",
          en: "Relative abundance by species",
        })}
      </h3>

      <div className="space-y-[5px]">
        {esp.slice(0, n).map((e) => {
          const enSeep = compartidos.has((e.genero ?? "").toLowerCase());
          return (
            <div key={e.taxon} className="flex items-center gap-3 text-[0.82rem]">
              <span className="w-[15rem] shrink-0 truncate">
                <Taxon nombre={e.taxon} />
              </span>
              <span className="relative h-4 flex-1 rounded-[2px] bg-(--surface-2)">
                <span
                  className="absolute inset-y-0 left-0 rounded-[2px]"
                  style={{
                    width: (e.abundancia_rel / max) * 100 + "%",
                    background: COLOR[e.subtipo ?? "Aglutinado"] ?? "var(--muted)",
                    opacity: enSeep ? 1 : 0.42,
                  }}
                />
              </span>
              <span className="tabular w-12 shrink-0 text-right text-(--muted)">
                {num(e.abundancia_rel, 2)}%
              </span>
            </div>
          );
        })}
      </div>

      {n < esp.length && (
        <button
          type="button"
          onClick={() => setN(esp.length)}
          className="mt-4 text-[0.8rem] text-(--muted) underline underline-offset-2 hover:text-(--ink)"
        >
          {tx({ es: "Ver las 52 especies", en: "Show all 52 species" })}
        </button>
      )}

      <div className="mt-8 grid gap-6 border-t border-(--border) pt-6 sm:grid-cols-3">
        {[
          {
            v: msh.indices.riqueza_S,
            t: tx({ es: "especies (riqueza S)", en: "species (richness S)" }),
          },
          {
            v: num(msh.indices.equidad_J, 3),
            t: tx({ es: "equidad de Pielou J'", en: "Pielou evenness J'" }),
          },
          {
            v: num(msh.indices.dominancia_top5) + "%",
            t: tx({
              es: "abundancia en las 5 principales",
              en: "abundance in the top 5",
            }),
          },
        ].map((d) => (
          <div key={d.t}>
            <div className="tabular text-[1.7rem] font-semibold leading-none">
              {d.v}
            </div>
            <div className="mt-1.5 text-[0.78rem] text-(--muted)">{d.t}</div>
          </div>
        ))}
      </div>

      <ComoSeLee>
        {tx({
          es: "El color indica el tipo de pared. Las barras a plena opacidad son géneros que la literatura mundial ya reporta en filtraciones; las atenuadas son exclusivas de esta plataforma caribeña. Ese contraste es el resultado: la asociación no es ni puramente de filtración ni puramente de plataforma, sino las dos superpuestas. Una equidad de 0,87 indica que la abundancia está muy repartida, sin una especie que aplaste a las demás.",
          en: "Colour shows wall type. Full-opacity bars are genera the global literature already reports at seeps; dimmed ones are exclusive to this Caribbean shelf. That contrast is the finding: the assemblage is neither purely seep nor purely shelf, but both superimposed. An evenness of 0.87 means abundance is widely spread, with no species crushing the rest.",
        })}
      </ComoSeLee>

      <Nota>
        {tx({
          es:
            "Los conteos originales son fraccionarios porque proceden de submuestreo por alícuotas; el factor de reparto no está documentado en la hoja de origen. " +
            num(solape.generos.pct_abundancia_compartida) +
            "% de la abundancia corresponde a géneros ya reportados en filtraciones.",
          en:
            "Original counts are fractional because they come from aliquot splitting; the split factor is not documented in the source sheet. " +
            solape.generos.pct_abundancia_compartida.toFixed(1) +
            "% of abundance belongs to genera already reported at seeps.",
        })}
      </Nota>
    </figure>
  );
}
