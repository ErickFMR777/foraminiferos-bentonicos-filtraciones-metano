"""
30_informe.py — Informe en PDF de todo el proceso de curación de datos.

Documento de trazabilidad: qué se hizo con los datos de la tesis, qué se
corrigió, qué se excluyó y por qué. Pensado para acompañar al dashboard y
para que un tercero pueda auditar las decisiones sin leer el código.

Salida -> Informe_curacion_datos.pdf (raíz del proyecto)

El PDF NO contiene datos primarios inéditos: sólo agregados, recuentos y las
decisiones de curación. Puede compartirse.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
DERIV = ROOT / "data" / "derived"
PRIV = ROOT / "data" / "private"
SALIDA = ROOT / "Informe_curacion_datos.pdf"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TINTA = (20, 20, 15)
SUAVE = (90, 88, 84)
LINEA = (200, 197, 190)
ACENTO = (42, 120, 214)


class Informe(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("D", "", 7.5)
        self.set_text_color(*SUAVE)
        self.cell(0, 6, "Foraminíferos y filtraciones de metano — informe de curación",
                  align="L")
        self.ln(7)
        self.set_draw_color(*LINEA)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("D", "", 7.5)
        self.set_text_color(*SUAVE)
        self.cell(0, 6, f"{self.page_no()}", align="C")

    # --- bloques ---
    def h1(self, t: str) -> None:
        self.ln(3)
        self.set_font("D", "B", 14)
        self.set_text_color(*TINTA)
        self.multi_cell(0, 7, t)
        self.ln(1.5)

    def h2(self, t: str) -> None:
        self.ln(2.5)
        self.set_font("D", "B", 10.5)
        self.set_text_color(*TINTA)
        self.multi_cell(0, 5.5, t)
        self.ln(1)

    def p(self, t: str, sangria: float = 0) -> None:
        self.set_font("D", "", 9.5)
        self.set_text_color(*TINTA)
        if sangria:
            self.set_x(self.l_margin + sangria)
        self.multi_cell(0 if not sangria else self.w - self.r_margin - self.x, 5, t)
        self.ln(1.2)

    def nota(self, t: str) -> None:
        self.set_font("D", "I", 8.5)
        self.set_text_color(*SUAVE)
        self.multi_cell(0, 4.4, t)
        self.ln(1.2)

    def item(self, t: str) -> None:
        self.set_font("D", "", 9.5)
        self.set_text_color(*TINTA)
        x = self.get_x()
        self.cell(4, 5, "·")
        self.multi_cell(self.w - self.r_margin - x - 4, 5, t)
        self.ln(0.6)

    def tabla(self, filas: list[tuple], anchos: list[float], cab: bool = True) -> None:
        self.set_font("D", "", 8.6)
        for i, fila in enumerate(filas):
            if self.get_y() > self.h - 28:
                self.add_page()
            neg = cab and i == 0
            self.set_font("D", "B" if neg else "", 8.6)
            self.set_text_color(*(TINTA if neg else SUAVE if i else TINTA))
            alto = 5.4
            y0 = self.get_y()
            for w, celda in zip(anchos, fila):
                self.set_xy(self.l_margin + sum(anchos[:anchos.index(w)]) if False else self.get_x(), y0)
                self.cell(w, alto, str(celda)[:int(w / 1.75)], align="L")
            self.ln(alto)
            if neg:
                self.set_draw_color(*LINEA)
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
                self.ln(1)
        self.ln(2)


def cargar():
    j = lambda n: json.loads((DERIV / n).read_text(encoding="utf-8"))  # noqa: E731
    corr = j("correcciones.json")
    return dict(
        corr=corr["correcciones"], resumen=corr["resumen"],
        est=j("estudios.json"), tax=j("taxones_global.json"),
        mat=j("matriz_lat_prof.json"), msh=j("msh_bc21.json"),
        sol=j("solape.json"),
        manif=json.loads((PRIV / "manifiesto_pdfs.json").read_text(encoding="utf-8"))
        if (PRIV / "manifiesto_pdfs.json").exists() else [],
    )


def main() -> int:
    d = cargar()
    pdf = Informe(format="A4")
    pdf.set_auto_page_break(True, margin=20)
    pdf.set_margins(22, 18, 22)

    fuentes = Path("C:/Windows/Fonts")
    pdf.add_font("D", "", str(fuentes / "arial.ttf"))
    pdf.add_font("D", "B", str(fuentes / "arialbd.ttf"))
    pdf.add_font("D", "I", str(fuentes / "ariali.ttf"))

    # ---------------------------------------------------------- portada
    pdf.add_page()
    pdf.ln(38)
    pdf.set_font("D", "B", 21)
    pdf.set_text_color(*TINTA)
    pdf.multi_cell(0, 9.5, "Foraminíferos bentónicos\ny filtraciones de metano")
    pdf.ln(3)
    pdf.set_font("D", "", 12.5)
    pdf.set_text_color(*SUAVE)
    pdf.multi_cell(0, 6, "Informe de curación de datos para el dashboard interactivo")
    pdf.ln(9)
    pdf.set_draw_color(*ACENTO)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 42, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(9)
    pdf.set_font("D", "", 10)
    pdf.set_text_color(*TINTA)
    pdf.multi_cell(0, 5.4,
        "A partir de la tesis de grado de Erick Francisco Mendoza Rivero\n"
        "«Análisis de las asociaciones de foraminíferos bentónicos en filtraciones\n"
        "de metano: comparación entre distintas localidades y la plataforma\n"
        "continental del Caribe colombiano»\n\n"
        "Universidad Nacional de Colombia, Facultad de Minas, 2022\n"
        "Directora: Ph.D. Gladys Rocío Bernal Franco\n"
        "Proyecto Methane Seep Hunting (MSH)")
    pdf.ln(14)
    pdf.set_font("D", "", 8.6)
    pdf.set_text_color(*SUAVE)
    pdf.multi_cell(0, 4.6,
        f"Documento generado automáticamente el {date.today():%d/%m/%Y} por el "
        "pipeline de datos del proyecto.\nRefleja el estado exacto de "
        "data/derived/ en esa fecha.\n\n"
        "Este informe no contiene datos primarios inéditos: sólo agregados, "
        "recuentos y decisiones de curación.")

    # ---------------------------------------------------------- 1
    pdf.add_page()
    pdf.h1("1. Qué documenta este informe")
    pdf.p("La tesis de 2022 se apoya en dos libros de Excel: una base bibliográfica "
          "que compila las asociaciones de foraminíferos reportadas en filtraciones "
          "de metano de todo el mundo, y el conteo de una muestra propia del Caribe "
          "colombiano (MSH-BC-21). Para convertir eso en un dashboard hubo que "
          "sanear, verificar y completar los datos.")
    pdf.p("Aquí queda registrado todo lo que se cambió respecto de los archivos "
          "originales, con su motivo. El objetivo no es disimular los errores del "
          "trabajo original sino dejar la trazabilidad a la vista: cualquiera "
          "debería poder reconstruir la distancia entre el manuscrito y los datos "
          "que alimentan el dashboard.")

    pdf.h2("Fuentes")
    pdf.p("Mendoza Rivero, E. F. (2022). Análisis de las asociaciones de "
          "foraminíferos bentónicos en filtraciones de metano: comparación entre "
          "distintas localidades y la plataforma continental del Caribe colombiano. "
          "Tesis de grado, Ingeniería Geológica, Universidad Nacional de Colombia, "
          "Facultad de Minas, Medellín. Directora: Ph.D. Gladys Rocío Bernal "
          "Franco. 62 pp.")
    pdf.p("Con sus dos anexos de datos:")
    pdf.item("«BD FORAMS AMBTE FILTRACION-filtros» — 9 hojas. Base bibliográfica "
             "de 38 estudios; la hoja maestra tiene 293 filas.")
    pdf.item("«Colección - Clasificación - Conteo MSH-BC-21» — 3 hojas. Conteo de "
             "52 especies de los 2 cm superficiales de un testigo de caja.")
    pdf.p(f"A esto se suman {len(d['manif'])} artículos científicos reunidos "
          "posteriormente para verificar localidades, morfología del fondo marino "
          "y tipo de fluido. Se listan en el apartado 7.")
    pdf.nota("La tesis y sus dos anexos de datos se citan pero no se publican: "
             "contienen datos primarios inéditos del proyecto MSH, previos a su "
             "publicación académica.")

    pdf.h2("Autoridades externas consultadas")
    pdf.item("WoRMS / World Foraminifera Database — resolución taxonómica de los "
             "211 nombres de especie. La propia tesis recomienda esta autoridad "
             "en sus conclusiones.")
    pdf.item("CrossRef — resolución bibliográfica de los estudios (autores, año, "
             "revista, DOI).")

    # ---------------------------------------------------------- 2
    pdf.add_page()
    pdf.h1("2. Correcciones aplicadas")
    tipos = Counter(c["tipo"] for c in d["corr"])
    ERR = {"errata", "reclasificacion_pared", "duplicado"}
    n_err = sum(c["registros_afectados"] for c in d["corr"] if c["tipo"] in ERR)

    pdf.p(f"El registro tiene {len(d['corr'])} entradas. Conviene distinguirlas: "
          "sólo una parte son errores del manuscrito.")

    ETIQ = {
        "normalizacion": "Normalización de nomenclatura abierta",
        "actualizacion": "Actualización taxonómica de WoRMS",
        "errata": "Errata del manuscrito",
        "reclasificacion_pared": "Tipo de pared mal asignado",
        "duplicado": "Fila duplicada",
        "exclusion": "Registro excluido",
        "exclusion_confirmada": "Exclusión del autor, confirmada",
        "sin_verificar": "Taxón no verificable",
        "aritmetica": "Inconsistencia aritmética",
        "recuperacion": "Estudio reincorporado",
    }
    filas = [("Tipo", "Entradas", "Registros")]
    for t, n in tipos.most_common():
        regs = sum(c["registros_afectados"] for c in d["corr"] if c["tipo"] == t)
        filas.append((ETIQ.get(t, t), str(n), str(regs)))
    pdf.tabla(filas, [104, 26, 30])

    pct = f"{100 * n_err / 293:.1f}".replace(".", ",")
    pdf.p(f"Errores reales del manuscrito: {sum(tipos[t] for t in ERR)} entradas que "
          f"afectan a {n_err} de los 293 registros originales, un {pct} %. Es una "
          "tasa baja para una compilación hecha a mano. El resto del registro no "
          "son errores del autor: nomenclatura abierta, cambios que WoRMS "
          "introdujo después de 2022 y notas aritméticas.")

    pdf.h2("Las correcciones de más impacto")
    pdf.p("Cibicidoides wuellerstorfi, Cibicides wuellerstorfi y Planulina "
          "wüllerstorfi son la misma especie. WoRMS la llama hoy Lobatula "
          "wuellerstorfi, tras el trabajo de ADN de Schweizer et al. (2009). "
          "Unificadas suman 11 registros en 10 estudios y pasa a ser el segundo "
          "taxón más reportado del mundo. Corrige el orden de la Tabla 1 de la "
          "tesis y refuerza su argumento.")
    pdf.p("Ammodiscus estaba clasificado como calcáreo porcelanáceo; es un género "
          "aglutinado. La proporción de formas calcáreas frente a aglutinadas en "
          "MSH-BC-21 pasa de 88,8 % a 87,0 %. El texto de la tesis dice «cerca de "
          "un 80 %», que no coincide con ninguno de los dos valores; se publica el "
          "calculado.")
    pdf.p("Cassidulina es un homónimo: existe también como género de equinoideo, y "
          "la consulta automática a WoRMS devolvía el erizo de mar. El pipeline "
          "filtra por phylum para evitarlo.")
    pdf.p("Doce filas estaban repetidas de forma exacta —mismo estudio, taxón, "
          "banda latitudinal, profundidad y microhábitat— e inflaban el recuento. "
          "Se eliminaron. En cambio se conservaron las 14 repeticiones en las que "
          "cambia la banda: ahí el artículo reporta la especie en dos estratos "
          "distintos y son observaciones separadas.")
    pdf.p("Cinco especies planctónicas figuraban en una base declarada de "
          "foraminíferos bentónicos y se excluyeron.")

    # ---------------------------------------------------------- 3
    pdf.add_page()
    pdf.h1("3. Exclusiones y reincorporaciones")
    pdf.p("El filtrado original descartó seis de los 44 estudios del libro borrador. "
          "Revisadas sus condiciones contra el criterio que declara la propia "
          "metodología de la tesis —condiciones oceánicas actuales y foraminíferos "
          "recientes superficiales—, cuatro exclusiones son correctas y dos "
          "resultaron discutibles.")

    pdf.h2("Se reincorporan")
    for c in d["corr"]:
        if c["tipo"] == "recuperacion":
            pdf.p(c["desde"], sangria=0)
            pdf.nota(c["motivo"])

    pdf.h2("Se mantienen fuera")
    for c in d["corr"]:
        if c["tipo"] == "exclusion_confirmada":
            pdf.p(c["desde"][:78], sangria=0)
            pdf.nota(c["motivo"])

    pdf.h2("Un estudio que no era de filtraciones")
    pdf.p("McCorkle et al. (1990) figuraba en la base con 18 registros. La lectura "
          "del artículo confirma que no estudia filtraciones: son testigos de caja "
          "en márgenes continentales normales del Atlántico y el Pacífico, y el "
          "gradiente δ13C que documenta entre taxones infaunales y epifaunales es "
          "la línea base frente a la que se mide una señal de metano, no la señal.")
    pdf.p("La consecuencia es grande: ocho de sus registros caían en la banda "
          "tropical 0-15°, que sin ellos queda sostenida por un único registro de "
          "un único estudio. El vacío que la tesis intuía es más extremo de lo que "
          "su propia base dejaba ver.")

    # ---------------------------------------------------------- 4
    pdf.add_page()
    pdf.h1("4. Información añadida")
    pdf.h2("Georreferenciación")
    geo = sum(1 for e in d["est"] if e["lat"] is not None)
    pdf.p(f"La base original no tenía campo de localidad, pese a que la metodología "
          f"menciona quince. Se reconstruyeron {geo} de {len(d['est'])} a partir de "
          "los títulos, los resúmenes de CrossRef, los artículos completos y datos "
          "aportados por el autor. Las coordenadas son la posición representativa "
          "de la localidad nombrada, no la del testigo, y cada una lleva su nivel "
          "de confianza y su fuente.")
    pdf.p("Una comprobación cruzada verifica que la coordenada de cada estudio cae "
          "dentro de una banda latitudinal que sus propios registros declaran. "
          "Pasa en todos, lo que valida a la vez las coordenadas nuevas y las "
          "bandas asignadas a mano en la hoja original.")

    pdf.h2("Tipología en dos ejes")
    pdf.p("Se separó lo que estaba mezclado en un solo campo: la naturaleza del "
          "fluido y la expresión geomorfológica del escape. Un pockmark puede ser "
          "frío o termogénico, y un volcán de lodo puede expulsar metano biogénico "
          "o termogénico; mezclarlos impedía filtrar por cualquiera de los dos.")
    fl = Counter(e["tipo_filtracion"] for e in d["est"])
    mo = Counter(e["morfologia"] or "sin determinar" for e in d["est"])
    pdf.tabla([("Fluido", "n")] + [(k, str(v)) for k, v in fl.most_common()], [104, 26])
    pdf.tabla([("Morfología", "n")] + [(k, str(v)) for k, v in mo.most_common()], [104, 26])
    pdf.nota("Sólo se asigna un valor cuando el título o el artículo lo declaran. "
             "Donde habría que adivinar se deja sin determinar: inventar una "
             "morfología sería peor que admitir que falta.")

    pdf.h2("Microhábitat")
    pdf.p("La columna «Discriminación adicional» del libro borrador se había "
          "perdido en la hoja filtrada. Se recuperó y se normalizó a vocabulario "
          "controlado: biocenosis, tanatocenosis, infaunal, epifaunal, banco de "
          "bivalvos y tapete bacteriano.")

    pdf.h2("Fauna de referencia del Caribe")
    pdf.p("Los porcentajes de las localidades caribeñas citadas en el capítulo 4.2 "
          "de la tesis —Salmedina, Cispatá, Urabá, Islas del Rosario— sólo existían "
          "en prosa. Se estructuraron por primera vez para poder contrastarlos con "
          "MSH-BC-21.")

    # ---------------------------------------------------------- 5
    pdf.add_page()
    pdf.h1("5. Estado de los datos")
    m = d["mat"]
    tot = sum(c["registros"] for c in m["celdas"])
    p500 = sum(c["registros"] for c in m["celdas"] if c["prof"] == "> 500 m")
    filas = [("Indicador", "Valor")]
    filas += [
        ("Estudios en la base", str(len(d["est"]))),
        ("Registros (base curada, sólo filtraciones)", str(tot)),
        ("Registros (base ampliada)", str(m["n_ampliada"])),
        ("Taxones", str(len(d["tax"]))),
        ("Celdas con datos de las 12 posibles",
         str(sum(1 for c in m["celdas"] if c["registros"]))),
        ("Registros procedentes de más de 500 m", f"{100 * p500 / tot:.0f} %"),
        ("MSH-BC-21: riqueza específica", str(d["msh"]["indices"]["riqueza_S"])),
        ("MSH-BC-21: Shannon H'", f"{d['msh']['indices']['shannon_H']:.4f}".replace(".", ",")),
        ("MSH-BC-21: equidad de Pielou J'", f"{d['msh']['indices']['equidad_J']:.4f}".replace(".", ",")),
        ("MSH-BC-21: calcáreos / aglutinados",
         f"{d['msh']['pared']['Calcareo']:.1f} % / {d['msh']['pared']['Aglutinado']:.1f} %".replace(".", ",")),
        ("Especies compartidas con la literatura",
         f"{d['sol']['especies']['n_compartidas']} de {d['sol']['especies']['n_msh']}"),
        ("Abundancia en géneros ya reportados en filtraciones",
         f"{d['sol']['generos']['pct_abundancia_compartida']:.1f} %".replace(".", ",")),
    ]
    pdf.tabla(filas, [118, 42])

    pdf.h2("El vacío tropical somero")
    pdf.p("La celda que cruza la banda 0-15° de latitud con profundidades menores "
          "de 150 metros —donde se sitúa la muestra del Caribe colombiano— no tiene "
          "ningún registro. Sigue vacía incluso al ampliar la base con los estudios "
          "reincorporados, lo que indica que el vacío es real y no un artefacto de "
          "la curación.")

    pdf.h2("Alcance de la extracción original")
    pdf.p("La metodología de la tesis recoge «las 5 principales especies» de cada "
          "filtro. La base es por tanto una muestra de las especies dominantes, no "
          "de las asociaciones completas: Lobegeier y Sen Gupta (2008) reportan 183 "
          "especies y la base tomó 18 registros de ese artículo. Es coherente con "
          "lo declarado, pero conviene tenerlo presente al leer los análisis de "
          "similitud y de solape.")

    # ---------------------------------------------------------- 6
    pdf.add_page()
    pdf.h1("6. Verificación")
    pdf.p("El pipeline incluye una auditoría independiente que vuelve a leer los "
          "Excel originales en lugar de fiarse de sus propias salidas. Comprueba "
          "la conservación de registros a través de cada etapa, que toda "
          "diferencia respecto del original esté documentada, la aritmética de los "
          "índices recalculada desde cero, la coherencia entre los conjuntos de "
          "datos publicados, la validez de los campos que alimentan los gráficos y "
          "que ningún archivo público filtre rutas o nombres de los documentos "
          "originales.")
    pdf.p("Una segunda comprobación verifica que cada PDF archivado contiene lo que "
          "su nombre indica, y detecta duplicados por contenido y por DOI. Existe "
          "porque el emparejador falló una vez de forma silenciosa: buscaba la "
          "firma del título en las tres primeras páginas y capturó una cita de la "
          "bibliografía, de modo que un resumen de Panieri (2000) quedó archivado "
          "con el nombre de Sen Gupta y Aharon (1994), a quien sólo citaba.")

    pdf.h2("Confidencialidad")
    pdf.p("Los documentos originales —la tesis y los dos libros de Excel— no se "
          "publican ni se versionan: contienen datos primarios inéditos del "
          "proyecto MSH. El repositorio sólo incluye el código del pipeline y los "
          "agregados derivados. Las referencias bibliográficas sí se publican, por "
          "decisión expresa del autor.")

    pdf.h2("Pendiente")
    sin_doi = [e for e in d["est"] if not e.get("doi")]
    for e in sin_doi:
        pdf.item(f"Referencia no localizada: «{e['titulo'][:70]}» "
                 f"({e['n_registros']} registros). No aparece en CrossRef ni en "
                 "búsqueda web.")
    pend = [m for m in d["manif"] if m["estado"] == "pendiente de integrar"]
    for m_ in pend:
        pdf.item(f"Pendiente de integrar: {m_['despues'][:72]}")

    # ---------------------------------------------------------- 7
    pdf.add_page()
    pdf.h1("7. Estudios que componen la base")
    pdf.p("Las 40 referencias, ordenadas por el número de registros que aportan. "
          "Se indica la localidad reconstruida y el tipo de fluido. Los marcados "
          "con «R» son los dos reincorporados en esta revisión; el marcado con «X» "
          "es el que no documenta filtraciones.")

    FL = {"frio": "frío", "termogenico": "termogénico", "biogenico": "biogénico",
          "hidrotermal": "hidrotermal", "mixto": "mixto",
          "no_filtracion": "no es filtración"}
    for e in sorted(d["est"], key=lambda x: -x["n_registros"]):
        if pdf.get_y() > pdf.h - 40:
            pdf.add_page()
        marca = "R " if e.get("recuperado") else ("X " if not e["es_filtracion"] else "")
        aut = ", ".join((e.get("autores") or [])[:3]) or "(autoría sin resolver)"
        if len(e.get("autores") or []) > 3:
            aut += " et al."
        def linea(texto: str, negrita: bool = False, color=SUAVE, alto: float = 4.4):
            # multi_cell deja el cursor al margen derecho; hay que devolverlo
            pdf.set_x(pdf.l_margin)
            pdf.set_font("D", "B" if negrita else "", 9 if negrita else 8.8)
            pdf.set_text_color(*color)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, alto, texto)

        linea(f"{marca}[{e['n_registros']}] {aut} ({e.get('anio') or 's.f.'})",
              negrita=True, color=TINTA, alto=4.8)
        linea(e["titulo"][:150])
        detalle = e.get("revista") or ""
        if e.get("doi"):
            detalle += ("  ·  " if detalle else "") + f"doi:{e['doi']}"
        if detalle:
            linea(detalle)
        loc = e.get("localidad") or "localidad sin determinar"
        linea(f"{loc}  ·  {FL.get(e['tipo_filtracion'], e['tipo_filtracion'])}"
              + (f"  ·  {e['morfologia_label']}" if e.get("morfologia_label") else ""))
        pdf.ln(2.2)

    pdf.output(str(SALIDA))
    print(f"Informe generado: {SALIDA}")
    print(f"  {SALIDA.stat().st_size / 1024:.0f} KB, {pdf.page_no()} páginas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
