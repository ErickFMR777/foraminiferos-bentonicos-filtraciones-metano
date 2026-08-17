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
    r"(dominant|dominate[sd]?|most abundant|abundant species|predominant"
    r"|characteristic species|highest abundance|the most common)", re.I)


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
        textos[r["estudio_id"]] = t
        for g, e in BINOMIO.findall(t):
            if e in STOP or g.lower() in STOP:
                continue
            candidatos[f"{g} {e}"] += 1
        for g in GENERO_ABIERTO.findall(t):
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
               and (cache[k].get("phylum") or "").lower() == "foraminifera"}
    print(f"    {len(validos)} candidatos son foraminíferos reconocidos")

    # --- 3. ocurrencias por estudio ------------------------------------
    print("[3] Ocurrencias por estudio")
    registros = []
    for eid, t in textos.items():
        # frases donde el artículo afirma dominancia
        frases_dom = [m.group(0) for m in
                      re.finditer(r"[^.]{0,220}" + FRASE_DOMINANCIA.pattern +
                                  r"[^.]{0,220}\.", t, re.I)]
        for crudo, w in validos.items():
            n = len(re.findall(r"\b" + re.escape(crudo) + r"\b", t))
            if not n:
                continue
            valido = w.get("valid_name") or w.get("matched") or crudo
            dominante = any(crudo in f or valido in f for f in frases_dom)
            registros.append({
                "estudio_id": eid,
                "taxon_texto": crudo,
                "taxon": valido,
                "aphia_id": w.get("valid_aphia") or w.get("aphia"),
                "rango": "genero" if w.get("rank") == "Genus" else "especie",
                "genero": T.genus_label(valido),
                "familia": w.get("family"),
                "orden": w.get("order"),
                "menciones": n,
                "dominante_declarado": dominante,
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
    if escaneados:
        print(f"Sin capa de texto: {escaneados}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
