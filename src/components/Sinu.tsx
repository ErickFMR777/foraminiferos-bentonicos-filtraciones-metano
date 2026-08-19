"use client";

import sinu from "@datos/sinu_2024.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota, Taxon, useNum } from "@/lib/ui";

const ZONA: Record<string, { es: string; en: string; color: string }> = {
  baja: { es: "Actividad baja", en: "Low activity", color: "var(--seq-250)" },
  moderada: { es: "Moderada", en: "Moderate", color: "var(--seq-400)" },
  "moderada-alta": {
    es: "Moderada-alta",
    en: "Moderate-high",
    color: "var(--seq-550)",
  },
};

export default function Sinu() {
  const { tx } = useT();
  const num = useNum();
  const compartidos = new Set(sinu.taxones_compartidos_con_msh);
  const zonas = ["baja", "moderada", "moderada-alta"];

  return (
    <figure className="m-0">
      <div className="mb-8 grid gap-6 sm:grid-cols-3">
        {[
          {
            v: sinu.diversidad.n_estaciones,
            t: tx({ es: "estaciones muestreadas", en: "stations sampled" }),
            n: tx({ es: "la tesis analizó una", en: "the thesis analysed one" }),
          },
          {
            v: sinu.n_taxones,
            t: tx({ es: "taxones reportados", en: "taxa reported" }),
            n: tx({
              es: sinu.taxones_compartidos_con_msh.length + " compartidos con MSH-BC-21",
              en: sinu.taxones_compartidos_con_msh.length + " shared with MSH-BC-21",
            }),
          },
          {
            v: "40–300",
            t: tx({ es: "metros de profundidad", en: "metres depth" }),
            n: tx({ es: "MSH-BC-21 está a ~75 m", en: "MSH-BC-21 sits at ~75 m" }),
          },
        ].map((d) => (
          <div key={d.t}>
            <div className="tabular text-[1.9rem] font-semibold leading-none">{d.v}</div>
            <div className="mt-1.5 text-[0.8rem] text-(--muted)">{d.t}</div>
            <div className="mt-0.5 text-[0.72rem] text-(--muted) opacity-80">{d.n}</div>
          </div>
        ))}
      </div>

      <h3 className="mb-4 text-[0.8rem] uppercase tracking-[0.1em] text-(--muted)">
        {tx({
          es: "Asociaciones por nivel de actividad de filtración",
          en: "Assemblages by seepage activity level",
        })}
      </h3>

      <div className="grid gap-5 md:grid-cols-3">
        {zonas.map((z) => {
          const taxa = sinu.taxones.filter((t) => t.zona_actividad === z);
          return (
            <div key={z} className="rounded-[6px] border border-(--border) p-4">
              <div className="mb-3 flex items-center gap-2">
                <span
                  className="inline-block h-2.5 w-2.5 rounded-full"
                  style={{ background: ZONA[z].color }}
                />
                <span className="text-[0.82rem] font-semibold">{tx(ZONA[z])}</span>
              </div>
              <ul className="space-y-1.5">
                {taxa.map((t) => (
                  <li key={t.taxon} className="text-[0.82rem] leading-snug">
                    <Taxon nombre={t.taxon} />
                    {compartidos.has(t.taxon) && (
                      <span
                        className="ml-1.5 inline-block h-1.5 w-1.5 rounded-full align-middle"
                        style={{ background: "var(--sitio)" }}
                        title="también en MSH-BC-21"
                      />
                    )}
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>

      <p className="mt-4 flex items-center gap-2 text-[0.75rem] text-(--muted)">
        <span
          className="inline-block h-1.5 w-1.5 rounded-full"
          style={{ background: "var(--sitio)" }}
        />
        {tx({
          es: "también presente en MSH-BC-21",
          en: "also present in MSH-BC-21",
        })}
      </p>

      <div className="mt-8 border-t border-(--border) pt-6">
        <h3 className="mb-3 text-[0.8rem] uppercase tracking-[0.1em] text-(--muted)">
          {tx({
            es: "Los primeros isótopos del área",
            en: "The first isotopes for the area",
          })}
        </h3>
        <p className="mb-4 max-w-[62ch] text-[0.9rem] leading-relaxed text-(--ink-2)">
          {tx({
            es: "La tesis no midió δ13C, que es la evidencia geoquímica directa de carbono derivado del metano. Estos son los primeros valores publicados para el Caribe colombiano, y proceden del mismo campo de filtración.",
            en: "The thesis did not measure δ13C, the direct geochemical evidence of methane-derived carbon. These are the first values published for the Colombian Caribbean, and they come from the same seep field.",
          })}
        </p>
        <div className="space-y-2.5">
          {sinu.isotopos.map((i) => (
            <div key={i.taxon} className="flex flex-wrap items-baseline gap-x-3 text-[0.85rem]">
              <span className="w-[13rem] shrink-0">
                <Taxon nombre={i.taxon} />
              </span>
              <span className="tabular text-(--ink-2)">
                {num(i.d13c_min, 2)} a{" "}
                {num(i.d13c_max, 2)} ‰ PDB
              </span>
              {i.nota && (
                <span className="text-[0.75rem] text-(--muted)">{i.nota}</span>
              )}
            </div>
          ))}
        </div>
      </div>

      <ComoSeLee>
        {tx({
          es: "Cada columna reúne los taxones que el artículo asocia a un nivel de actividad de filtración: baja, moderada y moderada-alta. La intensidad del color acompaña esa gradación y no codifica ninguna magnitud medida. El punto junto a un nombre indica que ese taxón también aparece en MSH-BC-21. Abajo, los rangos de δ13C son los valores mínimo y máximo publicados para cada especie, en por mil frente al estándar PDB: cuanto más negativos, mayor la impronta de carbono derivado del metano.",
          en: "Each column groups the taxa the article associates with one level of seepage activity: low, moderate and moderate-high. Colour intensity follows that gradation and encodes no measured magnitude. The dot beside a name marks a taxon that also occurs in MSH-BC-21. Below, the δ13C ranges are the minimum and maximum values published for each species, in per mil against the PDB standard: the more negative, the stronger the imprint of methane-derived carbon.",
        })}
      </ComoSeLee>

      <Nota>
        {tx({
          es: "Barragán-Jacksson, C.M. y Bernal, G.R. (2024). Journal of South American Earth Sciences 148, 105103. Los 27 taxones se extrajeron del texto del artículo y se validaron contra WoRMS; el artículo no publica abundancias por especie, así que aquí se registra presencia.",
          en: "Barragán-Jacksson, C.M. and Bernal, G.R. (2024). Journal of South American Earth Sciences 148, 105103. The 27 taxa were extracted from the article text and validated against WoRMS; the article does not publish per-species abundances, so presence is recorded here.",
        })}
      </Nota>
    </figure>
  );
}
