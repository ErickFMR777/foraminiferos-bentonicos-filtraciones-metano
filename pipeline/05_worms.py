"""
05_worms.py — Resolución taxonómica contra WoRMS / World Foraminifera Database.

La tesis declara haber usado WoRMS a noviembre de 2022 y sus conclusiones
recomiendan explícitamente esa autoridad. Este script vuelve a resolver cada
nombre contra la API oficial y separa dos cosas que NO son lo mismo:

  · errata      -> el nombre estaba mal escrito o mal transcrito
  · actualizacion -> el nombre era correcto en 2022 pero WoRMS lo ha
                     reclasificado desde entonces (p. ej. Cibicides
                     wuellerstorfi -> Lobatula wuellerstorfi, Schweizer 2009)

Ambas se registran, pero se reportan por separado: la primera es un error del
manuscrito, la segunda es evolución de la taxonomía y no lo es.

Resultado -> data/private/worms_cache.json  (cacheado; no re-consulta)
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
PRIV = ROOT / "data" / "private"
CACHE = PRIV / "worms_cache.json"

API = "https://www.marinespecies.org/rest/AphiaRecordsByMatchNames"
BATCH = 40
PAUSE = 1.2  # cortesía con la API pública


def query_name(name: str) -> str:
    """Nombre limpio para consultar: sin sp./spp./(?)/autoría."""
    s = re.sub(r"\(\?\)|\?", " ", str(name))
    s = re.sub(r",\s*\d{4}.*$", "", s)                    # "Reuss, 1862"
    s = re.sub(r"\b(spp?|sp)\b\.?", " ", s, flags=re.I)
    s = re.sub(r"\bsubsp\b\.?.*$", "", s, flags=re.I)
    s = re.sub(r"\b(cf|aff)\b\.?", " ", s, flags=re.I)
    s = re.sub(r"[^A-Za-zÀ-ÿ ]", " ", s)
    parts = " ".join(s.split()).split()
    return " ".join(parts[:2]) if parts else ""


def pick_foram(matches: list[dict]) -> dict | None:
    """Elige la coincidencia que sea foraminífero.

    Necesario porque varios géneros son homónimos entre grupos: 'Cassidulina'
    existe también como equinoideo, y WoRMS devuelve el equinoideo primero.
    Sin este filtro, un taxón central de la tesis entra clasificado como
    erizo de mar.
    """
    for m in matches:
        if (m.get("phylum") or "").lower() == "foraminifera":
            return m
    return None


def fuzzy(name: str) -> dict | None:
    """Respaldo: búsqueda parcial cuando la coincidencia exacta falla."""
    url = (
        "https://www.marinespecies.org/rest/AphiaRecordsByName/"
        f"{urllib.parse.quote(name)}?like=true&marine_only=false"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "tesis-forams-dashboard/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return pick_foram(json.load(r) or [])
    except Exception:  # noqa: BLE001
        return None


def fetch(names: list[str]) -> dict[str, dict]:
    qs = "&".join(
        f"scientificnames[]={urllib.parse.quote(n)}" for n in names
    )
    url = f"{API}?{qs}&marine_only=false"
    req = urllib.request.Request(url, headers={"User-Agent": "tesis-forams-dashboard/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    out: dict[str, dict] = {}
    for name, matches in zip(names, data):
        m = pick_foram(matches or [])
        if m is None:
            m = fuzzy(name)
            time.sleep(0.4)
        if m is None:
            out[name] = {"found": False}
            continue
        out[name] = {
            "found": True,
            "input": name,
            "matched": m.get("scientificname"),
            "authority": m.get("authority"),
            "status": m.get("status"),
            "unaccept_reason": m.get("unacceptreason"),
            "valid_name": m.get("valid_name"),
            "valid_aphia": m.get("valid_AphiaID"),
            "aphia": m.get("AphiaID"),
            "rank": m.get("rank"),
            "phylum": m.get("phylum"),
            "class": m.get("class"),
            "order": m.get("order"),
            "family": m.get("family"),
            "genus": m.get("genus"),
            "match_type": m.get("match_type"),
        }
    return out


def main() -> int:
    bib = json.loads((PRIV / "bibliografia_raw.json").read_text(encoding="utf-8"))
    msh = json.loads((PRIV / "msh_raw.json").read_text(encoding="utf-8"))

    raw_names: set[str] = set()
    for r in bib["maestra"]:
        if r["especie_raw"]:
            raw_names.add(r["especie_raw"].strip())
    for r in msh["especies"]:
        if r["especie_raw"]:
            raw_names.add(r["especie_raw"].strip())

    # nombre crudo -> nombre de consulta
    to_query = {}
    for rn in raw_names:
        q = query_name(rn)
        if q:
            to_query[rn] = q

    cache: dict[str, dict] = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))

    pending = sorted({q for q in to_query.values() if q not in cache})
    print(f"{len(raw_names)} nombres crudos -> {len(set(to_query.values()))} consultas únicas")
    print(f"{len(pending)} pendientes de resolver ({len(cache)} en caché)")

    for i in range(0, len(pending), BATCH):
        chunk = pending[i : i + BATCH]
        try:
            cache.update(fetch(chunk))
            print(f"  lote {i // BATCH + 1}: {len(chunk)} nombres OK")
        except Exception as exc:  # noqa: BLE001
            print(f"  lote {i // BATCH + 1} FALLÓ: {exc}", file=sys.stderr)
            for n in chunk:
                cache.setdefault(n, {"found": False, "error": str(exc)})
        time.sleep(PAUSE)

    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    # mapa nombre crudo -> resolución, para los pasos siguientes
    resolved = {rn: cache.get(q, {"found": False}) for rn, q in to_query.items()}
    (PRIV / "worms_resolved.json").write_text(
        json.dumps(resolved, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    n_ok = sum(1 for v in resolved.values() if v.get("found"))
    n_acc = sum(1 for v in resolved.values() if v.get("status") == "accepted")
    n_un = sum(1 for v in resolved.values() if v.get("status") == "unaccepted")
    n_fuzzy = sum(1 for v in resolved.values() if v.get("match_type") not in (None, "exact"))
    print(f"\nRESUELTOS {n_ok}/{len(resolved)}  ·  aceptados {n_acc}  ·  "
          f"no aceptados {n_un}  ·  coincidencia difusa {n_fuzzy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
