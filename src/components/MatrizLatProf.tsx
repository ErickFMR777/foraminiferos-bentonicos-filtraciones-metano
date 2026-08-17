"use client";

import { useState } from "react";
import matriz from "@datos/matriz_lat_prof.json";

type Celda = {
  lat: string;
  prof: string;
  registros: number;
  taxones: number;
  estudios: number;
};

const CELDAS = matriz.celdas as Celda[];
const LATS = matriz.lats as string[];
const PROFS = matriz.profs as string[];
const SITIO = matriz.sitio_tesis;

const TOTAL = CELDAS.reduce((s, c) => s + c.registros, 0);
const MAX = Math.max(...CELDAS.map((c) => c.registros));

/** Rampa secuencial de un solo tono. El paso más claro es «poco», no «nada»:
 *  la ausencia de datos se codifica aparte, con trama. */
function paso(n: number): { fondo: string; tinta: string } {
  if (n === 0) return { fondo: "var(--sin-datos)", tinta: "var(--muted)" };
  const r = n / MAX;
  if (r <= 0.1) return { fondo: "var(--seq-100)", tinta: "#0d366b" };
  if (r <= 0.25) return { fondo: "var(--seq-250)", tinta: "#0d366b" };
  if (r <= 0.55) return { fondo: "var(--seq-400)", tinta: "#ffffff" };
  return { fondo: "var(--seq-550)", tinta: "#ffffff" };
}

const get = (lat: string, prof: string) =>
  CELDAS.find((c) => c.lat === lat && c.prof === prof)!;

const esSitio = (lat: string, prof: string) =>
  lat === SITIO.banda_lat && prof === SITIO.banda_prof;

export default function MatrizLatProf() {
  const [activa, setActiva] = useState<Celda | null>(null);
  const [tabla, setTabla] = useState(false);

  const conDatos = CELDAS.filter((c) => c.registros > 0).length;
  const prof500 = CELDAS.filter((c) => c.prof === "> 500 m").reduce(
    (s, c) => s + c.registros,
    0,
  );

  return (
    <figure className="m-0">
      <figcaption className="mb-5">
        <h2 className="text-[1.6rem] leading-tight mb-2">
          Dónde se ha estudiado la relación entre foraminíferos y filtraciones
        </h2>
        <p className="text-[0.95rem] leading-relaxed text-(--ink-2) max-w-[62ch]">
          Cada celda cruza una banda de latitud con un intervalo de profundidad.
          El color indica cuántos registros aporta la literatura revisada.{" "}
          <strong className="font-semibold text-(--ink)">
            El {Math.round((prof500 / TOTAL) * 100)}% de todo lo publicado
            procede de aguas de más de 500 m
          </strong>
          , y tres de las cuatro bandas latitudinales no tienen ni un solo dato
          somero.
        </p>
      </figcaption>

      <div className="overflow-x-auto">
        <table className="border-separate border-spacing-[2px] tabular">
          <caption className="sr-only">
            Registros de foraminíferos en ambientes de filtración, por banda
            latitudinal y rango de profundidad
          </caption>
          <thead>
            <tr>
              <th scope="col" className="sr-only">
                Latitud
              </th>
              {PROFS.map((p) => (
                <th
                  key={p}
                  scope="col"
                  className="px-3 pb-2 text-[0.78rem] font-medium text-(--muted) whitespace-nowrap"
                >
                  {p}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {LATS.map((lat) => (
              <tr key={lat}>
                <th
                  scope="row"
                  className="pr-3 text-right text-[0.78rem] font-medium text-(--muted) whitespace-nowrap"
                >
                  {lat}°
                </th>
                {PROFS.map((prof) => {
                  const c = get(lat, prof);
                  const vacia = c.registros === 0;
                  const sitio = esSitio(lat, prof);
                  const { fondo, tinta } = paso(c.registros);
                  return (
                    <td key={prof} className="p-0">
                      <button
                        type="button"
                        onMouseEnter={() => setActiva(c)}
                        onMouseLeave={() => setActiva(null)}
                        onFocus={() => setActiva(c)}
                        onBlur={() => setActiva(null)}
                        aria-label={`Latitud ${lat} grados, profundidad ${prof}: ${c.registros} registros, ${c.taxones} taxones, ${c.estudios} estudios${sitio ? ". Aquí cae la muestra del Caribe colombiano" : ""}`}
                        className={`relative grid h-[86px] w-[116px] place-items-center rounded-[4px] transition-[box-shadow] ${vacia ? "trama-sin-datos" : ""}`}
                        style={{
                          background: fondo,
                          color: tinta,
                          boxShadow: sitio
                            ? "inset 0 0 0 2px var(--sitio)"
                            : undefined,
                        }}
                      >
                        <span className="text-[1.5rem] font-semibold leading-none">
                          {vacia ? "—" : c.registros}
                        </span>
                        {!vacia && (
                          <span className="mt-1 text-[0.68rem] opacity-80">
                            {c.estudios} {c.estudios === 1 ? "estudio" : "estudios"}
                          </span>
                        )}
                        {vacia && (
                          <span className="mt-1 text-[0.68rem] text-(--muted)">
                            sin datos
                          </span>
                        )}
                      </button>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Anotación del sitio de la tesis: forma y rótulo, no un color de serie */}
      <p className="mt-4 flex items-start gap-2 text-[0.85rem] leading-relaxed text-(--ink-2) max-w-[58ch]">
        <span
          aria-hidden
          className="mt-[3px] inline-block h-3 w-3 shrink-0 rounded-[2px]"
          style={{ boxShadow: "inset 0 0 0 2px var(--sitio)" }}
        />
        <span>
          La muestra <strong className="font-semibold text-(--ink)">MSH-BC-21</strong>{" "}
          del Caribe colombiano cae en {SITIO.banda_lat}° y {SITIO.banda_prof}:{" "}
          <strong className="font-semibold text-(--ink)">
            una celda sin ningún estudio previo
          </strong>
          .
        </span>
      </p>

      {/* Leyenda */}
      <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-[0.75rem] text-(--muted)">
        <span className="flex items-center gap-2">
          Menos
          <span className="flex gap-[2px]">
            {["var(--seq-100)", "var(--seq-250)", "var(--seq-400)", "var(--seq-550)"].map(
              (c) => (
                <span
                  key={c}
                  className="h-3 w-6 rounded-[2px]"
                  style={{ background: c }}
                />
              ),
            )}
          </span>
          Más registros
        </span>
        <span className="flex items-center gap-2">
          <span className="trama-sin-datos h-3 w-6 rounded-[2px]" style={{ background: "var(--sin-datos)" }} />
          Sin datos publicados
        </span>
        <button
          type="button"
          onClick={() => setTabla((v) => !v)}
          className="underline underline-offset-2 hover:text-(--ink)"
        >
          {tabla ? "Ocultar tabla" : "Ver como tabla"}
        </button>
      </div>

      {/* Detalle al pasar el cursor */}
      <div className="mt-3 min-h-[2.6rem] text-[0.85rem] leading-snug" aria-live="polite">
        {activa && (
          <div className="rounded-[5px] border border-(--border) bg-(--surface) px-3 py-2 inline-block">
            <strong className="font-semibold">
              {activa.lat}° · {activa.prof}
            </strong>
            {activa.registros === 0 ? (
              <span className="text-(--ink-2)">
                {" "}— ningún estudio publicado en estas condiciones
              </span>
            ) : (
              <span className="text-(--ink-2)">
                {" "}— {activa.registros} registros · {activa.taxones} taxones ·{" "}
                {activa.estudios} estudios
              </span>
            )}
          </div>
        )}
      </div>

      {tabla && (
        <table className="mt-4 w-full max-w-[46rem] border-collapse text-[0.85rem] tabular">
          <thead>
            <tr className="border-b border-(--axis) text-left">
              <th className="py-1.5 pr-4 font-medium">Latitud</th>
              <th className="py-1.5 pr-4 font-medium">Profundidad</th>
              <th className="py-1.5 pr-4 text-right font-medium">Registros</th>
              <th className="py-1.5 pr-4 text-right font-medium">Taxones</th>
              <th className="py-1.5 text-right font-medium">Estudios</th>
            </tr>
          </thead>
          <tbody>
            {CELDAS.map((c) => (
              <tr key={`${c.lat}-${c.prof}`} className="border-b border-(--grid)">
                <td className="py-1.5 pr-4">{c.lat}°</td>
                <td className="py-1.5 pr-4">{c.prof}</td>
                <td className="py-1.5 pr-4 text-right">{c.registros || "—"}</td>
                <td className="py-1.5 pr-4 text-right">{c.taxones || "—"}</td>
                <td className="py-1.5 text-right">{c.estudios || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <p className="mt-4 text-[0.72rem] leading-relaxed text-(--muted) max-w-[62ch]">
        {TOTAL} registros de {conDatos} de las 12 combinaciones posibles, a
        partir de 38 estudios revisados. Un «registro» es la mención de un taxón
        en un estudio para una banda y profundidad dadas.
      </p>
    </figure>
  );
}
