"use client";

import { useCallback, useMemo, useRef, useState } from "react";
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
const MARGEN = 8;
/** Dos puntos más cerca que esto EN PANTALLA se muestran como un grupo. Al
 *  acercar el zoom la distancia en pantalla crece y el grupo se abre solo. */
const JUNTOS = 24;
const K_MIN = 1;
const K_MAX = 12;

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

type Vista = { k: number; x: number; y: number };

/** Impide que el mapa se arrastre fuera de su marco y deje el lienzo vacío. */
function encajar(v: Vista): Vista {
  const k = Math.min(K_MAX, Math.max(K_MIN, v.k));
  return {
    k,
    x: Math.min(0, Math.max(W - W * k, v.x)),
    y: Math.min(0, Math.max(H - H * k, v.y)),
  };
}

export default function MapaMundial() {
  const { tx, idioma } = useT();
  const [activo, setActivo] = useState<Est | null>(null);
  const [filtro, setFiltro] = useState<string | null>(null);
  const [vista, setVista] = useState<Vista>({ k: 1, x: 0, y: 0 });
  // Tres estudios en la MISMA coordenada no se separan por mucho que se
  // acerque el zoom: su posición real es idéntica. Para ésos, el grupo se
  // despliega en una lista.
  const [grupoSel, setGrupoSel] = useState<Est[] | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const arrastre = useRef<{ x: number; y: number; vx: number; vy: number } | null>(
    null,
  );

  const { tierra, retic, proyectar } = useMemo(() => {
    const proj = geoNaturalEarth1().fitExtent(
      [
        [MARGEN, MARGEN],
        [W - MARGEN, H - MARGEN],
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

  const puntos = useMemo(
    () =>
      estudios
        .filter((e) => e.lat !== null && (!filtro || e.tipo_filtracion === filtro))
        .map((e) => ({ e, p: proyectar(e.lon as number, e.lat as number) }))
        .filter((d): d is { e: Est; p: [number, number] } => d.p !== null),
    [filtro, proyectar],
  );

  /** Coordenada del mapa -> coordenada en pantalla, con el zoom aplicado. */
  const aPantalla = useCallback(
    (p: [number, number]): [number, number] => [
      p[0] * vista.k + vista.x,
      p[1] * vista.k + vista.y,
    ],
    [vista],
  );

  /**
   * Agrupa lo que se solapa EN PANTALLA, no en el mapa.
   *
   * Doce de los treinta y nueve estudios comparten coordenada exacta —tres en
   * Hydrate Ridge, tres en Vestnesa Ridge…— porque la posición es la de la
   * localidad y no la del testigo. Antes se dibujaban unos encima de otros y
   * los de abajo eran inalcanzables. Ahora salen como un grupo con su número, y
   * como el criterio es la distancia en pantalla, acercar el zoom los separa
   * solo, cada uno en su sitio real. Ningún punto se desplaza nunca.
   */
  const grupos = useMemo(() => {
    const out: { xs: number; ys: number; miembros: Est[] }[] = [];
    for (const { e, p } of puntos) {
      const [xs, ys] = aPantalla(p);
      const g = out.find((g) => Math.hypot(g.xs - xs, g.ys - ys) < JUNTOS);
      if (g) g.miembros.push(e);
      else out.push({ xs, ys, miembros: [e] });
    }
    return out;
  }, [puntos, aPantalla]);

  const sitio = matriz.sitio_tesis;
  const pSitio = proyectar(sitio.lon, sitio.lat);
  const sSitio = pSitio ? aPantalla(pSitio) : null;
  const tipos = [...new Set(estudios.map((e) => e.tipo_filtracion))];

  const activoPos = useMemo(() => {
    const d = puntos.find((d) => d.e.id === activo?.id);
    return d ? aPantalla(d.p) : null;
  }, [activo, puntos, aPantalla]);

  // --- zoom y arrastre ---------------------------------------------------
  const zoomA = (k2: number, cx = W / 2, cy = H / 2) =>
    setVista((v) => {
      const k = Math.min(K_MAX, Math.max(K_MIN, k2));
      // el punto bajo el cursor se queda donde está
      return encajar({
        k,
        x: cx - ((cx - v.x) / v.k) * k,
        y: cy - ((cy - v.y) / v.k) * k,
      });
    });

  const enRueda = (ev: React.WheelEvent<SVGSVGElement>) => {
    const r = svgRef.current?.getBoundingClientRect();
    if (!r) return;
    const cx = ((ev.clientX - r.left) / r.width) * W;
    const cy = ((ev.clientY - r.top) / r.height) * H;
    zoomA(vista.k * (ev.deltaY < 0 ? 1.25 : 0.8), cx, cy);
  };

  const enBajar = (ev: React.PointerEvent<SVGSVGElement>) => {
    arrastre.current = { x: ev.clientX, y: ev.clientY, vx: vista.x, vy: vista.y };
    (ev.target as Element).setPointerCapture?.(ev.pointerId);
  };
  const enMover = (ev: React.PointerEvent<SVGSVGElement>) => {
    const a = arrastre.current;
    const r = svgRef.current?.getBoundingClientRect();
    if (!a || !r) return;
    const esc = W / r.width;
    setVista((v) =>
      encajar({
        ...v,
        x: a.vx + (ev.clientX - a.x) * esc,
        y: a.vy + (ev.clientY - a.y) * esc,
      }),
    );
  };
  const enSoltar = () => {
    arrastre.current = null;
  };

  const btn =
    "rounded-[4px] border border-(--border) px-2 py-0.5 text-[0.78rem] " +
    "text-(--ink-2) hover:bg-(--surface-2)";

  return (
    <figure className="m-0">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <button type="button" className={btn} onClick={() => zoomA(vista.k * 1.6)}>
          + {tx({ es: "Acercar", en: "Zoom in" })}
        </button>
        <button type="button" className={btn} onClick={() => zoomA(vista.k / 1.6)}>
          − {tx({ es: "Alejar", en: "Zoom out" })}
        </button>
        <button
          type="button"
          className={btn}
          onClick={() => setVista({ k: 1, x: 0, y: 0 })}
        >
          {tx({ es: "Ver todo", en: "Reset" })}
        </button>
        <span className="tabular text-[0.72rem] text-(--muted)">
          ×{vista.k.toFixed(1).replace(".", idioma === "es" ? "," : ".")}
        </span>
      </div>

      <div className="relative overflow-hidden rounded-[6px] border border-(--border)">
        <svg
          ref={svgRef}
          viewBox={"0 0 " + W + " " + H}
          className="block w-full touch-none select-none"
          style={{ cursor: arrastre.current ? "grabbing" : "grab" }}
          onWheel={enRueda}
          onPointerDown={enBajar}
          onPointerMove={enMover}
          onPointerUp={enSoltar}
          onPointerLeave={enSoltar}
          role="img"
          aria-label={tx({
            es:
              puntos.length +
              " estudios de foraminíferos en filtraciones de metano situados en un mapa mundial con zoom, con la posición de la muestra del Caribe colombiano",
            en:
              puntos.length +
              " foraminifera methane-seep studies on a zoomable world map, with the position of the Colombian Caribbean sample",
          })}
        >
          {/* Todo se recorta al marco: nada puede dibujarse fuera del mapa. */}
          <defs>
            <clipPath id="marco-mapa">
              <rect x="0" y="0" width={W} height={H} />
            </clipPath>
          </defs>
          <g clipPath="url(#marco-mapa)">
            <rect x="0" y="0" width={W} height={H} fill="var(--page)" />
            <g transform={`translate(${vista.x},${vista.y}) scale(${vista.k})`}>
              <path
                d={retic}
                fill="none"
                stroke="var(--grid)"
                strokeWidth={0.5 / vista.k}
              />
              <path
                d={tierra}
                fill="var(--surface-2)"
                stroke="var(--axis)"
                strokeWidth={0.5 / vista.k}
              />
            </g>

            {/* Los puntos van FUERA del grupo escalado: así conservan su
                tamaño en pantalla a cualquier zoom y siguen siendo fáciles de
                señalar. */}
            {grupos.map((g) => {
              const n = g.miembros.length;
              if (n > 1) {
                const r = 9 + Math.min(7, n * 1.6);
                return (
                  <g
                    key={"g" + g.miembros[0].id}
                    className="cursor-zoom-in"
                    onClick={() => {
                      setGrupoSel(g.miembros);
                      zoomA(vista.k * 2.4, g.xs, g.ys);
                    }}
                    role="button"
                    tabIndex={0}
                    aria-label={tx({
                      es:
                        n +
                        " estudios en esta localidad; pulsa para acercar y verlos",
                      en: n + " studies at this locality; click to zoom in and list",
                    })}
                    onKeyDown={(ev) => {
                      if (ev.key !== "Enter") return;
                      setGrupoSel(g.miembros);
                      zoomA(vista.k * 2.4, g.xs, g.ys);
                    }}
                  >
                    <circle
                      cx={g.xs}
                      cy={g.ys}
                      r={r}
                      fill="var(--seq-400)"
                      fillOpacity={0.28}
                      stroke="var(--seq-550)"
                      strokeWidth={1.6}
                    />
                    <text
                      x={g.xs}
                      y={g.ys}
                      textAnchor="middle"
                      dominantBaseline="central"
                      className="tabular pointer-events-none"
                      fontSize={11}
                      fontWeight={600}
                      fill="var(--ink)"
                    >
                      {n}
                    </text>
                  </g>
                );
              }
              const e = g.miembros[0];
              const on = activo?.id === e.id;
              return (
                <circle
                  key={e.id}
                  cx={g.xs}
                  cy={g.ys}
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
                  onFocus={() => setActivo(e)}
                  onBlur={() => setActivo(null)}
                />
              );
            })}

            {sSitio && (
              <g className="pointer-events-none">
                <circle
                  cx={sSitio[0]}
                  cy={sSitio[1]}
                  r={11}
                  fill="none"
                  stroke="var(--sitio)"
                  strokeWidth={2}
                />
                <circle cx={sSitio[0]} cy={sSitio[1]} r={3} fill="var(--sitio)" />
                <text
                  x={sSitio[0] - 16}
                  y={sSitio[1] + 26}
                  textAnchor="end"
                  className="fill-(--ink) text-[11px] font-semibold"
                >
                  MSH-BC-21
                </text>
              </g>
            )}
          </g>
        </svg>

        {activo && activoPos && (
          <div
            className="pointer-events-none absolute z-10 w-[19rem] max-w-[80vw] rounded-[6px] border border-(--border) bg-(--surface) px-3 py-2.5 shadow-lg"
            style={{
              left: (activoPos[0] / W) * 100 + "%",
              top: (activoPos[1] / H) * 100 + "%",
              transform:
                "translate(" +
                (activoPos[0] < W * 0.22
                  ? "0"
                  : activoPos[0] > W * 0.78
                    ? "-100%"
                    : "-50%") +
                ", " +
                (activoPos[1] < H * 0.38 ? "1.4rem" : "calc(-100% - 1.1rem)") +
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
                  [tx({ es: "Registros", en: "Records" }), activo.n_registros],
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

      {grupoSel && (
        <div className="mt-3 rounded-[6px] border border-(--border) bg-(--surface) p-3">
          <div className="mb-2 flex items-baseline justify-between gap-3">
            <span className="text-[0.82rem] font-semibold">
              {grupoSel.length}{" "}
              {tx({
                es: "estudios en esta localidad",
                en: "studies at this locality",
              })}
            </span>
            <button
              type="button"
              onClick={() => setGrupoSel(null)}
              className="text-[0.74rem] text-(--muted) underline underline-offset-2 hover:text-(--ink)"
            >
              {tx({ es: "cerrar", en: "close" })}
            </button>
          </div>
          <ul className="space-y-1.5">
            {grupoSel.map((e) => (
              <li
                key={e.id}
                onMouseEnter={() => setActivo(e)}
                onMouseLeave={() => setActivo(null)}
                className="flex flex-wrap items-baseline gap-x-2 text-[0.8rem] leading-snug"
              >
                <span
                  className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
                  style={{
                    background: FLUIDO[e.tipo_filtracion]?.color ?? "var(--muted)",
                  }}
                />
                <strong className="font-semibold">
                  {(e.autores ?? ["?"])[0]} {e.anio}
                </strong>
                <span className="text-(--ink-2)">{e.localidad}</span>
                <span className="text-(--muted)">
                  {e.prof_m ? " · " + e.prof_m + " m" : ""}
                  {e.morfologia_label ? " · " + e.morfologia_label : ""}
                  {" · " + e.n_registros + " "}
                  {tx({ es: "registros", en: "records" })}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="sr-only" aria-live="polite">
        {activo
          ? activo.localidad +
            " — " +
            (activo.autores ?? ["?"])[0] +
            " " +
            (activo.anio ?? "")
          : ""}
      </p>

      <p className="mt-3 text-[0.75rem] text-(--muted)">
        {tx({
          es: "Arrastra para mover el mapa y usa la rueda o los botones para acercar. Los círculos azules con un número reúnen varios estudios: pulsa uno para acercarte y ver su lista debajo. Pasa el cursor —o tabula— por un punto para ver el estudio.",
          en: "Drag to pan and use the wheel or the buttons to zoom. Blue circles with a number hold several studies: click one to zoom in and see them listed below. Hover — or tab — over a dot to see the study.",
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

      <ComoSeLee>
        {tx({
          es: "Cada punto es un estudio, situado en la localidad de filtración que describe. Las coordenadas son la posición representativa de esa localidad, no la del testigo concreto: sirven para situar los trabajos, no para análisis espacial fino. Doce estudios comparten coordenada con otro —tres en Hydrate Ridge, tres en Vestnesa Ridge, dos en la bahía de Monterey—, así que los que se solapan en pantalla se reúnen en un círculo con su número; al acercar el zoom se van separando, cada uno en su posición real. Cuando dos estudios comparten coordenada EXACTA no hay zoom que los separe —su posición es la misma—, y por eso al pulsar el círculo se despliega su lista debajo del mapa. Ningún punto se desplaza nunca de su sitio. El color codifica el tipo de fluido; pulsa la leyenda para filtrar. El anillo marca la muestra de la tesis.",
          en: "Each dot is a study, placed at the seep locality it describes. Coordinates are the representative position of that locality, not of the individual core: they place the work, they are not for fine spatial analysis. Twelve studies share coordinates with another — three at Hydrate Ridge, three at Vestnesa Ridge, two in Monterey Bay — so those overlapping on screen are gathered into a circle with their count; zooming in gradually splits them, each at its true position. When two studies share the EXACT same coordinates no zoom can separate them — their position is identical — which is why clicking the circle lists them below the map. No dot is ever moved from its place. Colour encodes fluid type; click the legend to filter. The ring marks the thesis sample.",
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
