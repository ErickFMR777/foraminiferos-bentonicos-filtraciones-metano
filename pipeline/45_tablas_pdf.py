"""
45_tablas_pdf.py — Extrae de las TABLAS lo que 40_taxones_pdf.py no puede leer:
valores de δ13C y δ18O por taxón, índices de diversidad y abundancias relativas.

POR QUÉ HACE FALTA OTRA HERRAMIENTA. `pypdf` devuelve el texto en orden de
lectura y una tabla se convierte en una ristra de números sin columnas. Aquí se
usa `pdfplumber`, que da la POSICIÓN de cada palabra: agrupando por coordenada
vertical se recupera la fila, que es la unidad que asocia un taxón con sus
cifras.

Lo que NO se hace, y es deliberado: reconstruir las tablas de forma genérica.
Se probó y en artículos a dos columnas produce basura — mezcla el cuerpo del
texto con la tabla. En su lugar se buscan FILAS ENCABEZADAS POR UN TAXÓN ya
validado contra WoRMS, y cada cifra se acepta sólo si cae en el rango físico de
su variable.

LA TRAMPA DEL POR MIL. En varios artículos el símbolo ‰ de los valores
isotópicos sale del PDF convertido en «%», de modo que «1,26 ± 0,15 %» es un
δ13C y no una abundancia relativa. Por eso una abundancia sólo se acepta cuando
el encabezado o el pie de la tabla dice explícitamente «%» o «relative
abundance», y nunca en una página cuyo pie anuncia isótopos.

Salidas:
  data/private/tablas_pdf.json   — todo, con la fila literal como evidencia
  data/derived/cuantitativos.json — agregados, SIN texto literal
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taxonomy as T  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("THESIS_DATA_DIR", ROOT / "Data_nosubiralrepo"))
PRIV = ROOT / "data" / "private"
DERIV = ROOT / "data" / "derived"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Un número con signo, admitiendo el menos tipográfico y la coma decimal.
NUM = re.compile(r"^[-−–—+]?\d{1,4}(?:[.,]\d+)?$")

# Rangos FÍSICOS de cada variable. Son el filtro que impide que una cifra
# cualquiera de la fila acabe archivada como dato.
RANGOS = {
    # El carbono de las filtraciones llega a valores muy negativos; por debajo
    # de -75 ‰ ya no es un δ13C de carbonato biogénico.
    "d13C": (-75.0, 5.0),
    "d18O": (-6.0, 6.5),
    "abundancia_rel": (0.0, 100.0),
    "shannon_H": (0.0, 6.0),
    "equidad_J": (0.0, 1.0),
    "simpson": (0.0, 1.0),
    "fisher_alpha": (0.0, 120.0),
}

CAPTION_ISOTOPO = re.compile(r"δ\s*1[38]\s*[CO]|d\s*1[38]\s*[CO]|isotop", re.I)
CAPTION_ABUND = re.compile(
    r"relative abundance|abundancia relativa|percent|%\s*of\s*(?:the\s*)?"
    r"(?:total|assemblage|fauna)", re.I)

# Índices de diversidad en prosa o en pie de tabla.
# El `(?!\s*%)` no es cosmético: en las páginas a dos columnas el texto de una
# columna se intercala con el de la otra, y sin él «…and Shannon-Wiener indices,
# but (2.4%), and Gyrodina altiforms» archivaba como Shannon el 2,4 % de
# abundancia de otra especie. Un índice de diversidad nunca es un porcentaje.
INDICES = [
    ("shannon_H", re.compile(
        r"(?:H\s*['′’]|Shannon(?:[-–\s]Wiener| index| diversity)?)"
        r"[^.\d]{0,40}?(\d[.,]\d{1,3})(?!\s*%)")),
    ("equidad_J", re.compile(
        r"(?:J\s*['′’]|evenness|equitability|Pielou)"
        r"[^.\d]{0,40}?(\d[.,]\d{1,3})(?!\s*%)")),
    ("simpson", re.compile(
        r"Simpson[^.\d]{0,40}?(\d[.,]\d{1,3})(?!\s*%)")),
    ("fisher_alpha", re.compile(
        r"Fisher[^.\d]{0,18}?(?:alpha|α)[^.\d]{0,24}?"
        r"(\d{1,3}(?:[.,]\d{1,2})?)(?!\s*%)")),
]

# «ranged from 1,5 to 3,5»: sin esto sólo se guardaba el extremo inferior y el
# máximo publicado quedaba fuera.
RANGO_SEGUIDO = re.compile(
    r"^\s*(?:to|and|a|hasta|[–—-])\s*(\d{1,3}[.,]\d{1,3})(?!\s*%)")


def a_float(s: str) -> float | None:
    s = s.replace("−", "-").replace("–", "-").replace("—", "-").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def filas_por_coordenada(pg) -> list[list[dict]]:
    """Reagrupa las palabras de la página en filas por su coordenada vertical.

    Es lo que `pypdf` no puede dar: sin la posición, la fila de una tabla se
    pierde entre el texto del cuerpo.
    """
    bandas: dict[int, list[dict]] = defaultdict(list)
    for w in pg.extract_words(x_tolerance=1.6, y_tolerance=2.2):
        bandas[round(w["top"] / 3.2)].append(w)
    return [sorted(bandas[k], key=lambda w: w["x0"]) for k in sorted(bandas)]


# Calificadores de nomenclatura abierta. El número que los sigue es el
# DESIGNADOR de la especie, no un dato: en «Reophax sp. 1 0,7 2,3» el «1» forma
# parte del nombre, y tomarlo por abundancia daba un 1 % inventado.
CALIFICADOR = {"sp.", "spp.", "sp", "spp", "cf.", "cf", "aff.", "aff", "?"}


def cifras_tras_taxon(ws: list[dict], taxon: str) -> list[float]:
    """Números de la fila que están DESPUÉS del nombre del taxón.

    Leer la fila entera metía en los datos el designador de especie y cualquier
    cifra que el nombre llevara dentro.
    """
    toks = [w["text"] for w in ws]
    partes = taxon.split()
    fin = None
    for i in range(len(toks) - len(partes) + 1):
        if toks[i:i + len(partes)] == partes:
            fin = i + len(partes)
            break
    if fin is None:                     # el nombre venía partido: se descarta
        return []
    while fin < len(toks) and toks[fin].rstrip(",;") in CALIFICADOR:
        fin += 1
        # tras «sp.» puede ir el número que identifica la morfoespecie
        if fin < len(toks) and re.fullmatch(r"\d{1,2}", toks[fin]):
            fin += 1
    out = []
    for t in toks[fin:]:
        if NUM.match(t):
            v = a_float(t)
            if v is not None:
                out.append(v)
    return out


def main() -> int:
    ev = json.loads((PRIV / "pdfs_evidencia.json").read_text(encoding="utf-8"))
    regs = json.loads((PRIV / "taxones_pdf.json").read_text(encoding="utf-8"))
    estudios = {e["id"]: e for e in
                json.loads((DERIV / "estudios.json").read_text(encoding="utf-8"))}

    # Taxones ya validados contra WoRMS, por estudio: sólo se aceptan filas
    # encabezadas por uno de ellos. Inventar el nombre a partir de la tabla
    # abriría la puerta a cualquier cosa.
    por_est: dict[str, dict[str, str]] = defaultdict(dict)
    for r in regs["registros"]:
        por_est[r["estudio_id"]][r["taxon_texto"]] = r["taxon"]

    valores: list[dict] = []
    indices: list[dict] = []
    sin_tabla: list[str] = []

    print("[1] Lectura de tablas con pdfplumber")
    for e in ev:
        eid = e.get("estudio_id")
        if not eid:
            continue
        p = DATA_DIR / e["archivo"]
        if not p.exists():
            continue
        conocidos = por_est.get(eid, {})
        if not conocidos:
            continue
        # Los binomios primero: si una fila empieza por «Uvigerina peregrina»,
        # debe reconocerse el binomio y no sólo el género.
        claves = sorted(conocidos, key=len, reverse=True)
        n_val = 0
        try:
            with pdfplumber.open(str(p)) as pdf:
                for i, pg in enumerate(pdf.pages):
                    texto_pg = pg.extract_text() or ""
                    es_iso = bool(CAPTION_ISOTOPO.search(texto_pg))
                    es_ab = bool(CAPTION_ABUND.search(texto_pg))
                    if not (es_iso or es_ab):
                        continue
                    for ws in filas_por_coordenada(pg):
                        linea = " ".join(w["text"] for w in ws)
                        # El taxón no siempre encabeza la fila: muchas tablas
                        # ponen antes la muestra o la profundidad. Exigir que
                        # estuviera al principio dejaba fuera casi todo.
                        taxon = next((k for k in claves if k in linea), None)
                        if taxon is None:
                            continue
                        nums = cifras_tras_taxon(ws, taxon)
                        if not nums:
                            continue

                        # δ13C: negativo y dentro de rango. El signo es la
                        # firma —el carbono del metano es muy negativo— y es
                        # además lo que lo distingue de una abundancia.
                        if es_iso:
                            # Se recogen TODOS los negativos de la fila, no
                            # sólo el primero: una fila suele traer el valor de
                            # varias muestras o estaciones.
                            #
                            # Sólo negativos, y es una decisión consciente: es
                            # la firma del carbono derivado del metano —lo que
                            # interesa aquí— y además es lo único que distingue
                            # un δ13C de un δ18O o de una abundancia cuando la
                            # cabecera de columna no se puede leer. Los valores
                            # positivos quedan sin clasificar, y así se declara.
                            lo, hi = RANGOS["d13C"]
                            for n in {x for x in nums if lo <= x <= -0.05}:
                                valores.append(dict(
                                    estudio_id=eid, taxon=conocidos[taxon],
                                    taxon_texto=taxon, variable="d13C",
                                    valor=n, unidad="‰ PDB", pagina=i + 1,
                                    evidencia=linea[:220]))
                                n_val += 1
                        # Abundancia relativa: sólo si el pie lo dice y la
                        # página no es de isótopos, por la trampa del ‰.
                        elif es_ab and not es_iso:
                            # Una fila de abundancias trae un valor por
                            # estación o muestra. Se guardan todos: el agregado
                            # público resume después en mínimo, máximo y media.
                            # Los encabezados de columna no se leen de forma
                            # fiable, así que NO se dice a qué estación
                            # corresponde cada cifra.
                            lo, hi = RANGOS["abundancia_rel"]
                            for n in sorted({x for x in nums if lo < x <= hi}):
                                valores.append(dict(
                                    estudio_id=eid, taxon=conocidos[taxon],
                                    taxon_texto=taxon,
                                    variable="abundancia_rel", valor=n,
                                    unidad="%", pagina=i + 1,
                                    evidencia=linea[:220]))
                                n_val += 1

                    # Índices de diversidad, de la propia página
                    for nombre, pat in INDICES:
                        for m in pat.finditer(texto_pg):
                            lo, hi = RANGOS[nombre]
                            cand = [a_float(m.group(1))]
                            # si detrás viene «to 3,5», es el otro extremo
                            r2 = RANGO_SEGUIDO.match(texto_pg[m.end():])
                            if r2:
                                cand.append(a_float(r2.group(1)))
                            ctx = " ".join(
                                texto_pg[max(0, m.start() - 90):
                                         m.end() + 40].split())[:220]
                            for v in cand:
                                if v is None or not (lo <= v <= hi):
                                    continue
                                indices.append(dict(
                                    estudio_id=eid, indice=nombre, valor=v,
                                    pagina=i + 1, evidencia=ctx))
        except Exception as exc:  # noqa: BLE001
            print(f"    {eid}: pdfplumber falló ({exc})", file=sys.stderr)
            continue
        if n_val == 0:
            sin_tabla.append(eid)

    # --- deduplicar: la misma cifra puede repetirse en cabecera y cuerpo ----
    def unico(xs: list[dict], claves: tuple[str, ...]) -> list[dict]:
        vistos, out = set(), []
        for x in xs:
            k = tuple(x[c] for c in claves)
            if k not in vistos:
                vistos.add(k)
                out.append(x)
        return out

    valores = unico(valores, ("estudio_id", "taxon", "variable", "valor"))
    indices = unico(indices, ("estudio_id", "indice", "valor"))

    (PRIV / "tablas_pdf.json").write_text(json.dumps({
        "valores": valores, "indices": indices,
        "estudios_sin_tabla_legible": sin_tabla,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- agregado público, SIN la fila literal --------------------------
    def resumen(var: str) -> list[dict]:
        g = defaultdict(list)
        for v in valores:
            if v["variable"] == var:
                g[(v["estudio_id"], v["taxon"])].append(v["valor"])
        return sorted(({"estudio_id": k[0], "taxon": k[1], "n": len(vs),
                        "min": round(min(vs), 3), "max": round(max(vs), 3),
                        "media": round(sum(vs) / len(vs), 3)}
                       for k, vs in g.items()),
                      key=lambda d: (d["estudio_id"], d["taxon"]))

    idx_pub = defaultdict(list)
    for x in indices:
        idx_pub[(x["estudio_id"], x["indice"])].append(x["valor"])

    (DERIV / "cuantitativos.json").write_text(json.dumps({
        "d13C": resumen("d13C"),
        "abundancia_rel": resumen("abundancia_rel"),
        "indices": sorted(({"estudio_id": k[0], "indice": k[1], "n": len(v),
                            "min": min(v), "max": max(v)}
                           for k, v in idx_pub.items()),
                          key=lambda d: (d["estudio_id"], d["indice"])),
        "nota_metodo":
            "Extraído de las tablas con pdfplumber, reagrupando las palabras "
            "por coordenada para recuperar la fila. Sólo se aceptan filas "
            "encabezadas por un taxón ya validado contra WoRMS, y cada cifra "
            "debe caer en el rango físico de su variable. Las abundancias "
            "exigen que el pie de tabla diga «%» o «relative abundance»: en "
            "varios artículos el símbolo ‰ de los δ13C sale del PDF como «%», "
            "y tomarlo por abundancia corrompería el dato. La cobertura es "
            "parcial por definición: muchas tablas son imágenes.",
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    d13 = [v for v in valores if v["variable"] == "d13C"]
    ab = [v for v in valores if v["variable"] == "abundancia_rel"]
    print(f"\n{len(d13)} valores de δ13C en {len({v['estudio_id'] for v in d13})} estudios")
    print(f"{len(ab)} abundancias relativas en {len({v['estudio_id'] for v in ab})} estudios")
    print(f"{len(indices)} índices de diversidad en "
          f"{len({x['estudio_id'] for x in indices})} estudios")
    if d13:
        print(f"δ13C: de {min(v['valor'] for v in d13):.2f} a "
              f"{max(v['valor'] for v in d13):.2f} ‰")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
