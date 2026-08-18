"use client";

import pared from "@datos/pared_por_banda.json";
import msh from "@datos/msh_bc21.json";
import { useApp, useT } from "@/lib/i18n";
import { ComoSeLee, Nota } from "@/lib/ui";

/** Referencia publicada: Chiang et al. (2015) contrastan sitios de filtración
 *  con sitios de control en la misma zona. Es la única cifra de control que
 *  la literatura de la tesis aporta, y sirve de vara de medir. */
const CONTROL = { calcareo: 24, aglutinado: 76 };
const SEEP_LIT = { calcareo: 68, aglutinado: 32 };

function Barra({
  calcareo,
  n,
  etiqueta,
  destacado,
}: {
  calcareo: number;
  n?: number;
  etiqueta: string;
  destacado?: boolean;
}) {
  const agl = 100 - calcareo;
  const pocos = n !== undefined && n < 10;
  return (
    <div className="mb-3">
      <div className="mb-1 flex items-baseline justify-between text-[0.78rem]">
        <span className={destacado ? "font-semibold text-(--ink)" : "text-(--ink-2)"}>
          {etiqueta}
        </span>
        <span className="tabular text-(--muted)">
          {calcareo.toFixed(0)} / {agl.toFixed(0)}
          {n !== undefined && (
            <span className={pocos ? "ml-2 text-(--pared-aglutinado)" : "ml-2"}>
              n={n}
            </span>
          )}
        </span>
      </div>
      <div
        className="flex h-6 gap-[2px] overflow-hidden rounded-[3px]"
        style={{ opacity: pocos ? 0.55 : 1 }}
      >
        <div
          style={{ width: calcareo + "%", background: "var(--pared-hialino)" }}
          className="rounded-l-[3px]"
        />
        <div
          style={{ width: agl + "%", background: "var(--pared-aglutinado)" }}
          className="rounded-r-[3px]"
        />
      </div>
    </div>
  );
}

export default function ParedPorBanda() {
  const { tx } = useT();
  const { modo } = useApp();
  const lat = pared.filter((p) => p.eje === "latitud" && p.n > 0);
  const prof = pared.filter((p) => p.eje === "profundidad" && p.n > 0);
  const pocos = pared.filter((p) => p.n > 0 && p.n < 10).length;

  return (
    <figure className="m-0">
      <div className="grid gap-x-10 gap-y-8 md:grid-cols-2">
        <div>
          <h3 className="mb-4 text-[0.8rem] uppercase tracking-[0.1em] text-(--muted)">
            {tx({ es: "Por latitud", en: "By latitude" })}
          </h3>
          {lat.map((p) => (
            <Barra
              key={p.banda}
              calcareo={p.calcareo ?? 0}
              n={modo === "exploracion" ? p.n : undefined}
              etiqueta={p.banda + "°"}
            />
          ))}
        </div>
        <div>
          <h3 className="mb-4 text-[0.8rem] uppercase tracking-[0.1em] text-(--muted)">
            {tx({ es: "Por profundidad", en: "By depth" })}
          </h3>
          {prof.map((p) => (
            <Barra
              key={p.banda}
              calcareo={p.calcareo ?? 0}
              n={modo === "exploracion" ? p.n : undefined}
              etiqueta={p.banda}
            />
          ))}
        </div>
      </div>

      <div className="mt-8 border-t border-(--border) pt-6">
        <h3 className="mb-4 text-[0.8rem] uppercase tracking-[0.1em] text-(--muted)">
          {tx({ es: "Contra las referencias", en: "Against reference values" })}
        </h3>
        <Barra
          calcareo={SEEP_LIT.calcareo}
          etiqueta={tx({
            es: "Filtraciones (Chiang et al., 2015)",
            en: "Seep sites (Chiang et al., 2015)",
          })}
        />
        <Barra
          calcareo={CONTROL.calcareo}
          etiqueta={tx({
            es: "Control sin filtración (Chiang et al., 2015)",
            en: "Non-seep control (Chiang et al., 2015)",
          })}
        />
        <Barra
          calcareo={msh.pared.Calcareo}
          etiqueta="MSH-BC-21"
          destacado
        />
      </div>

      <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-[0.75rem] text-(--muted)">
        <span className="flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-4 rounded-[2px]"
            style={{ background: "var(--pared-hialino)" }}
          />
          {tx({ es: "Calcáreos", en: "Calcareous" })}
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-4 rounded-[2px]"
            style={{ background: "var(--pared-aglutinado)" }}
          />
          {tx({ es: "Aglutinados", en: "Agglutinated" })}
        </span>
      </div>

      <ComoSeLee>
        {tx({
          es: "Cada barra reparte el 100% entre formas calcáreas y aglutinadas. La literatura sostiene que en las filtraciones los aglutinados se desploman, porque toleran mal el metano y el sulfuro. MSH-BC-21 muestra 87 / 13, más extremo aún que el valor de filtración publicado. Las bandas con menos de diez registros aparecen atenuadas: con tan pocos datos el porcentaje es frágil.",
          en: "Each bar splits 100% between calcareous and agglutinated forms. The literature holds that agglutinated taxa collapse at seeps, tolerating methane and sulphide poorly. MSH-BC-21 shows 87 / 13, even more extreme than the published seep value. Bands with fewer than ten records are dimmed: with so few data the percentage is fragile.",
        })}
      </ComoSeLee>

      <Nota>
        {tx({
          es:
            "Sólo 19 de los registros de la base son aglutinados, así que " +
            pocos +
            " bandas quedan por debajo de diez registros. La corrección de Ammodiscus —mal clasificado como porcelanáceo— movió el valor de MSH-BC-21 de 88,8 a 87,0%.",
          en:
            "Only 19 records in the base are agglutinated, so " +
            pocos +
            " bands fall below ten records. Correcting Ammodiscus — misfiled as porcelaneous — moved the MSH-BC-21 value from 88.8 to 87.0%.",
        })}
      </Nota>
    </figure>
  );
}
