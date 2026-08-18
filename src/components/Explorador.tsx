"use client";

import { useMemo, useState } from "react";
import completo from "@datos/taxones_completo.json";
import { useT } from "@/lib/i18n";
import { ComoSeLee, Nota, Taxon } from "@/lib/ui";

type Fila = (typeof completo.taxones)[number];
type Orden = "estudios" | "dominancia" | "alfabetico";

export default function Explorador() {
  const { tx } = useT();
  const [busca, setBusca] = useState("");
  const [rango, setRango] = useState<"todos" | "especie" | "genero">("especie");
  const [soloMsh, setSoloMsh] = useState(false);
  const [orden, setOrden] = useState<Orden>("estudios");
  const [n, setN] = useState(25);

  const filas = useMemo(() => {
    let f = completo.taxones as Fila[];
    if (rango !== "todos") f = f.filter((t) => t.rango === rango);
    if (soloMsh) f = f.filter((t) => t.en_msh_bc21);
    if (busca.trim()) {
      const q = busca.trim().toLowerCase();
      f = f.filter(
        (t) =>
          t.taxon.toLowerCase().includes(q) ||
          (t.genero ?? "").toLowerCase().includes(q) ||
          (t.familia ?? "").toLowerCase().includes(q),
      );
    }
    const s = [...f];
    if (orden === "alfabetico") s.sort((a, b) => a.taxon.localeCompare(b.taxon));
    else if (orden === "dominancia")
      s.sort(
        (a, b) =>
          b.n_estudios_dominante - a.n_estudios_dominante ||
          b.n_estudios - a.n_estudios,
      );
    return s;
  }, [busca, rango, soloMsh, orden]);

  const maxEst = completo.taxones[0]?.n_estudios ?? 1;
  const sel =
    "rounded-[4px] border border-(--border) bg-(--surface) px-2 py-1 text-[0.78rem] text-(--ink)";

  return (
    <figure className="m-0">
      <div className="mb-5 flex flex-wrap items-center gap-2">
        <input
          type="search"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder={tx({
            es: "Buscar taxón, género o familia…",
            en: "Search taxon, genus or family…",
          })}
          aria-label={tx({ es: "Buscar", en: "Search" })}
          className={sel + " min-w-[15rem] flex-1"}
        />
        <select
          value={rango}
          onChange={(e) => setRango(e.target.value as typeof rango)}
          className={sel}
          aria-label={tx({ es: "Rango taxonómico", en: "Taxonomic rank" })}
        >
          <option value="especie">{tx({ es: "Especies", en: "Species" })}</option>
          <option value="genero">{tx({ es: "Géneros", en: "Genera" })}</option>
          <option value="todos">{tx({ es: "Todos", en: "All" })}</option>
        </select>
        <select
          value={orden}
          onChange={(e) => setOrden(e.target.value as Orden)}
          className={sel}
          aria-label={tx({ es: "Ordenar por", en: "Sort by" })}
        >
          <option value="estudios">
            {tx({ es: "Nº de estudios", en: "No. of studies" })}
          </option>
          <option value="dominancia">
            {tx({ es: "Dominancia", en: "Dominance" })}
          </option>
          <option value="alfabetico">
            {tx({ es: "Alfabético", en: "Alphabetical" })}
          </option>
        </select>
        <label className="flex items-center gap-1.5 text-[0.78rem] text-(--ink-2)">
          <input
            type="checkbox"
            checked={soloMsh}
            onChange={(e) => setSoloMsh(e.target.checked)}
          />
          {tx({ es: "Sólo en MSH-BC-21", en: "In MSH-BC-21 only" })}
        </label>
      </div>

      <p className="mb-3 text-[0.78rem] text-(--muted)">
        {filas.length} {tx({ es: "taxones", en: "taxa" })}
      </p>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[36rem] border-collapse text-[0.85rem]">
          <thead>
            <tr className="border-b border-(--axis) text-left text-[0.72rem] uppercase tracking-wide text-(--muted)">
              <th className="py-2 pr-3 font-medium">
                {tx({ es: "Taxón", en: "Taxon" })}
              </th>
              <th className="py-2 pr-3 font-medium">
                {tx({ es: "Familia", en: "Family" })}
              </th>
              <th className="py-2 pr-3 text-right font-medium">
                {tx({ es: "Estudios", en: "Studies" })}
              </th>
              <th className="py-2 pr-3 text-right font-medium">
                {tx({ es: "Dominante en", en: "Dominant in" })}
              </th>
              <th className="py-2 font-medium">MSH</th>
            </tr>
          </thead>
          <tbody>
            {filas.slice(0, n).map((t) => (
              <tr key={t.taxon} className="border-b border-(--grid)">
                <td className="py-2 pr-3">
                  <Taxon nombre={t.taxon} />
                  {t.rango === "genero" && (
                    <span className="ml-1.5 text-[0.68rem] text-(--muted)">
                      {tx({ es: "gén.", en: "gen." })}
                    </span>
                  )}
                </td>
                <td className="py-2 pr-3 text-[0.78rem] text-(--muted)">
                  {t.familia ?? "—"}
                </td>
                <td className="py-2 pr-3">
                  <div className="flex items-center justify-end gap-2">
                    <span
                      className="h-2 rounded-[1px]"
                      style={{
                        width: (t.n_estudios / maxEst) * 68 + "px",
                        background: "var(--pared-hialino)",
                      }}
                    />
                    <span className="tabular w-6 text-right">{t.n_estudios}</span>
                  </div>
                </td>
                <td className="tabular py-2 pr-3 text-right">
                  {t.n_estudios_dominante || (
                    <span className="text-(--muted)">—</span>
                  )}
                </td>
                <td className="py-2">
                  {t.en_msh_bc21 && (
                    <span
                      className="inline-block h-2 w-2 rounded-full"
                      style={{ background: "var(--sitio)" }}
                      aria-label="presente en MSH-BC-21"
                    />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filas.length > n && (
        <button
          type="button"
          onClick={() => setN(n + 50)}
          className="mt-4 text-[0.8rem] text-(--muted) underline underline-offset-2 hover:text-(--ink)"
        >
          {tx({ es: "Mostrar más", en: "Show more" })} ({filas.length - n})
        </button>
      )}

      <ComoSeLee>
        {tx({
          es: "«Estudios» cuenta en cuántos artículos aparece el taxón: es la señal sólida. «Dominante en» cuenta en cuántos el propio texto lo declara dominante o más abundante, y es la única señal que puede leerse como dominancia. No se muestra el número de menciones porque es un proxy engañoso: un artículo largo repite nombres en la introducción, en la discusión y al citar a otros.",
          en: "“Studies” counts how many articles mention the taxon: the solid signal. “Dominant in” counts how many state it as dominant or most abundant, and is the only signal that can be read as dominance. Mention counts are not shown because they are a misleading proxy: a long article repeats names in the introduction, the discussion and when citing others.",
        })}
      </ComoSeLee>

      <Nota>
        {tx({
          es:
            "Extraído del texto completo de " +
            completo.resumen.articulos_leidos +
            " artículos y validado contra WoRMS: si la autoridad no reconoce un nombre, no entra. La base original de la tesis recogía " +
            completo.resumen.taxones_base_tesis +
            " taxones porque su metodología tomaba las cinco especies principales de cada filtro; la unión de ambas fuentes son " +
            completo.resumen.union_taxones +
            ". Un artículo escaneado sin capa de texto no pudo leerse.",
          en:
            "Extracted from the full text of " +
            completo.resumen.articulos_leidos +
            " articles and validated against WoRMS: if the authority does not recognise a name, it does not enter. The thesis base held " +
            completo.resumen.taxones_base_tesis +
            " taxa because its method took the top five species per filter; the union of both sources is " +
            completo.resumen.union_taxones +
            ". One scanned article without a text layer could not be read.",
        })}
      </Nota>
    </figure>
  );
}
