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

  /**
   * Separa en abanico los estudios que caen unos sobre otros.
   *
   * Doce de los treinta y nueve comparten coordenada EXACTA —tres estudios en
   * Hydrate Ridge, tres en Vestnesa Ridge, dos en Monterey…— porque la posición
   * es la de la localidad, no la del testigo. Dibujados sin más, los de abajo
   * quedaban tapados y era imposible señalarlos con el cursor.
   *
   * Se reparten en un círculo alrededor de su posición real, que se marca con
   * un punto tenue y una línea a cada uno: así se ve que son un grupo y de
   * dónde vienen, en vez de fingir que están separados.
   */
  const colocados = useMemo(() => {
    const base = puntos
      .map((e) => ({ e, p: proyectar(e.lon as number, e.lat as number) }))
      .filter((d): d is { e: Est; p: [number, number] } => d.p !== null);

    const grupos: { miembros: typeof base; cx: number; cy: number }[] = [];
    for (const d of base) {
      const g = grupos.find(
        (g) => Math.hypot(g.cx - d.p[0], g.cy - d.p[1]) < 11,
      );
      if (g) g.miembros.push(d);
      else grupos.push({ miembros: [d], cx: d.p[0], cy: d.p[1] });
    }

    const salida = grupos.flatMap(({ miembros, cx, cy }) => {
      if (miembros.length === 1) {
        return [{ e: miembros[0].e, x: cx, y: cy, cx, cy, fan: false }];
      }
      const r = 8 + 2.2 * miembros.length;
      return miembros.map((m, i) => {
        // Se empieza arriba y se reparte en sentido horario: el orden depende
        // sólo del índice, así que el dibujo es estable entre renders.
        const a = (i / miembros.length) * 2 * Math.PI - Math.PI / 2;
        return {
          e: m.e,
          x: cx + r * Math.cos(a),
          y: cy + r * Math.sin(a),
          cx,
          cy,
          fan: true,
        };
      });
    });

    // Dos abanicos vecinos pueden acercar sus miembros entre sí —pasó con
    // Monterey y Hydrate Ridge, que quedaron a 5,4 px—. Unas pocas pasadas de
    // separación garantizan que ningún par baje del diámetro de un punto.
    const MIN = 10;
    for (let paso = 0; paso < 24; paso++) {
      let movido = false;
      for (let i = 0; i < salida.length; i++) {
        for (let j = i + 1; j < salida.length; j++) {
          const dx = salida[j].x - salida[i].x;
          const dy = salida[j].y - salida[i].y;
          const d = Math.hypot(dx, dy) || 0.01;
          if (d >= MIN) continue;
          const empuje = (MIN - d) / 2;
          const ux = (dx / d) * empuje;
          const uy = (dy / d) * empuje;
          salida[i].x -= ux;
          salida[i].y -= uy;
          salida[j].x += ux;
          salida[j].y += uy;
          salida[i].fan = salida[j].fan = true;
          movido = true;
        }
      }
      if (!movido) break;
    }
    return salida;
  }, [puntos, proyectar]);
  const sitio = matriz.sitio_tesis;
  const pSitio = proyectar(sitio.lon, sitio.lat);
  const tipos = [...new Set(estudios.map((e) => e.tipo_filtracion))];

  // La ficha sigue al punto DIBUJADO, que en un abanico no coincide con su
  // coordenada: si usara la original, aparecería descolgada del círculo.
  const dActivo = colocados.find((d) => d.e.id === activo?.id);
  const ptActivo: [number, number] | null = dActivo
    ? [dActivo.x, dActivo.y]
    : null;

  return (
    <figure className="m-0">
      {/* El contenedor es relativo para poder colgar la ficha SOBRE el punto.
          Antes la información salía debajo del mapa y el usuario no llegaba a
          enterarse de que el mapa respondía al cursor. */}
      <div className="relative overflow-x-auto">
        <div className="relative min-w-[560px]">
        <svg
          viewBox={"0 0 " + W + " " + H}
          className="block w-full"
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

          {/* Las guías del abanico van debajo de todos los puntos */}
          {colocados
            .filter((d) => d.fan)
            .map((d) => (
              <g key={"g" + d.e.id}>
                <line
                  x1={d.cx}
                  y1={d.cy}
                  x2={d.x}
                  y2={d.y}
                  stroke="var(--axis)"
                  strokeWidth={0.7}
                />
                <circle cx={d.cx} cy={d.cy} r={1.4} fill="var(--axis)" />
              </g>
            ))}

          {/* El punto activo se dibuja el último para que quede encima */}
          {[...colocados]
            .sort((a, b) =>
              a.e.id === activo?.id ? 1 : b.e.id === activo?.id ? -1 : 0,
            )
            .map(({ e, x, y }) => {
            const on = activo?.id === e.id;
            return (
              <circle
                key={e.id}
                cx={x}
                cy={y}
                r={on ? 7 : 4.5}
                fill={FLUIDO[e.tipo_filtracion]?.color ?? "var(--muted)"}
                stroke="var(--surface)"
                strokeWidth={1.5}
                className="cursor-pointer transition-all"
                tabIndex={0}
                role="button"
                aria-label={
                  (e.localidad ?? "") +
                  " — " +
                  (e.autores ?? ["?"])[0] +
                  " " +
                  (e.anio ?? "")
                }
                onMouseEnter={() => setActivo(e)}
                onMouseLeave={() => setActivo(null)}
                // El teclado abre la misma ficha: sin esto, la información
                // sólo existía para quien usa ratón.
                onFocus={() => setActivo(e)}
                onBlur={() => setActivo(null)}
              />
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

        {/* Ficha flotante anclada al punto. Va en HTML y no en SVG porque el
            texto tiene que fluir y ajustarse; se posiciona en porcentaje, que
            es lo que sobrevive al escalado del viewBox. */}
        {activo && ptActivo && (
          <div
            className="pointer-events-none absolute z-10 w-[19rem] max-w-[80vw] rounded-[6px] border border-(--border) bg-(--surface) px-3 py-2.5 shadow-lg"
            style={{
              left: (ptActivo[0] / W) * 100 + "%",
              top: (ptActivo[1] / H) * 100 + "%",
              // Cerca de un borde la ficha se ancla del lado contrario para
              // no salirse del mapa.
              transform:
                "translate(" +
                (ptActivo[0] < W * 0.22
                  ? "0"
                  : ptActivo[0] > W * 0.78
                    ? "-100%"
                    : "-50%") +
                ", " +
                (ptActivo[1] < H * 0.38 ? "1.4rem" : "calc(-100% - 1.1rem)") +
                ")",
            }}
          >
            <p className="mb-1 text-[0.9rem] font-semibold leading-snug">
              {activo.localidad}
            </p>
            <p className="mb-2 text-[0.78rem] leading-snug text-(--ink-2)">
              {(activo.autores ?? ["?"])[0]} {activo.anio ?? ""}
              {activo.revista ? " · " + activo.revista : ""}
            </p>
            <dl className="space-y-0.5 text-[0.76rem] leading-snug">
              {(
                [
                  [
                    tx({ es: "Fluido", en: "Fluid" }),
                    activo.tipo_filtracion
                      ? idioma === "es"
                        ? FLUIDO[activo.tipo_filtracion]?.es
                        : FLUIDO[activo.tipo_filtracion]?.en
                      : null,
                  ],
                  [
                    tx({ es: "Morfología", en: "Morphology" }),
                    activo.morfologia_label,
                  ],
                  [
                    tx({ es: "Profundidad", en: "Depth" }),
                    activo.prof_m ? activo.prof_m + " m" : null,
                  ],
                  [
                    tx({ es: "Registros", en: "Records" }),
                    activo.n_registros,
                  ],
                ] as const
              )
                .filter(([, v]) => v !== null && v !== undefined && v !== "")
                .map(([k, v]) => (
                  <div key={k} className="flex gap-2">
                    <dt className="w-[5.6rem] shrink-0 text-(--muted)">{k}</dt>
                    <dd className="m-0 tabular text-(--ink-2)">{v}</dd>
                  </div>
                ))}
            </dl>
          </div>
        )}
        </div>
      </div>

      {/* Sin este aviso la interacción no se descubre: el mapa parece
          estático hasta que alguien pasa por encima de un punto por azar. */}
      <p className="mt-3 text-[0.75rem] text-(--muted)">
        {tx({
          es: "Pasa el cursor —o tabula— por un punto para ver el estudio. Pulsa un color de la leyenda para filtrar.",
          en: "Hover — or tab — over a dot to see the study. Click a legend colour to filter.",
        })}
      </p>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-[0.75rem]">
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

      {/* La ficha aparece sobre el punto, pero un lector de pantalla no la
          «ve»: este bloque anuncia lo mismo sin ocupar espacio. */}
      <p className="sr-only" aria-live="polite">
        {activo
          ? activo.localidad +
            " — " +
            (activo.autores ?? ["?"])[0] +
            " " +
            (activo.anio ?? "")
          : ""}
      </p>

      <ComoSeLee>
        {tx({
          es: "Cada punto es un estudio, situado en la localidad de filtración que describe. Las coordenadas son la posición representativa de esa localidad, no la del testigo concreto: sirven para situar los trabajos, no para análisis espacial fino. Varias localidades reúnen más de un estudio —tres en Hydrate Ridge, tres en Vestnesa Ridge, dos en la bahía de Monterey—, y esos puntos se abren en abanico para poder señalarlos uno a uno: la línea fina los une a su posición real, marcada con un punto tenue. El color codifica el tipo de fluido; pulsa la leyenda para filtrar. El anillo marca la muestra de la tesis.",
          en: "Each dot is a study, placed at the seep locality it describes. Coordinates are the representative position of that locality, not of the individual core: they place the work, they are not for fine spatial analysis. Several localities hold more than one study — three at Hydrate Ridge, three at Vestnesa Ridge, two in Monterey Bay — and those dots are fanned out so each can be picked individually: the thin line ties them to their true position, marked by a faint dot. Colour encodes fluid type; click the legend to filter. The ring marks the thesis sample.",
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
