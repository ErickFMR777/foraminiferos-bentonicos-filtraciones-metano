"use client";

import Barra from "./Barra";
import Composicion from "./Composicion";
import Cuenta from "./Cuenta";
import Explorador from "./Explorador";
import MapaMundial from "./MapaMundial";
import MatrizLatProf from "./MatrizLatProf";
import ParedPorBanda from "./ParedPorBanda";
import Referencias from "./Referencias";
import Sinu from "./Sinu";
import Testigo from "./Testigo";
import Veredicto from "./Veredicto";
import completo from "@datos/taxones_completo.json";
import correcciones from "@datos/correcciones.json";
import estudios from "@datos/estudios.json";
import matriz from "@datos/matriz_lat_prof.json";
import msh from "@datos/msh_bc21.json";
import { useT } from "@/lib/i18n";
import { Cifra, Nota, Seccion, Taxon } from "@/lib/ui";

export default function Pagina() {
  const { tx } = useT();
  const tropical = matriz.celdas.find(
    (c) => c.lat === "0-15" && c.prof === "> 500 m",
  );

  return (
    <>
      <Barra />
      <main className="mx-auto max-w-[68rem] px-6 pb-24">
        {/* ── portada ─────────────────────────────────────────── */}
        <header className="py-16 md:py-24">
          {/* El nombre del proyecto va COMPLETO, no abreviado: es el que
              consta en el contrato con Minciencias. */}
          <div className="mb-5 space-y-1 text-[0.72rem] uppercase tracking-[0.16em] text-(--muted)">
            <p>
              {tx({
                es: "Universidad Nacional de Colombia, sede Medellín · Facultad de Minas",
                en: "Universidad Nacional de Colombia, Medellín · Facultad de Minas",
              })}
            </p>
            <p className="text-(--ink-2)">
              {tx({
                es: "Proyecto Methane seep hunting: A multi-scale and multi method approach",
                en: "Methane seep hunting: A multi-scale and multi method approach",
              })}
            </p>
            <p>UPB · UNAL · GMAS · GEOMARES · ACGGP</p>
          </div>
          <h1 className="mb-4 max-w-[20ch] text-[2.5rem] leading-[1.08] md:text-[3.4rem]">
            {tx({
              es: "Foraminíferos bentónicos en filtraciones de metano",
              en: "Benthic foraminifera at methane seeps",
            })}
          </h1>
          {/* El subtítulo carga el alcance real del trabajo: la comparación es
              mundial y el Caribe colombiano es una de las localidades, no el
              objeto único. Sin esta línea el titular se leía como un estudio
              local. */}
          <p className="mb-6 max-w-[46ch] text-[1.15rem] leading-snug text-(--ink-2) md:text-[1.3rem]">
            {tx({
              es: "Comparación entre distintas localidades del mundo y la plataforma continental del Caribe colombiano",
              en: "A comparison between localities worldwide and the Colombian Caribbean continental shelf",
            })}
          </p>
          <p className="max-w-[58ch] text-[1.08rem] leading-relaxed text-(--ink-2)">
            {tx({
              es: "Protistas de menos de un milímetro que construyen un caparazón y registran en él las condiciones del fondo marino. Este trabajo reúne lo que la literatura mundial ha publicado sobre ellos en filtraciones de metano —40 estudios repartidos por los océanos del planeta— y lo contrasta con una muestra de la plataforma continental frente al Golfo de Morrosquillo.",
              en: "Protists under a millimetre across that build a shell and record the seafloor conditions in it. This work brings together what the global literature has published about them at methane seeps — 40 studies spread across the world's oceans — and contrasts it with a sample from the continental shelf off the Gulf of Morrosquillo.",
            })}
          </p>
        </header>

        <section className="grid grid-cols-2 gap-x-8 gap-y-7 border-y border-(--border) py-8 md:grid-cols-4">
          <Cifra
            valor={estudios.filter((e) => e.es_filtracion).length}
            etiqueta={tx({
              es: "estudios de filtración revisados",
              en: "seep studies reviewed",
            })}
          />
          <Cifra
            valor={completo.resumen.union_taxones}
            etiqueta={tx({ es: "taxones identificados", en: "taxa identified" })}
            nota={tx({
              es: "leyendo los artículos completos",
              en: "reading the full articles",
            })}
          />
          <Cifra
            valor={msh.indices.riqueza_S}
            etiqueta={tx({ es: "especies en MSH-BC-21", en: "species in MSH-BC-21" })}
          />
          <Cifra
            valor={0}
            etiqueta={tx({
              es: "estudios previos a esta latitud y profundidad",
              en: "previous studies at this latitude and depth",
            })}
          />
        </section>

        {/* ── 1 ─────────────────────────────────────────────────── */}
        <Seccion
          n={tx({ es: "01 · El vacío", en: "01 · The gap" })}
          titulo={tx({
            es: "Dónde se ha estudiado esto, y dónde no",
            en: "Where this has been studied, and where it has not",
          })}
        >
          <MatrizLatProf />
          <div className="mt-12">
            <MapaMundial />
          </div>
        </Seccion>

        {/* ── 2 ─────────────────────────────────────────────────── */}
        <Seccion
          n={tx({ es: "02 · La firma de la pared", en: "02 · The wall signature" })}
          titulo={tx({
            es: "El caparazón como semáforo de metano",
            en: "The shell as a methane signal",
          })}
          entradilla={tx({
            es: "Los foraminíferos aglutinados construyen su caparazón pegando granos del sedimento; los calcáreos lo segregan. En las filtraciones los aglutinados desaparecen, porque toleran mal el metano y el sulfuro de hidrógeno. La proporción entre unos y otros es, por eso, una de las señales más fiables.",
            en: "Agglutinated foraminifera build their shell by cementing sediment grains; calcareous ones secrete it. At seeps the agglutinated forms vanish, tolerating methane and hydrogen sulphide poorly. The ratio between them is therefore one of the most reliable signals.",
          })}
        >
          <ParedPorBanda />
        </Seccion>

        {/* ── 3 ─────────────────────────────────────────────────── */}
        <Seccion
          n={tx({ es: "03 · La muestra", en: "03 · The sample" })}
          titulo={tx({
            es: "Qué hay dentro de MSH-BC-21",
            en: "What is inside MSH-BC-21",
          })}
          entradilla={tx({
            es: "Un testigo de caja de la plataforma externa frente al Golfo de Morrosquillo, en un pockmark con señales acústicas de escape de gas entre 50 y 75 metros. Se procesaron sus dos centímetros superficiales.",
            en: "A box core from the outer shelf off the Gulf of Morrosquillo, on a pockmark with acoustic gas-escape signals between 50 and 75 metres. Its two surface centimetres were processed.",
          })}
        >
          <Composicion />
          <div className="mt-14">
            <Testigo />
          </div>
        </Seccion>

        {/* ── 4 ─────────────────────────────────────────────────── */}
        <Seccion
          n={tx({ es: "04 · El veredicto", en: "04 · The verdict" })}
          titulo={tx({
            es: "¿Qué tan filtración parece esta muestra?",
            en: "How much does this sample look like a seep?",
          })}
          entradilla={tx({
            es: "Cuatro criterios que la literatura propone para reconocer una filtración, contrastados con lo que la muestra realmente mide. Durante dos años el cuarto pareció una contradicción.",
            en: "Four criteria the literature proposes for recognising a seep, contrasted with what the sample actually measures. For two years the fourth looked like a contradiction.",
          })}
        >
          <Veredicto />
        </Seccion>

        {/* ── 4 bis ─────────────────────────────────────────────── */}
        <Seccion
          n={tx({ es: "05 · La continuación", en: "05 · The continuation" })}
          titulo={tx({
            es: "El mismo campo, dos años después",
            en: "The same field, two years later",
          })}
          entradilla={tx({
            es: "En 2024, el mismo proyecto y la misma directora publicaron un estudio de 18 estaciones en este campo de filtración. Es la línea base local que a la tesis le faltaba: resuelve la duda sobre la diversidad y aporta los primeros isótopos del área.",
            en: "In 2024, the same project and the same advisor published a study of 18 stations in this seep field. It is the local baseline the thesis lacked: it settles the diversity question and supplies the first isotopes for the area.",
          })}
        >
          <Sinu />
        </Seccion>

        {/* ── 5 ─────────────────────────────────────────────────── */}
        <Seccion
          n={tx({ es: "06 · El catálogo", en: "06 · The catalogue" })}
          titulo={tx({
            es: "Qué se ha reportado en las filtraciones del mundo",
            en: "What has been reported at the world's seeps",
          })}
          entradilla={
            <>
              {tx({
                es: "La base original de la tesis recogía las cinco especies principales de cada filtro. Al leer los artículos completos aparecen ",
                en: "The thesis base collected the top five species per filter. Reading the full articles brings up ",
              })}
              <strong className="font-semibold text-(--ink)">
                {completo.resumen.taxones_validados}{" "}
                {tx({ es: "taxones", en: "taxa" })}
              </strong>
              {tx({
                es: ". El más reportado del mundo sigue siendo ",
                en: ". The most reported worldwide is still ",
              })}
              <Taxon nombre="Uvigerina peregrina" />
              {tx({ es: ", ahora en 22 estudios.", en: ", now in 22 studies." })}
            </>
          }
        >
          <Explorador />
        </Seccion>

        {/* ── cierre ───────────────────────────────────────────── */}
        <Seccion
          n={tx({ es: "07 · Límites", en: "07 · Limits" })}
          titulo={tx({
            es: "Lo que estos datos no pueden decir",
            en: "What these data cannot tell us",
          })}
        >
          <ul className="max-w-[64ch] space-y-3 text-[0.95rem] leading-relaxed text-(--ink-2)">
            {[
              tx({
                es: "Una sola muestra. MSH-BC-21 es un testigo, sin réplicas y sin sitios de control propios. El estudio de 2024 en el mismo campo aporta las 18 estaciones que faltaban.",
                en: "A single sample. MSH-BC-21 is one core, with no replicates and no control sites of its own. The 2024 study in the same field supplies the 18 stations that were missing.",
              }),
              tx({
                es: "Sin isótopos propios. La tesis no midió δ13C, que es la evidencia geoquímica directa de carbono derivado del metano. Los primeros valores para el área son los de Barragán y Bernal (2024).",
                en: "No isotopes of its own. The thesis did not measure δ13C, the direct geochemical evidence of methane-derived carbon. The first values for the area are those of Barragán and Bernal (2024).",
              }),
              tx({
                es: "El registro mundial está sesgado. El 80% procede de más de 500 metros y tres de las cuatro bandas latitudinales no tienen ni un dato somero. Comparar una plataforma tropical con filtraciones profundas de latitudes altas tiene un límite.",
                en: "The global record is biased. 80% comes from below 500 metres and three of the four latitude bands have no shallow data at all. Comparing a tropical shelf against deep high-latitude seeps has a limit.",
              }),
              tx({
                es: "Presencia no es abundancia. Del texto de los artículos se puede extraer qué taxones aparecen, no cuánto pesa cada uno. Sólo se marca dominancia cuando el propio artículo la afirma.",
                en: "Presence is not abundance. From the article text one can extract which taxa appear, not how much each weighs. Dominance is marked only when the article itself states it.",
              }),
            ].map((s, i) => (
              <li key={i} className="flex gap-3">
                <span className="mt-[9px] h-1 w-1 shrink-0 rounded-full bg-(--muted)" />
                <span>{s}</span>
              </li>
            ))}
          </ul>

          <div className="mt-10 border-t border-(--border) pt-8">
            <h3 className="mb-3 text-[1rem] font-semibold">
              {tx({ es: "Trazabilidad", en: "Traceability" })}
            </h3>
            <p className="mb-4 max-w-[64ch] text-[0.9rem] leading-relaxed text-(--ink-2)">
              {tx({
                es:
                  "Todo lo que se corrigió respecto de los archivos originales está registrado: " +
                  correcciones.correcciones.length +
                  " entradas con su motivo y su fuente. Incluye erratas, actualizaciones taxonómicas de WoRMS posteriores a 2022, filas duplicadas y reclasificaciones de tipo de pared.",
                en:
                  "Everything corrected from the original files is on record: " +
                  correcciones.correcciones.length +
                  " entries with their reason and source. It covers typos, WoRMS taxonomic updates issued after 2022, duplicate rows and wall-type reclassifications.",
              })}
            </p>
            <Referencias />
          </div>
        </Seccion>

        {/* ── 08 ────────────────────────────────────────────────── */}
        <Seccion
          n={tx({ es: "08 · Cuenta", en: "08 · Account" })}
          titulo={tx({ es: "Cambiar la contraseña", en: "Change the password" })}
          entradilla={tx({
            es: "El acceso es restringido porque los datos primarios del proyecto son inéditos. Desde aquí se rota la contraseña sin pasar por el panel de Vercel ni volver a desplegar. Hace falta además la respuesta a la pregunta de seguridad: así se puede compartir el acceso para que alguien lo vea, sin que pueda cambiar la clave.",
            en: "Access is restricted because the project's primary data are unpublished. From here the password is rotated without going through the Vercel dashboard or redeploying. The answer to the security question is also required: that way access can be shared for someone to look around, without letting them change the password.",
          })}
        >
          <Cuenta />
        </Seccion>

        <footer className="border-t border-(--border) pt-8 text-[0.8rem] leading-relaxed text-(--muted)">
          <p className="mb-5 max-w-[64ch]">
            {tx({ es: "A partir de la tesis de grado de ", en: "Based on the undergraduate thesis of " })}
            <strong className="font-semibold text-(--ink-2)">
              Erick Francisco Mendoza Rivero
            </strong>
            {tx({
              es: ", Ingeniero Geólogo, «Análisis de las asociaciones de foraminíferos bentónicos en filtraciones de metano: comparación entre distintas localidades y la plataforma continental del Caribe colombiano». Trabajo de grado presentado como requisito parcial para optar al título de Ingeniero Geólogo. Universidad Nacional de Colombia, sede Medellín, Facultad de Minas, Departamento de Geociencias y Medio Ambiente, 2022. Directora: Ph.D. Gladys Rocío Bernal Franco.",
              en: ", Geological Engineer, “Analysis of benthic foraminiferal assemblages at methane seeps: a comparison between localities and the Colombian Caribbean continental shelf”. Undergraduate thesis submitted in partial fulfilment of the requirements for the degree of Geological Engineer. Universidad Nacional de Colombia, Medellín campus, Facultad de Minas, Department of Geosciences and Environment, 2022. Advisor: Ph.D. Gladys Rocío Bernal Franco.",
            })}
          </p>

          {/* Ficha del proyecto. Va completa y con los identificadores
              oficiales porque un dashboard que publica datos de investigación
              financiada tiene que dejar rastro de quién la financió y bajo qué
              convenio. Tomada del informe técnico final de la beca-pasantía. */}
          <div className="mb-5 max-w-[64ch] border-l-2 border-(--axis) pl-4">
            <p className="mb-2 font-semibold text-(--ink-2)">
              {tx({ es: "Marco del proyecto", en: "Project framework" })}
            </p>
            <dl className="space-y-1.5">
              {[
                {
                  k: tx({ es: "Proyecto", en: "Project" }),
                  v: "Methane seep hunting: A multi-scale and multi method approach",
                },
                {
                  k: tx({ es: "Objetivo general", en: "General objective" }),
                  v: tx({
                    es: "Proponer un enfoque de múltiples escalas y métodos para detectar rezumaderos de metano, determinar su actividad de filtración actual e identificar su fuente, utilizando tecnología de punta en el Caribe colombiano.",
                    en: "To propose a multi-scale, multi-method approach to detect methane seeps, determine their present seepage activity and identify their source, using state-of-the-art technology in the Colombian Caribbean.",
                  }),
                },
                {
                  k: tx({ es: "Programa CTeI", en: "STI programme" }),
                  v: tx({
                    es: "Programa Nacional de Ciencia, Tecnología e Innovación en Geociencias — Minciencias",
                    en: "National Programme for Science, Technology and Innovation in Geosciences — Minciencias",
                  }),
                },
                {
                  k: tx({ es: "Convocatoria", en: "Call" }),
                  v: tx({
                    es: "877-2020 — Financiación de proyectos de investigación en geociencias para el sector de hidrocarburos",
                    en: "877-2020 — Funding of geoscience research projects for the hydrocarbon sector",
                  }),
                },
                {
                  k: tx({
                    es: "Contrato / convenio",
                    en: "Contract / agreement",
                  }),
                  v: tx({
                    es: "80740-143-2021 (Minciencias — Entidad)",
                    en: "80740-143-2021 (Minciencias — Institution)",
                  }),
                },
                {
                  k: tx({ es: "Grupo de investigación", en: "Research group" }),
                  v: "OCEÁNICOS — Universidad Nacional de Colombia, sede Medellín",
                },
                {
                  k: tx({ es: "Entidades", en: "Institutions" }),
                  v: tx({
                    es: "UPB · UNAL · GMAS · GEOMARES · ACGGP (ejecutoras y beneficiarias)",
                    en: "UPB · UNAL · GMAS · GEOMARES · ACGGP (executing and beneficiary)",
                  }),
                },
                {
                  k: tx({ es: "Vinculación", en: "Appointment" }),
                  v: tx({
                    es: "Beca-pasantía del programa Jóvenes Investigadores, 21-08-2021 a 31-03-2024. Tutora: Gladys Rocío Bernal Franco.",
                    en: "Young Researchers scholarship-internship, 21 Aug 2021 to 31 Mar 2024. Tutor: Gladys Rocío Bernal Franco.",
                  }),
                },
              ].map((d) => (
                <div key={d.k} className="sm:flex sm:gap-3">
                  <dt className="shrink-0 font-medium sm:w-[9.5rem]">{d.k}</dt>
                  <dd className="m-0">{d.v}</dd>
                </div>
              ))}
            </dl>
          </div>

          <p className="max-w-[64ch]">
            {tx({
              es: "Taxonomía verificada contra WoRMS (World Foraminifera Database). Referencias resueltas con CrossRef. Los datos primarios del proyecto son inéditos y no se publican: aquí sólo se muestran agregados y tablas derivadas.",
              en: "Taxonomy verified against WoRMS (World Foraminifera Database). References resolved with CrossRef. The project's primary data are unpublished and not released: only aggregates and derived tables are shown here.",
            })}
          </p>
        </footer>
      </main>
    </>
  );
}
