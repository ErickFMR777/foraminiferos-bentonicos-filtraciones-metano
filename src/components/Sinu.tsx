"use client";

import sinu from "@datos/sinu_2024.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota, Taxon } from "@/lib/ui";

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
                {i.d13c_min.toFixed(2).replace(".", ",")} a{" "}
                {i.d13c_max.toFixed(2).replace(".", ",")} ‰ PDB
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
          es: "Este trabajo es la continuación directa de la tesis: mismo proyecto MSH, misma directora y el mismo campo de filtración frente al Golfo de Morrosquillo. Donde la tesis analizó un testigo, aquí hay 18 estaciones; y aporta los isótopos que a la tesis le faltaban. Las asociaciones son las que el propio artículo declara para cada nivel de actividad.",
          en: "This work is the direct continuation of the thesis: same MSH project, same advisor and the same seep field off the Gulf of Morrosquillo. Where the thesis analysed one core, here there are 18 stations; and it supplies the isotopes the thesis lacked. The assemblages are those the article itself states for each activity level.",
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
