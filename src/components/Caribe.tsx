"use client";

import caribe from "@datos/caribe_referencia.json";
import msh from "@datos/msh_bc21.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota, Taxon, useNum } from "@/lib/ui";

const AMBIENTE: Record<string, { es: string; en: string }> = {
  Estuarino: { es: "Estuarino", en: "Estuarine" },
  Manglar: { es: "Manglar", en: "Mangrove" },
  Arrecifal: { es: "Arrecifal", en: "Reef" },
  "Arrecifal / plataforma": { es: "Arrecifal / plataforma", en: "Reef / shelf" },
  "Plataforma / presunto seep": {
    es: "Plataforma / presunta filtración",
    en: "Shelf / putative seep",
  },
};

export default function Caribe() {
  const { tx } = useT();
  const num = useNum();

  // Ordenadas por dominancia del taxón principal: así el contraste con
  // MSH-BC-21 —que cierra la lista— se lee de un vistazo.
  const sitios = [...caribe]
    .map((s) => ({
      ...s,
      taxones: [...s.taxones].sort((a, b) => b.abundancia_rel - a.abundancia_rel),
    }))
    .sort((a, b) => b.taxones[0].abundancia_rel - a.taxones[0].abundancia_rel);

  const esMsh = (id: string) => id === "msh_bc21";
  const mshTop = sitios.find((s) => esMsh(s.id))!.taxones[0];
  const otros = sitios.filter((s) => !esMsh(s.id));
  const minOtros = Math.min(...otros.map((s) => s.taxones[0].abundancia_rel));
  const maxOtros = Math.max(...otros.map((s) => s.taxones[0].abundancia_rel));

  return (
    <figure className="m-0">
      <div className="mb-8 grid gap-6 sm:grid-cols-3">
        {[
          {
            v: num(maxOtros) + "%",
            t: tx({
              es: "domina la especie principal en los manglares de Urabá",
              en: "share of the top species in the Urabá mangroves",
            }),
          },
          {
            v: num(minOtros) + "%",
            t: tx({
              es: "la menos desigual de las localidades caribeñas",
              en: "the least uneven of the Caribbean localities",
            }),
          },
          {
            v: num(mshTop.abundancia_rel) + "%",
            t: tx({
              es: "domina la principal en MSH-BC-21",
              en: "share of the top species in MSH-BC-21",
            }),
            destacar: true,
          },
        ].map((d) => (
          <div key={d.t}>
            <div
              className="tabular text-[2rem] font-semibold leading-none"
              style={d.destacar ? { color: "var(--pared-hialino)" } : undefined}
            >
              {d.v}
            </div>
            <div className="mt-1.5 max-w-[24ch] text-[0.8rem] leading-snug text-(--muted)">
              {d.t}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-6">
        {sitios.map((s) => {
          const top = s.taxones[0].abundancia_rel;
          return (
            <div
              key={s.id}
              className={
                "rounded-[6px] border p-4 " +
                (esMsh(s.id)
                  ? "border-(--sitio) bg-(--surface-2)"
                  : "border-(--border)")
              }
            >
              <div className="mb-3 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                <h3 className="text-[0.92rem] font-semibold">{s.nombre}</h3>
                <span className="text-[0.74rem] text-(--muted)">
                  {tx(AMBIENTE[s.ambiente] ?? { es: s.ambiente, en: s.ambiente })}
                  {" · "}
                  <span className="text-(--ink-2)">{s.fuente}</span>
                  {s.cita_en_tesis && !esMsh(s.id) && (
                    <span className="ml-1 opacity-80">
                      ({tx({ es: "citado en la tesis, ", en: "cited in the thesis, " })}
                      {s.cita_en_tesis})
                    </span>
                  )}
                </span>
              </div>

              <div className="space-y-1.5">
                {s.taxones.slice(0, 6).map((t) => (
                  <div key={t.taxon} className="flex items-center gap-3">
                    <span className="w-[13.5rem] shrink-0 truncate text-[0.8rem]">
                      <Taxon nombre={t.taxon} />
                    </span>
                    <span className="h-3 flex-1 rounded-[2px] bg-(--sin-datos)">
                      {/* La escala es la MISMA en todas las localidades —0 a
                          100 %— porque el punto es comparar cuánto manda la
                          especie principal, no el reparto interno de cada una. */}
                      <span
                        className="block h-3 rounded-[2px]"
                        style={{
                          width: t.abundancia_rel + "%",
                          background: esMsh(s.id)
                            ? "var(--pared-hialino)"
                            : "var(--seq-400)",
                        }}
                      />
                    </span>
                    <span className="tabular w-[3.4rem] shrink-0 text-right text-[0.78rem] text-(--ink-2)">
                      {num(t.abundancia_rel)}%
                    </span>
                  </div>
                ))}
              </div>

              <p className="mt-2.5 text-[0.72rem] leading-snug text-(--muted)">
                {tx({
                  es: "La principal ocupa el " + num(top) + "%. ",
                  en: "The top species takes " + num(top) + "%. ",
                })}
                {s.nota}
              </p>
            </div>
          );
        })}
      </div>

      <ComoSeLee>
        {tx({
          es: "Cada bloque es una localidad del Caribe colombiano con las abundancias relativas que la tesis cita de trabajos del grupo OCEÁNICOS, y el último es la muestra de este trabajo. Las barras comparten escala de 0 a 100 %, de modo que lo que se compara es cuánto ocupa la especie principal en cada sitio, no el reparto interno. Ninguna de las cinco primeras es un ambiente de filtración: son la fauna de fondo regional, el término de comparación.",
          en: "Each block is a Colombian Caribbean locality with the relative abundances the thesis cites from OCEÁNICOS group work, and the last one is this study's sample. Bars share a 0-100% scale, so what is compared is how much the leading species takes at each site, not the internal split. None of the first five is a seep environment: they are the regional background fauna, the term of comparison.",
        })}
      </ComoSeLee>

      <Nota>
        <span className="text-(--ink-2)">
          {tx({ es: "Fuentes de las cifras caribeñas: ", en: "Sources of the Caribbean figures: " })}
        </span>
        {otros.map((s, i) => (
          <span key={s.id}>
            {i > 0 && "; "}
            <span className="text-(--ink-2)">{s.fuente}</span>
            {tx({ es: " para ", en: " for " })}
            {s.nombre}
            {s.cita_en_tesis && " (" + s.cita_en_tesis + ")"}
          </span>
        ))}
        {tx({
          es: ". Son trabajos del grupo OCEÁNICOS que la tesis cita en su capítulo 4.2; aquí se estructuran por primera vez para poder compararlos, pero las cifras son de esos autores y hay que citarlos a ellos. ",
          en: ". These are OCEÁNICOS group works that the thesis cites in its chapter 4.2; they are structured here for the first time so they can be compared, but the figures belong to those authors and it is they who should be cited. ",
        })}
        {tx({
          es: `Advertencia metodológica: estas cifras proceden de fuentes secundarias —la tesis citando a terceros— con métodos de muestreo, fracciones de tamaño y ambientes distintos entre sí y distintos de MSH-BC-21. La comparación es indicativa, no cuantitativamente estricta. Por esa misma razón estas localidades NO forman parte de la base principal: no son filtraciones, y sumarlas llenaría con fauna de manglar y arrecife justamente la celda tropical somera que el trabajo señala como vacía. MSH-BC-21: ${msh.indices.riqueza_S} especies, J′ = ${num(msh.indices.equidad_J, 4)}.`,
          en: `Methodological caveat: these figures come from secondary sources — the thesis citing third parties — with sampling methods, size fractions and environments that differ from one another and from MSH-BC-21. The comparison is indicative, not quantitatively strict. For that same reason these localities are NOT part of the main database: they are not seeps, and adding them would fill with mangrove and reef fauna precisely the shallow tropical cell this work reports as empty. MSH-BC-21: ${msh.indices.riqueza_S} species, J′ = ${num(msh.indices.equidad_J, 4)}.`,
        })}
      </Nota>
    </figure>
  );
}
