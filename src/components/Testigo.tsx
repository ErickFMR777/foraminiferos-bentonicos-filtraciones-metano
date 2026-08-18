"use client";

import msh from "@datos/msh_bc21.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota } from "@/lib/ui";

const FRACC = ["125", "250", "500"] as const;
const CM = ["MSH_21_BC_01", "MSH_21_BC_02"] as const;

type Ab = Record<string, Record<string, Record<string, number | null>>>;

export default function Testigo() {
  const { tx } = useT();
  const ab = msh.abundancias as unknown as Ab;

  const serie = (variable: string, cm: string) =>
    FRACC.map((f) => ab[cm]?.[variable]?.[f] ?? 0);

  const bent = CM.map((c) => serie("Abundancia F.B", c));
  const max = Math.max(...bent.flat());

  const totalB = CM.map((c) => ab[c]?.["Forams B extraidos"]?.TOTAL ?? 0);
  const totalP = CM.map((c) => ab[c]?.["Forams P extraidos"]?.TOTAL ?? 0);
  const densidad = CM.map((c) => ab[c]?.["Abundancia F.B"]?.TOTAL ?? 0);

  return (
    <figure className="m-0">
      <div className="grid gap-8 md:grid-cols-[1.4fr_1fr]">
        <div>
          <h3 className="mb-5 text-[0.8rem] uppercase tracking-[0.1em] text-(--muted)">
            {tx({
              es: "Densidad por fracción de tamaño (ind./g)",
              en: "Density by size fraction (ind./g)",
            })}
          </h3>
          <svg viewBox="0 0 420 210" className="w-full" role="img"
            aria-label={tx({
              es: "Densidad de foraminíferos bentónicos por fracción de tamaño en los dos centímetros del testigo",
              en: "Benthic foraminifera density by size fraction across the two centimetres of the core",
            })}>
            {[0, 0.5, 1].map((g) => (
              <g key={g}>
                <line
                  x1={44}
                  x2={414}
                  y1={170 - g * 150}
                  y2={170 - g * 150}
                  stroke="var(--grid)"
                  strokeWidth={1}
                />
                <text
                  x={38}
                  y={174 - g * 150}
                  textAnchor="end"
                  className="fill-(--muted) text-[9px] tabular"
                >
                  {Math.round(g * max).toLocaleString("es")}
                </text>
              </g>
            ))}
            {FRACC.map((f, i) => {
              const x = 80 + i * 120;
              return (
                <g key={f}>
                  {bent.map((s, ci) => {
                    const h = (s[i] / max) * 150;
                    return (
                      <rect
                        key={ci}
                        x={x + ci * 26 - 26}
                        y={170 - h}
                        width={22}
                        height={Math.max(h, 1)}
                        rx={3}
                        fill={
                          ci === 0
                            ? "var(--pared-hialino)"
                            : "var(--pared-porcelanaceo)"
                        }
                      />
                    );
                  })}
                  <text
                    x={x - 2}
                    y={188}
                    textAnchor="middle"
                    className="fill-(--ink-2) text-[10px]"
                  >
                    {f} µm
                  </text>
                </g>
              );
            })}
          </svg>
          <div className="mt-3 flex gap-5 text-[0.75rem] text-(--muted)">
            {CM.map((c, i) => (
              <span key={c} className="flex items-center gap-1.5">
                <span
                  className="inline-block h-2.5 w-4 rounded-[2px]"
                  style={{
                    background:
                      i === 0 ? "var(--pared-hialino)" : "var(--pared-porcelanaceo)",
                  }}
                />
                {tx({ es: "cm ", en: "cm " })}
                {i + 1}
              </span>
            ))}
          </div>
        </div>

        <div className="space-y-5">
          {[
            {
              t: tx({ es: "Densidad total", en: "Total density" }),
              v: densidad.map((d) => Math.round(d).toLocaleString("es")),
              u: "ind./g",
            },
            {
              t: tx({ es: "Bentónicos extraídos", en: "Benthics picked" }),
              v: totalB.map((d) => d.toLocaleString("es")),
              u: "",
            },
            {
              t: tx({ es: "Razón bentónicos / planctónicos", en: "Benthic / planktic ratio" }),
              v: totalB.map((b, i) => (b / (totalP[i] || 1)).toFixed(2)),
              u: "",
            },
          ].map((f) => (
            <div key={f.t} className="border-t border-(--border) pt-3">
              <div className="mb-1.5 text-[0.78rem] text-(--muted)">{f.t}</div>
              <div className="flex items-baseline gap-3">
                <span className="tabular text-[1.35rem] font-semibold">{f.v[0]}</span>
                <span className="text-(--muted)">→</span>
                <span className="tabular text-[1.35rem] font-semibold">{f.v[1]}</span>
                {f.u && <span className="text-[0.72rem] text-(--muted)">{f.u}</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      <ComoSeLee>
        {tx({
          es: "Los dos centímetros superficiales del mismo testigo, no dos estaciones. Hacia abajo la densidad total cae de 4015 a 3050 ind./g, pero en la fracción fina de 125 µm SUBE de 6730 a 9224: la asociación se empobrece y a la vez se concentra en los tamaños pequeños. La razón bentónicos/planctónicos baja de 2,88 a 1,87.",
          en: "The two surface centimetres of the same core, not two stations. Downward, total density falls from 4015 to 3050 ind./g, yet in the fine 125 µm fraction it RISES from 6730 to 9224: the assemblage thins out and concentrates in the small sizes at once. The benthic/planktic ratio drops from 2.88 to 1.87.",
        })}
      </ComoSeLee>

      <Nota>
        {tx({
          es: "Son dos centímetros de un solo testigo: esto es una observación exploratoria, no una tendencia. La densidad se calcula como individuos extraídos dividido por el peso de sedimento picado, y así lo verifica la auditoría en las ocho celdas.",
          en: "These are two centimetres of a single core: an exploratory observation, not a trend. Density is computed as picked individuals divided by picked sediment weight, and the audit verifies it across all eight cells.",
        })}
      </Nota>
    </figure>
  );
}
