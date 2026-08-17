import MatrizLatProf from "@/components/MatrizLatProf";
import msh from "@datos/msh_bc21.json";
import taxones from "@datos/taxones_global.json";
import estudios from "@datos/estudios.json";

export default function Home() {
  return (
    <main className="mx-auto max-w-[68rem] px-6 py-16 md:py-24">
      <header className="mb-16 max-w-[52rem]">
        <p className="mb-4 text-[0.75rem] uppercase tracking-[0.14em] text-(--muted)">
          Universidad Nacional de Colombia · Proyecto MSH
        </p>
        <h1 className="mb-5 text-[2.4rem] leading-[1.12] md:text-[3rem]">
          Foraminíferos y metano en el Caribe colombiano
        </h1>
        <p className="max-w-[58ch] text-[1.05rem] leading-relaxed text-(--ink-2)">
          Protistas de menos de un milímetro que construyen un caparazón y
          registran en él las condiciones del fondo marino. Este trabajo
          contrasta lo que la literatura mundial ha publicado sobre ellos en
          filtraciones de metano con una muestra de la plataforma continental
          frente al Golfo de Morrosquillo.
        </p>
      </header>

      <section className="mb-16 grid grid-cols-2 gap-x-8 gap-y-7 border-y border-(--border) py-8 md:grid-cols-4">
        {[
          { cifra: estudios.length, etiqueta: "estudios revisados" },
          { cifra: taxones.length, etiqueta: "taxones registrados" },
          { cifra: msh.indices.riqueza_S, etiqueta: "especies en MSH-BC-21" },
          { cifra: 0, etiqueta: "estudios previos en estas condiciones" },
        ].map((d) => (
          <div key={d.etiqueta}>
            <div className="text-[2.6rem] font-semibold leading-none">
              {d.cifra}
            </div>
            <div className="mt-2 text-[0.82rem] leading-snug text-(--muted)">
              {d.etiqueta}
            </div>
          </div>
        ))}
      </section>

      <MatrizLatProf />
    </main>
  );
}
