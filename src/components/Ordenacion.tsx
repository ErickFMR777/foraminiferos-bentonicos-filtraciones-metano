"use client";

import { useState } from "react";
import ord from "@datos/ordenacion.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota } from "@/lib/ui";

/** Latitud absoluta -> banda, igual que en el resto del dashboard. */
const banda = (lat: number | null) =>
  lat === null
    ? "sin dato"
    : Math.abs(lat) < 15
      ? "0-15°"
      : Math.abs(lat) < 30
        ? "15-30°"
        : Math.abs(lat) < 60
          ? "30-60°"
          : "60-90°";

const COLOR_FLUIDO: Record<string, string> = {
  frio: "var(--pared-hialino)",
  termogenico: "var(--pared-aglutinado)",
  biogenico: "var(--pared-porcelanaceo)",
};
const COLOR_LAT: Record<string, string> = {
  "0-15°": "var(--seq-700)",
  "15-30°": "var(--seq-550)",
  "30-60°": "var(--seq-400)",
  "60-90°": "var(--seq-250)",
};

type Eje = "tipo_fluido" | "banda_latitud";

export default function Ordenacion() {
  const { tx, idioma } = useT();
  const [color, setColor] = useState<Eje>("banda_latitud");

  const P = ord.puntos;
  const W = 720;
  const H = 440;
  const M = { t: 18, r: 18, b: 44, l: 52 };

  const x1 = Math.min(...P.map((p) => p.eje1));
  const x2 = Math.max(...P.map((p) => p.eje1));
  const y1 = Math.min(...P.map((p) => p.eje2));
  const y2 = Math.max(...P.map((p) => p.eje2));
  const pad = 0.06;
  const ex = (v: number) =>
    M.l + ((v - x1 + pad) / (x2 - x1 + 2 * pad)) * (W - M.l - M.r);
  const ey = (v: number) =>
    H - M.b - ((v - y1 + pad) / (y2 - y1 + 2 * pad)) * (H - M.t - M.b);
  // El radio va con la RAÍZ de la riqueza: el área es lo que el ojo compara,
  // y escalar el radio directo exagera los estudios ricos.
  const rmax = Math.max(...P.map((p) => p.riqueza));
  const er = (n: number) => 5 + 9 * Math.sqrt(n / rmax);

  const grupo = (p: (typeof P)[number]) =>
    color === "tipo_fluido" ? p.tipo_fluido || "sin dato" : banda(p.lat);
  const paleta = color === "tipo_fluido" ? COLOR_FLUIDO : COLOR_LAT;
  const leyenda = [...new Set(P.map(grupo))].sort();

  const ETI: Record<string, { es: string; en: string }> = {
    frio: { es: "Filtración fría", en: "Cold seep" },
    termogenico: { es: "Termogénico", en: "Thermogenic" },
    biogenico: { es: "Biogénico", en: "Biogenic" },
  };
  const eti = (g: string) => (ETI[g] ? tx(ETI[g]) : g);

  const f = ord.factores;
  const num = (v: number, d = 3) =>
    v.toFixed(d).replace(".", idioma === "es" ? "," : ".");

  return (
    <figure className="m-0">
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <span className="text-[0.75rem] text-(--muted)">
          {tx({ es: "Colorear por", en: "Colour by" })}
        </span>
        {(["banda_latitud", "tipo_fluido"] as Eje[]).map((e) => (
          <button
            key={e}
            type="button"
            onClick={() => setColor(e)}
            aria-pressed={color === e}
            className={
              "rounded-[4px] px-2.5 py-1 text-[0.72rem] transition-colors " +
              (color === e
                ? "bg-(--ink) text-(--surface)"
                : "text-(--muted) hover:text-(--ink)")
            }
          >
            {e === "banda_latitud"
              ? tx({ es: "Latitud", en: "Latitude" })
              : tx({ es: "Tipo de fluido", en: "Fluid type" })}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full min-w-[34rem]"
          role="img"
          aria-label={tx({
            es: "Ordenación PCoA de las asociaciones de foraminíferos por estudio",
            en: "PCoA ordination of foraminiferal assemblages by study",
          })}
        >
          {/* ejes en el cero: en una ordenación el origen es el centroide */}
          <line
            x1={ex(0)} x2={ex(0)} y1={M.t} y2={H - M.b}
            stroke="var(--grid)" strokeDasharray="3 3"
          />
          <line
            x1={M.l} x2={W - M.r} y1={ey(0)} y2={ey(0)}
            stroke="var(--grid)" strokeDasharray="3 3"
          />
          <line x1={M.l} x2={W - M.r} y1={H - M.b} y2={H - M.b} stroke="var(--axis)" />
          <line x1={M.l} x2={M.l} y1={M.t} y2={H - M.b} stroke="var(--axis)" />

          {P.map((p) => (
            <g key={p.estudio_id}>
              <circle
                cx={ex(p.eje1)} cy={ey(p.eje2)} r={er(p.riqueza)}
                fill={paleta[grupo(p)] ?? "var(--muted)"}
                fillOpacity={0.62}
                stroke={paleta[grupo(p)] ?? "var(--muted)"}
                strokeWidth={1.4}
              >
                <title>
                  {`${p.estudio_id} · ${p.autor} ${p.anio}\n${p.localidad}\n` +
                    tx({ es: "taxones: ", en: "taxa: " }) + p.riqueza}
                </title>
              </circle>
              <text
                x={ex(p.eje1)} y={ey(p.eje2) - er(p.riqueza) - 4}
                textAnchor="middle" className="tabular"
                fontSize={9.5} fill="var(--ink-2)"
              >
                {p.estudio_id}
              </text>
            </g>
          ))}

          <text
            x={(M.l + W - M.r) / 2} y={H - 10} textAnchor="middle"
            fontSize={11} fill="var(--muted)"
          >
            {tx({ es: "Eje 1", en: "Axis 1" })} ·{" "}
            {num(ord.varianza_explicada[0] * 100, 1)}%
          </text>
          <text
            x={14} y={(M.t + H - M.b) / 2} textAnchor="middle"
            fontSize={11} fill="var(--muted)"
            transform={`rotate(-90 14 ${(M.t + H - M.b) / 2})`}
          >
            {tx({ es: "Eje 2", en: "Axis 2" })} ·{" "}
            {num(ord.varianza_explicada[1] * 100, 1)}%
          </text>
        </svg>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-[0.75rem]">
        {leyenda.map((g) => (
          <span key={g} className="flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ background: paleta[g] ?? "var(--muted)" }}
            />
            {eti(g)}
          </span>
        ))}
        <span className="text-(--muted)">
          {tx({
            es: "· el tamaño del círculo es el nº de taxones",
            en: "· circle size is the number of taxa",
          })}
        </span>
      </div>

      {/* --- resultados de la prueba --- */}
      <div className="mt-8 border-t border-(--border) pt-6">
        <h3 className="mb-3 text-[0.8rem] uppercase tracking-[0.1em] text-(--muted)">
          {tx({
            es: "¿Separa alguna variable las asociaciones? (PERMANOVA)",
            en: "Does any variable separate the assemblages? (PERMANOVA)",
          })}
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[30rem] border-collapse text-[0.85rem]">
            <thead>
              <tr className="border-b border-(--border) text-left text-(--muted)">
                <th className="py-1.5 font-medium">
                  {tx({ es: "Variable", en: "Variable" })}
                </th>
                <th className="py-1.5 text-right font-medium">pseudo-F</th>
                <th className="py-1.5 text-right font-medium">p</th>
                <th className="py-1.5 pl-4 font-medium">
                  {tx({ es: "Lectura", en: "Reading" })}
                </th>
              </tr>
            </thead>
            <tbody>
              {(
                [
                  ["banda_latitud", { es: "Banda de latitud", en: "Latitude band" }],
                  ["morfologia", { es: "Morfología del escape", en: "Seep morphology" }],
                  ["tipo_fluido", { es: "Tipo de fluido", en: "Fluid type" }],
                  ["banda_profundidad", { es: "Profundidad", en: "Depth" }],
                ] as const
              ).map(([k, lab]) => {
                const d = f[k as keyof typeof f];
                const sig = d.p !== null && d.p < 0.05;
                return (
                  <tr key={k} className="border-b border-(--border)">
                    <td className="py-1.5">{tx(lab)}</td>
                    <td className="py-1.5 text-right tabular">
                      {d.pseudo_F === null ? "—" : num(d.pseudo_F)}
                    </td>
                    <td
                      className="py-1.5 text-right tabular"
                      style={{ color: sig ? "var(--ink)" : "var(--muted)" }}
                    >
                      {d.p === null ? "—" : num(d.p, 4)}
                    </td>
                    <td className="py-1.5 pl-4 text-[0.8rem] text-(--ink-2)">
                      {sig
                        ? tx({ es: "separa", en: "separates" })
                        : tx({ es: "no separa", en: "does not separate" })}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <ComoSeLee>
        {tx({
          es: "Cada círculo es un estudio, situado por el parecido de su lista de taxones con la de los demás: dos puntos próximos comparten especies. La posición sale de un PCoA sobre la distancia de Jaccard entre presencias, y el PERMANOVA prueba, por permutación, si los grupos de una variable están más juntos entre sí de lo que cabría esperar por azar. Los ejes no tienen unidades: sólo importan las distancias relativas, y el porcentaje indica cuánta de la variación total recoge cada eje.",
          en: "Each circle is one study, placed by how similar its taxon list is to the others': nearby points share species. Position comes from a PCoA on the Jaccard distance between presences, and PERMANOVA tests by permutation whether the groups of a variable sit closer together than chance would predict. The axes have no units: only relative distances matter, and the percentage shows how much of the total variation each axis captures.",
        })}
      </ComoSeLee>

      <Nota>
        {tx({
          es: `Sobre ${ord.n_estudios} estudios y ${ord.n_taxones} taxones. Es un análisis exploratorio, no confirmatorio: con doce estudios y grupos desiguales, un valor de p rozando 0,05 no sostiene una conclusión. La franja de riqueza 18-70 taxones no es un recorte arbitrario — es la única en que la riqueza deja de gobernar el primer eje (rho = ${num(ord.correlacion_con_riqueza.eje1_rho)}, p = ${num(ord.correlacion_con_riqueza.eje1_p, 2)}).`,
          en: `Over ${ord.n_estudios} studies and ${ord.n_taxones} taxa. This is exploratory, not confirmatory: with twelve studies and unequal groups, a p-value hovering around 0.05 does not support a conclusion. The 18-70 taxa richness band is not an arbitrary cut — it is the only one in which richness stops governing the first axis (rho = ${num(ord.correlacion_con_riqueza.eje1_rho)}, p = ${num(ord.correlacion_con_riqueza.eje1_p, 2)}).`,
        })}
      </Nota>
    </figure>
  );
}
