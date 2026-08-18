"""
40_taxones_pdf.py — Extrae las listas completas de taxones de cada artículo.

La base de la tesis recoge «las 5 principales especies» de cada filtro, tal
como declara su metodología. Es por tanto una muestra de las dominantes, no
las asociaciones completas: Lobegeier y Sen Gupta (2008) reportan 183 especies
y la base tomó 18 registros de ese artículo.

Aquí se leen los artículos completos y se extrae todo taxón mencionado, para
poder responder qué especies y géneros reporta cada estudio, cuáles dominan en
cada uno y cuáles en el conjunto.

Método y sus límites, que el dashboard debe declarar:

  · Se buscan binomios en el texto y se validan contra WoRMS, conservando sólo
    lo que la autoridad reconoce como Foraminifera. Un nombre que WoRMS no
    reconozca no entra: se prefiere perder taxones a inventarlos.
  · La MENCIÓN no es lo mismo que la ABUNDANCIA. Un artículo nombra especies
    en su introducción, en la discusión y al citar otros trabajos. Por eso se
    guarda además dónde aparece cada taxón y cuántas veces, y la dominancia se
    marca sólo cuando el texto la afirma explícitamente.
  · Un PDF escaneado sin capa de texto no aporta nada. Quedan señalados.

Salida -> data/private/taxones_pdf.json
"""

from __future__ import annotations

import json
import bisect
import difflib
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taxonomy as T  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("THESIS_DATA_DIR", ROOT / "Data_nosubiralrepo"))
PRIV = ROOT / "data" / "private"
DERIV = ROOT / "data" / "derived"
CACHE = PRIV / "worms_cache.json"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BINOMIO = re.compile(r"\b([A-Z][a-z]{3,15})\s+([a-z]{3,18})\b")
GENERO_ABIERTO = re.compile(r"\b([A-Z][a-z]{3,15})\s+(?:spp?|sp)\.")

# Palabras que nunca son epíteto ni género: recortan el ruido antes de
# molestar a la API de WoRMS.
STOP = set("""the and for with from this that were was are have has been not but all
its their which when where than then also more most other some such these those
species genus samples sample study area data results table figure fig
sediment sediments water depth seep seeps methane carbon isotope isotopes
foraminifera foraminiferal benthic marine deep sea ocean margin basin ridge
university department research journal press volume issue pages available
based using between during within after before both each many also
however therefore moreover although because while since though
bengal stained mats mat bed beds field fields slope shelf zone zones
values value ratio ratios content contents range ranges site sites
analysis analyses method methods result total number percent
north south east west northern southern eastern western upper lower
first second third high low higher lower increase decrease""".split())

FRASE_DOMINANCIA = re.compile(
    r"(dominant|dominate[sd]?|dominating|dominance of|most abundant"
    r"|abundant species|predominant|characteristic species|highest abundance"
    r"|the most common|highest relative abundance)", re.I)

# --- Lo que convierte una señal de dominancia en un falso positivo --------
# Cláusula: la unidad correcta para atribuir la afirmación. Antes bastaba con
# que el taxón y la palabra «dominant» cayeran en la misma FRASE, y eso marcaba
# dominante a cualquier taxón nombrado de paso: en «Bolivina dominated the
# assemblage, whereas Uvigerina was rare», Uvigerina salía dominante.
CORTE_CLAUSULA = re.compile(
    r"[;.]|\b(?:whereas|while|but|although|however|though|except|unlike"
    r"|in contrast|compared with|compared to|rather than|instead of)\b", re.I)
# «dominant» calificando algo que NO es una asociación de foraminíferos: la
# dirección de enrollamiento, la litología, un proceso geoquímico. Así se
# colaba «the dominant coiling direction of the planktonic foraminifer
# Neogloboquadrina pachyderma», que no habla de abundancia ninguna.
SUJETO_AJENO = re.compile(
    r"\b(coiling|lithology|lithologies|role|process(?:es)?|pathway|factor"
    r"|control|direction|source|mechanism|facies|mineral|phase|mode|trend"
    r"|reaction|oxidation|reduction|current|wind|clay|sand|silt|carbonate"
    r"|bacteri\w+|mat|mats|worm|worms|macrofauna|vegetation|lineage)\b", re.I)
NEGACION = re.compile(
    r"\b(not|never|rarely|seldom|neither|nor|without|absent|absence|lack\w*"
    r"|no longer|less|fewer|scarce|rare|scarcely|hardly)\b", re.I)
# «Rathburn et al. (2000) found X dominant» habla de OTRO trabajo, no de este.
#
# «et al» va SIN exigir año ni paréntesis de cierre: la cita puede quedar
# partida por el propio límite de cláusula, y así se colaba
# «they recorded the dominance of Fursenkoina … (Kaminski et al» como si el
# artículo lo afirmara de sus datos.
ATRIBUCION = re.compile(
    r"(\bet\s+al\b"
    r"|\b(?:they|who|which)\s+(?:also\s+)?(?:recorded|reported|found|observed"
    r"|described|noted|documented|identified|showed)\b"
    r"|\b(?:has|have|had|was|were|been)\s+(?:also\s+)?(?:reported|recorded"
    r"|observed|described|noted|documented)\b"
    r"|\b(?:reported|recorded|observed|described|noted|documented)\s+by\b"
    r"|\baccording to\b"
    r"|[A-Z][a-z]+\s+and\s+[A-Z][a-z]+\s*\(?\s*(?:19|20)\d{2}"
    r"|\(\s*(?:e\.g\.,?\s*|see\s+|cf\.\s*)?[A-Z][a-z]+[^)]{0,70}?(?:19|20)\d{2}[a-z]?\s*\))")

# La bibliografía cita los títulos de otros artículos, y esos títulos llevan
# nombres de especies. Contarlos convierte en «reportado» un taxón que el
# artículo sólo nombra al citar a un tercero.
REFERENCIAS = re.compile(
    r"\b(references(?:\s+cited)?|bibliography|literature cited"
    r"|referencias(?:\s+bibliogr[áa]ficas)?)\b", re.I)
# Forma de una entrada bibliográfica: «Rathburn, A.» / «Sen Gupta, B.». Sirve
# para confirmar que donde dice «references» empieza de verdad la bibliografía.
ENTRADA_BIB = re.compile(r"[A-Z][a-z]{2,}\s*,\s*[A-Z]\.")
# Encabezado de Resultados, no la palabra suelta. SIN re.I a propósito: la
# prosa escribe «our results show…» en minúscula y el encabezado va
# capitalizado, así que la mayúscula es el discriminador. Tomar cualquier
# «results» por el encabezado daría por reportado casi todo.
RESULTADOS = re.compile(
    r"(?:\d\.?\s*)?\b(RESULTS AND DISCUSSION|RESULTS|Results and Discussion"
    r"|Results|RESULTADOS|Resultados)\b")
# «U. peregrina» tras la primera cita completa del binomio.
ABREVIADO = re.compile(r"\b([A-Z])\.\s*([a-z]{3,18})\b")


def cortar_referencias(t: str) -> tuple[str, str]:
    """Separa el cuerpo del artículo de su lista de referencias.

    El encabezado se busca sólo en la segunda mitad del texto —es donde está— y
    se exige que lo que quede detrás tenga tamaño de bibliografía, para no
    partir el artículo por una mención suelta a «references» en un pie de
    figura.
    """
    for m in REFERENCIAS.finditer(t):
        if m.start() <= len(t) * 0.5 or (len(t) - m.start()) <= len(t) * 0.03:
            continue
        # «references» también aparece en prosa («with references to…»). Cortar
        # ahí descartaría los Resultados enteros, así que se exige que detrás
        # haya forma de bibliografía: varios «Apellido, X.» seguidos.
        if len(ENTRADA_BIB.findall(t[m.end():m.end() + 600])) >= 3:
            return t[:m.start()], t[m.start():]
    return t, ""


def expandir_abreviados(t: str, completos: set[str]) -> str:
    """Reescribe «U. peregrina» como «Uvigerina peregrina».

    Los artículos escriben el binomio entero la primera vez y lo abrevian
    después, sobre todo en tablas y listas de especies. Sin esto se pierden
    menciones en masa y el recuento queda sesgado hacia los taxones que se
    nombran pocas veces.

    Sólo se expande cuando inicial y epíteto identifican UN único binomio del
    propio artículo: si «B. spissa» pudiera ser Bolivina o Bulimina, se deja
    como está antes que adivinar.
    """
    idx: dict[tuple[str, str], set[str]] = {}
    for nombre in completos:
        genero, _, epiteto = nombre.partition(" ")
        if epiteto:
            idx.setdefault((genero[0], epiteto), set()).add(nombre)

    def sub(m: re.Match) -> str:
        cand = idx.get((m.group(1), m.group(2)))
        return next(iter(cand)) if cand and len(cand) == 1 else m.group(0)

    return ABREVIADO.sub(sub, t)


def genero_compatible(candidato: str, w: dict) -> bool:
    """¿La coincidencia difusa de WoRMS respeta el género?

    WoRMS empareja por aproximación, y eso RESCATA erratas de OCR reales
    —«Sfainforfhia fisiformis» es Stainforthia fusiformis, «Bolivma ordinaria»
    es Bolivina ordinaria— pero también puede saltar de un género a otro:
    «Bolivina tenuata» acabó emparejado con *Bulimina* tenuata y archivado como
    Eubuliminella exilis, que es otra cosa.

    El umbral de 0,80 no es arbitrario: se midió sobre los 87 nombres difusos
    de esta base y separa exactamente ese único salto de género (0,750) de la
    errata legítima más extrema (0,800).
    """
    if w.get("match_type") in ("exact", "exact_subgenus"):
        return True
    emparejado = (w.get("matched") or "").split()
    partes = candidato.split()
    if not emparejado or not partes:
        return False
    return difflib.SequenceMatcher(
        None, partes[0].lower(), emparejado[0].lower()).ratio() >= 0.80


def dominantes_del_texto(cuerpo: str, nombres: list[str]) -> dict[str, str]:
    """Taxones que el ARTÍCULO declara dominantes, con la cláusula que lo dice.

    Se descartan las cláusulas negadas («X was not dominant») y las que
    atribuyen el hallazgo a otro trabajo. La evidencia se devuelve para que la
    afirmación sea auditable: es texto literal del artículo, así que sólo puede
    viajar a la carpeta privada.
    """
    # Los límites de cláusula se calculan UNA vez y se localizan por bisección.
    # Recorrer el prefijo del texto en cada indicio era cuadrático y con
    # artículos de 400 KB se volvía inviable.
    cortes = [m.end() for m in CORTE_CLAUSULA.finditer(cuerpo)]
    inicios = [m.start() for m in CORTE_CLAUSULA.finditer(cuerpo)]
    patrones = {n: re.compile(r"\b" + re.escape(n) + r"\b") for n in nombres}

    out: dict[str, str] = {}
    for m in FRASE_DOMINANCIA.finditer(cuerpo):
        p = m.start()
        i = bisect.bisect_left(cortes, p)
        izq = cortes[i - 1] if i else 0
        j = bisect.bisect_right(inicios, p)
        der = inicios[j] if j < len(inicios) else min(len(cuerpo), p + 260)
        cl = cuerpo[izq:der]
        # La atribución sólo cuenta si va ANTES del indicio. Una cita que
        # aparece después suele ser apoyo del hallazgo propio, no su autoría:
        # buscándola también detrás se perdía «Dominant infaunal taxa included:
        # Globobulimina pacifica, Nonionella stella…» por un «(e.g., Rathburn y
        # Corliss)» que venía a continuación.
        # Y sin margen a la izquierda: una cita de la frase ANTERIOR no
        # atribuye ésta. Con 40 caracteres de cortesía se perdía «Dominant
        # infaunal taxa included: …» porque la oración previa terminaba en
        # «(e.g., Rathburn y Corliss, 2002).».
        if NEGACION.search(cl) or ATRIBUCION.search(cuerpo[izq:p]):
            continue
        # Lo que el indicio califica va justo detrás: si es un proceso, una
        # litología o la dirección de enrollamiento, no es una dominancia
        # faunística.
        if SUJETO_AJENO.search(cuerpo[m.end():m.end() + 34]):
            continue
        for n, pat in patrones.items():
            # Límite de palabra: sin él «Bolivina» casaba dentro de
            # «Bolivinita» y contagiaba la dominancia a otro género.
            if n not in out and pat.search(cl):
                out[n] = " ".join(cl.split())[:300]
    return out


def cargar_cache() -> dict:
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def consultar_worms(nombres: list[str], cache: dict) -> None:
    """Resuelve en lotes y guarda en el caché compartido. Sólo Foraminifera."""
    pend = [n for n in nombres if n not in cache]
    if not pend:
        return
    api = "https://www.marinespecies.org/rest/AphiaRecordsByMatchNames"
    for i in range(0, len(pend), 40):
        chunk = pend[i:i + 40]
        qs = "&".join(f"scientificnames[]={urllib.parse.quote(n)}" for n in chunk)
        req = urllib.request.Request(
            f"{api}?{qs}&marine_only=false",
            headers={"User-Agent": "tesis-forams-dashboard/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.load(r)
        except Exception as exc:  # noqa: BLE001
            print(f"    lote {i // 40 + 1} falló: {exc}", file=sys.stderr)
            for n in chunk:
                cache.setdefault(n, {"found": False})
            time.sleep(2)
            continue
        for nombre, matches in zip(chunk, data):
            m = next((x for x in (matches or [])
                      if (x.get("phylum") or "").lower() == "foraminifera"), None)
            cache[nombre] = {"found": False} if m is None else {
                "found": True, "matched": m.get("scientificname"),
                "status": m.get("status"), "valid_name": m.get("valid_name"),
                "valid_aphia": m.get("valid_AphiaID"), "aphia": m.get("AphiaID"),
                "rank": m.get("rank"), "phylum": m.get("phylum"),
                "class": m.get("class"), "order": m.get("order"),
                "family": m.get("family"), "genus": m.get("genus"),
                "match_type": m.get("match_type"),
            }
        print(f"    lote {i // 40 + 1}/{(len(pend) + 39) // 40}: {len(chunk)} nombres")
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        time.sleep(1.2)


def main() -> int:
    ev = json.loads((PRIV / "pdfs_evidencia.json").read_text(encoding="utf-8"))
    estudios = {e["id"]: e for e in
                json.loads((DERIV / "estudios.json").read_text(encoding="utf-8"))}
    cache = cargar_cache()

    # --- 1. leer los PDF y proponer candidatos --------------------------
    print("[1] Lectura de los artículos")
    textos, candidatos = {}, Counter()
    escaneados, ausentes = [], []
    for r in ev:
        if not r["estudio_id"]:
            continue
        p = DATA_DIR / r["archivo"]
        if not p.exists():
            # Nunca en silencio: pdfs_evidencia.json guarda el nombre del
            # archivo, y 08_organizar.py los renombra. Si el índice está
            # desfasado, dos artículos desaparecerían sin dejar rastro.
            ausentes.append((r["estudio_id"], r["archivo"]))
            continue
        try:
            crudo = " ".join((pg.extract_text() or "")
                             for pg in PdfReader(str(p)).pages)
        except Exception:  # noqa: BLE001
            continue
        t = T.normalizar_pdf(crudo)
        if len(t.strip()) < 500:
            escaneados.append(r["estudio_id"])
            continue

        # El índice de abreviaturas se construye con el texto ENTERO —el
        # binomio completo puede estar sólo en la bibliografía— pero las
        # menciones se cuentan después sólo en el cuerpo.
        completos = {f"{g} {e}" for g, e in BINOMIO.findall(t)
                     if e not in STOP and g.lower() not in STOP}
        t = expandir_abreviados(t, completos)
        cuerpo, refs = cortar_referencias(t)
        textos[r["estudio_id"]] = (cuerpo, refs)

        for g, e in BINOMIO.findall(cuerpo):
            if e in STOP or g.lower() in STOP:
                continue
            candidatos[f"{g} {e}"] += 1
        for g in GENERO_ABIERTO.findall(cuerpo):
            if g.lower() not in STOP:
                candidatos[g] += 1
    print(f"    {len(textos)} artículos legibles, {len(escaneados)} escaneados")
    if ausentes:
        print(f"    AVISO: {len(ausentes)} archivos del índice no existen "
              f"(ejecuta 07_pdfs.py para refrescarlo): {ausentes}")
    print(f"    {len(candidatos)} candidatos únicos")

    # --- 2. validar contra WoRMS ---------------------------------------
    print("[2] Validación taxonómica contra WoRMS")
    por_consultar = sorted(k for k in candidatos if k not in cache)
    print(f"    {len(cache)} en caché · {len(por_consultar)} por consultar")
    consultar_worms(por_consultar, cache)

    validos = {k: cache[k] for k in candidatos
               if cache.get(k, {}).get("found")
               and (cache[k].get("phylum") or "").lower() == "foraminifera"
               and genero_compatible(k, cache[k])}
    print(f"    {len(validos)} candidatos son foraminíferos reconocidos")

    # --- 3. ocurrencias por estudio ------------------------------------
    print("[3] Ocurrencias por estudio")
    registros = []
    for eid, (cuerpo, refs) in textos.items():
        presentes = [c for c in validos
                     if re.search(r"\b" + re.escape(c) + r"\b", cuerpo)]
        dom = dominantes_del_texto(cuerpo, presentes)

        # Marca de si el taxón aparece en Resultados y no sólo en la
        # introducción: una especie citada al repasar la literatura no está
        # reportada por este artículo.
        mres = None
        for m in RESULTADOS.finditer(cuerpo):
            if m.start() > len(cuerpo) * 0.12:
                mres = m.start()
                break

        for crudo in presentes:
            w = validos[crudo]
            pos = [m.start() for m in
                   re.finditer(r"\b" + re.escape(crudo) + r"\b", cuerpo)]
            valido = w.get("valid_name") or w.get("matched") or crudo
            registros.append({
                "estudio_id": eid,
                "taxon_texto": crudo,
                "taxon": valido,
                "aphia_id": w.get("valid_aphia") or w.get("aphia"),
                "rango": "genero" if w.get("rank") == "Genus" else "especie",
                "genero": T.genus_label(valido),
                "familia": w.get("family"),
                "orden": w.get("order"),
                "menciones": len(pos),
                "menciones_en_referencias": len(re.findall(
                    r"\b" + re.escape(crudo) + r"\b", refs)) if refs else 0,
                # None = no se localizó el encabezado de Resultados en este
                # artículo. No es lo mismo que «no aparece allí», y contarlo
                # como falso subestimaría lo realmente reportado.
                "en_resultados": (None if mres is None
                                  else any(p >= mres for p in pos)),
                "dominante_declarado": crudo in dom,
                # Texto literal del artículo: NO puede salir de data/private/.
                "evidencia_dominancia": dom.get(crudo),
            })

    salida = {
        "registros": registros,
        "escaneados": escaneados,
        "ausentes": ausentes,
        "n_articulos": len(textos),
        "n_candidatos": len(candidatos),
        "n_validos": len(validos),
    }
    (PRIV / "taxones_pdf.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{len(registros)} ocurrencias taxón×estudio")
    print(f"{len({r['taxon'] for r in registros})} taxones distintos")
    print(f"{sum(1 for r in registros if r['dominante_declarado'])} marcadas como "
          "dominantes por el propio artículo")
    print(f"{sum(1 for r in registros if r['en_resultados'] is True)} aparecen "
          "en Resultados y no sólo al repasar la literatura")
    print(f"{sum(1 for r in registros if r['en_resultados'] is False)} sólo "
          "antes de Resultados (introducción o métodos)")
    print(f"{sum(1 for r in registros if r['en_resultados'] is None)} sin "
          "determinar: no se localizó el encabezado de Resultados")
    print(f"{sum(r['menciones_en_referencias'] for r in registros)} menciones "
          "quedaron fuera al descartar la bibliografía")
    if escaneados:
        print(f"Sin capa de texto: {escaneados}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
