"use client";

import msh from "@datos/msh_bc21.json";
import sinu from "@datos/sinu_2024.json";
import solape from "@datos/solape.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota, Taxon } from "@/lib/ui";

type Estado = "cumple" | "matiza";

function Criterio({
  estado,
  titulo,
  esperado,
  observado,
  explicacion,
}: {
  estado: Estado;
  titulo: string;
  esperado: string;
  observado: string;
  explicacion: React.ReactNode;
}) {
  const color =
    estado === "cumple" ? "var(--pared-porcelanaceo)" : "var(--pared-monocristalino)";
  return (
    <div className="border-t border-(--border) py-5">
      <div className="mb-2 flex items-start gap-3">
        <span
          aria-hidden
          className="mt-[7px] inline-block h-2.5 w-2.5 shrink-0 rounded-full"
          style={{ background: color }}
        />
        <div className="flex-1">
          <h3 className="text-[1.05rem] font-semibold leading-snug">{titulo}</h3>
          <p className="mt-1 text-[0.8rem] text-(--muted)">
            <span className="sr-only">
              {estado === "cumple" ? "Cumple. " : "Con matiz. "}
            </span>
            {esperado}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <div className="tabular text-[1.35rem] font-semibold leading-none">
            {observado}
          </div>
        </div>
      </div>
      <div className="max-w-[62ch] pl-[22px] text-[0.88rem] leading-relaxed text-(--ink-2)">
        {explicacion}
      </div>
    </div>
  );
}

export default function Veredicto() {
  const { tx } = useT();
  const d = sinu.diversidad;
  const c = sinu.comparacion_msh;

  return (
    <figure className="m-0">
      <Criterio
        estado="cumple"
        titulo={tx({
          es: "Dominan las formas calcáreas",
          en: "Calcareous forms dominate",
        })}
        esperado={tx({
          es: "La literatura espera que los aglutinados se desplomen en filtraciones",
          en: "The literature expects agglutinated taxa to collapse at seeps",
        })}
        observado={msh.pared.Calcareo.toFixed(0) + "%"}
        explicacion={tx({
          es: "87% calcáreos frente a 13% aglutinados. Es un contraste más extremo que el 68/32 que Chiang et al. (2015) publican para filtraciones, y muy lejos del 24/76 de sus sitios de control.",
          en: "87% calcareous against 13% agglutinated. A sharper contrast than the 68/32 Chiang et al. (2015) publish for seeps, and far from the 24/76 of their control sites.",
        })}
      />

      <Criterio
        estado="cumple"
        titulo={tx({ es: "Abundancia alta", en: "High abundance" })}
        esperado={tx({
          es: "Las filtraciones sostienen densidades elevadas por la oferta de alimento bacteriano",
          en: "Seeps sustain high densities thanks to abundant bacterial food",
        })}
        observado="4015"
        explicacion={tx({
          es: "4015 y 3050 individuos por gramo en los dos centímetros analizados. Valores altos, coherentes con lo que la literatura describe para ambientes de filtración.",
          en: "4015 and 3050 individuals per gram in the two centimetres analysed. High values, consistent with what the literature describes for seep environments.",
        })}
      />

      <Criterio
        estado="cumple"
        titulo={tx({
          es: "Presencia de taxones indicadores",
          en: "Indicator taxa present",
        })}
        esperado={tx({
          es: "Uvigerina, Bolivina, Bulimina, Melonis, Chilostomella",
          en: "Uvigerina, Bolivina, Bulimina, Melonis, Chilostomella",
        })}
        observado={solape.generos.n_compartidos + "/" + solape.generos.n_msh}
        explicacion={
          <>
            {tx({
              es: "Comparte 19 de sus 41 géneros con la literatura mundial de filtraciones, y ese solape concentra el 55% de la abundancia de la muestra. Entre ellos ",
              en: "It shares 19 of its 41 genera with the global seep literature, and that overlap holds 55% of the sample abundance. Among them ",
            })}
            <Taxon nombre="Uvigerina" />, <Taxon nombre="Cibicidoides mundulus" />
            {tx({ es: " y ", en: " and " })}
            <Taxon nombre="Lobatula wuellerstorfi" />
            {tx({
              es: ", el segundo taxón más reportado del mundo en filtraciones.",
              en: ", the second most reported taxon worldwide at seeps.",
            })}
          </>
        }
      />

      <Criterio
        estado="matiza"
        titulo={tx({
          es: "Diversidad: la excepción que resultó no serlo",
          en: "Diversity: the exception that turned out not to be one",
        })}
        esperado={tx({
          es: "La literatura predice diversidad BAJA en filtraciones",
          en: "The literature predicts LOW diversity at seeps",
        })}
        observado={"H' " + msh.indices.shannon_H.toFixed(2)}
        explicacion={
          <>
            {tx({
              es: "La tesis obtuvo un Shannon de 3,43 y lo trató como una anomalía, atribuyéndola a la ubicación tropical. Dos años después, Barragán y Bernal midieron el mismo campo de filtración —el mismo proyecto y el mismo sitio— y encontraron ",
              en: "The thesis obtained a Shannon of 3.43 and treated it as an anomaly, attributing it to the tropical setting. Two years later, Barragán and Bernal measured the same seep field — same project, same site — and found ",
            })}
            <strong className="font-semibold text-(--ink)">
              {tx({ es: "Shannon entre ", en: "Shannon between " })}
              {d.shannon_min.toFixed(1)}
              {tx({ es: " y ", en: " and " })}
              {d.shannon_max.toFixed(1)}
              {tx({
                es: " en las 18 estaciones",
                en: " across all 18 stations",
              })}
            </strong>
            {tx({
              es: ", incluidas las de actividad alta. En esta plataforma tropical la diversidad alta es lo normal Y es compatible con filtración activa. El valor de la tesis deja de ser anómalo: cae justo en medio del rango.",
              en: ", including the high-activity ones. On this tropical shelf high diversity is normal AND compatible with active seepage. The thesis value stops being anomalous: it sits right in the middle of the range.",
            })}
          </>
        }
      />

      <div className="mt-8 rounded-[6px] border border-(--border) bg-(--surface) p-5">
        <div className="mb-3 flex flex-wrap items-baseline gap-x-3">
          <span className="text-[0.72rem] uppercase tracking-[0.14em] text-(--muted)">
            {tx({ es: "Escala de diversidad", en: "Diversity scale" })}
          </span>
          <span className="text-[0.78rem] text-(--ink-2)">
            {tx({
              es: "campo de filtración del Sinú, 18 estaciones",
              en: "Sinú seep field, 18 stations",
            })}
          </span>
        </div>
        <div className="relative h-11">
          <div className="absolute top-4 h-1.5 w-full rounded-full bg-(--surface-2)" />
          <div
            className="absolute top-4 h-1.5 rounded-full"
            style={{
              left: (((d.shannon_min - 2) / 2) * 100).toFixed(1) + "%",
              width: (((d.shannon_max - d.shannon_min) / 2) * 100).toFixed(1) + "%",
              background: "var(--pared-hialino)",
              opacity: 0.35,
            }}
          />
          <div
            className="absolute top-1 h-8 w-[2px]"
            style={{
              left: (((msh.indices.shannon_H - 2) / 2) * 100).toFixed(1) + "%",
              background: "var(--sitio)",
            }}
          />
          <div
            className="absolute top-10 -translate-x-1/2 whitespace-nowrap text-[0.72rem] font-semibold"
            style={{ left: (((msh.indices.shannon_H - 2) / 2) * 100).toFixed(1) + "%" }}
          >
            MSH-BC-21 · {msh.indices.shannon_H.toFixed(2)}
          </div>
          <span className="absolute top-7 left-0 text-[0.68rem] tabular text-(--muted)">
            2,0
          </span>
          <span className="absolute top-7 right-0 text-[0.68rem] tabular text-(--muted)">
            4,0
          </span>
        </div>
        <p className="mt-7 text-[0.8rem] leading-relaxed text-(--ink-2)">
          {c.dentro_del_rango
            ? tx({
                es: "La banda azul es el rango medido en el campo de filtración. La línea es la muestra de la tesis: cae dentro.",
                en: "The blue band is the range measured across the seep field. The line is the thesis sample: it falls inside.",
              })
            : ""}
        </p>
      </div>

      <ComoSeLee>
        {tx({
          es: "Cada criterio contrasta lo que la literatura predice para una filtración con lo que la muestra realmente mide. El cuarto criterio es el interesante: durante dos años pareció una contradicción, y sólo dejó de serlo cuando apareció una línea base medida en el mismo sitio. Sin ella, comparar una plataforma tropical somera con filtraciones profundas de latitudes altas era comparar cosas distintas.",
          en: "Each criterion contrasts what the literature predicts for a seep with what the sample actually measures. The fourth is the interesting one: for two years it looked like a contradiction, and stopped being one only when a baseline measured at the same site appeared. Without it, comparing a shallow tropical shelf against deep high-latitude seeps was comparing different things.",
        })}
      </ComoSeLee>

      <Nota>
        {tx({
          es: "Rango de diversidad y valores de δ13C: Barragán-Jacksson y Bernal (2024), Journal of South American Earth Sciences. Mismo proyecto MSH y misma localidad que la tesis. Proporciones de pared de control: Chiang et al. (2015).",
          en: "Diversity range and δ13C values: Barragán-Jacksson and Bernal (2024), Journal of South American Earth Sciences. Same MSH project and same locality as the thesis. Control wall proportions: Chiang et al. (2015).",
        })}
      </Nota>
    </figure>
  );
}
