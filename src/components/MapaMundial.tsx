"use client";

import { useMemo, useState } from "react";
import { geoNaturalEarth1, geoPath, geoGraticule10 } from "d3-geo";
import { feature } from "topojson-client";
import type { FeatureCollection } from "geojson";
import land from "world-atlas/land-110m.json";
import estudios from "@datos/estudios.json";
import matriz from "@datos/matriz_lat_prof.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota } from "@/lib/ui";

const W = 900;
const H = 460;

type Est = (typeof estudios)[number];

const FLUIDO: Record<string, { es: string; en: string; color: string }> = {
  frio: { es: "Filtración fría", en: "Cold seep", color: "var(--pared-hialino)" },
  termogenico: {
    es: "Termogénico",
    en: "Thermogenic",
    color: "var(--pared-aglutinado)",
  },
  biogenico: {
    es: "Biogénico",
    en: "Biogenic",
    color: "var(--pared-porcelanaceo)",
  },
  hidrotermal: {
    es: "Hidrotermal",
    en: "Hydrothermal",
    color: "var(--pared-monocristalino)",
  },
  mixto: { es: "Mixto", en: "Mixed", color: "var(--muted)" },
  no_filtracion: { es: "No es filtración", en: "Not a seep", color: "var(--axis)" },
};

export default function MapaMundial() {
  const { tx, idioma } = useT();
  const [activo, setActivo] = useState<Est | null>(null);
  const [filtro, setFiltro] = useState<string | null>(null);

  const { tierra, retic, proyectar } = useMemo(() => {
    const proj = geoNaturalEarth1().fitExtent(
      [
        [8, 8],
        [W - 8, H - 8],
      ],
      { type: "Sphere" },
    );
    const p = geoPath(proj);
    const objetos = (land as unknown as { objects: { land: unknown } }).objects;
    const fc = feature(
      land as never,
      objetos.land as never,
    ) as unknown as FeatureCollection;
    return {
      tierra: p(fc) ?? "",
      retic: p(geoGraticule10()) ?? "",
      proyectar: (lon: number, lat: number) => proj([lon, lat]),
    };
  }, []);

  const puntos = estudios.filter(
    (e) => e.lat !== null && (!filtro || e.tipo_filtracion === filtro),
  );
  const sitio = matriz.sitio_tesis;
  const pSitio = proyectar(sitio.lon, sitio.lat);
  const tipos = [...new Set(estudios.map((e) => e.tipo_filtracion))];

  return (
    <figure className="m-0">
      <div className="overflow-x-auto">
        <svg
          viewBox={"0 0 " + W + " " + H}
          className="w-full min-w-[560px]"
          role="img"
          aria-label={tx({
            es:
              puntos.length +
              " estudios de foraminíferos en filtraciones de metano situados en un mapa mundial, con la posición de la muestra del Caribe colombiano",
            en:
              puntos.length +
              " foraminifera methane-seep studies on a world map, with the position of the Colombian Caribbean sample",
          })}
        >
          <path d={retic} fill="none" stroke="var(--grid)" strokeWidth={0.5} />
          <path
            d={tierra}
            fill="var(--surface-2)"
            stroke="var(--axis)"
            strokeWidth={0.5}
          />

          {puntos.map((e) => {
            const pt = proyectar(e.lon as number, e.lat as number);
            if (!pt) return null;
            const on = activo?.id === e.id;
            return (
              <circle
                key={e.id}
                cx={pt[0]}
                cy={pt[1]}
                r={on ? 7 : 4.5}
                fill={FLUIDO[e.tipo_filtracion]?.color ?? "var(--muted)"}
                stroke="var(--surface)"
                strokeWidth={1.5}
                className="cursor-pointer transition-all"
                onMouseEnter={() => setActivo(e)}
                onMouseLeave={() => setActivo(null)}
              >
                <title>{e.localidad ?? ""}</title>
              </circle>
            );
          })}

          {pSitio && (
            <g>
              <circle
                cx={pSitio[0]}
                cy={pSitio[1]}
                r={11}
                fill="none"
                stroke="var(--sitio)"
                strokeWidth={2}
              />
              <circle cx={pSitio[0]} cy={pSitio[1]} r={3} fill="var(--sitio)" />
              <text
                x={pSitio[0] - 16}
                y={pSitio[1] + 26}
                textAnchor="end"
                className="fill-(--ink) text-[11px] font-semibold"
              >
                MSH-BC-21
              </text>
            </g>
          )}
        </svg>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-[0.75rem]">
        {tipos.map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => setFiltro(filtro === k ? null : k)}
            aria-pressed={filtro === k}
            className={
              "flex items-center gap-1.5 rounded-[4px] px-1.5 py-0.5 hover:bg-(--surface-2) " +
              (filtro && filtro !== k ? "opacity-40" : "")
            }
          >
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ background: FLUIDO[k]?.color }}
            />
            <span className="text-(--ink-2)">
              {idioma === "es" ? FLUIDO[k]?.es : FLUIDO[k]?.en}
            </span>
            <span className="tabular text-(--muted)">
              {estudios.filter((e) => e.tipo_filtracion === k).length}
            </span>
          </button>
        ))}
      </div>

      <div className="mt-3 min-h-[3.2rem] text-[0.85rem]" aria-live="polite">
        {activo && (
          <div className="inline-block max-w-[62ch] rounded-[5px] border border-(--border) bg-(--surface) px-3 py-2">
            <strong className="font-semibold">{activo.localidad}</strong>
            <span className="text-(--ink-2)">
              {" — "}
              {(activo.autores ?? ["?"])[0]} {activo.anio ?? ""} ·{" "}
              {activo.n_registros} {tx({ es: "registros", en: "records" })}
              {activo.prof_m ? " · " + activo.prof_m + " m" : ""}
              {activo.morfologia_label ? " · " + activo.morfologia_label : ""}
            </span>
          </div>
        )}
      </div>

      <ComoSeLee>
        {tx({
          es: "Cada punto es un estudio, situado en la localidad de filtración que describe. Las coordenadas son la posición representativa de esa localidad, no la del testigo concreto: sirven para situar los trabajos, no para análisis espacial fino. El color codifica el tipo de fluido; pulsa la leyenda para filtrar. El anillo marca la muestra de la tesis.",
          en: "Each dot is a study, placed at the seep locality it describes. Coordinates are the representative position of that locality, not of the individual core: they place the work, they are not for fine spatial analysis. Colour encodes fluid type; click the legend to filter. The ring marks the thesis sample.",
        })}
      </ComoSeLee>

      <Nota>
        {tx({
          es:
            estudios.filter((e) => e.lat !== null).length +
            " de " +
            estudios.length +
            " estudios georreferenciados. El restante es multi-sitio y además no documenta filtraciones.",
          en:
            estudios.filter((e) => e.lat !== null).length +
            " of " +
            estudios.length +
            " studies georeferenced. The remaining one is multi-site and does not document seepage.",
        })}
      </Nota>
    </figure>
  );
}
