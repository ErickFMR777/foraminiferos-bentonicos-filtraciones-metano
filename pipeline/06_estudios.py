"""
06_estudios.py — Resuelve cada estudio a una referencia citable.

El campo 'Título' del libro original es heterogéneo: a veces es el título
inglés, a veces una cita APA completa, a veces el título seguido de su
traducción al español entre comillas tipográficas, y en dos casos incluye
anotaciones de trabajo del autor («(3 B Sofia)», «*comentarios rosa de
bengala: fracaso*»). Aquí se normaliza y se resuelve contra CrossRef para
obtener autores, año, revista y DOI.

Salida -> data/private/estudios_crossref.json
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
PRIV = ROOT / "data" / "private"

MAILTO = "dashboard-tesis@example.org"  # CrossRef pide un contacto; "polite pool"


def limpiar_titulo(t: str) -> str:
    """Deja sólo el título en inglés, sin traducción ni anotaciones."""
    s = t.replace("\n", " ")
    s = re.sub(r"[“”\"][^“”\"]*[“”\"]", " ", s)      # traducción entre comillas
    s = re.sub(r"\*[^*]*\*", " ", s)                  # *anotaciones*
    s = re.sub(r"\(\s*\d+\s*B\s+\w+\s*\)", " ", s)    # "(3 B Sofia)"
    s = re.sub(r"\s+", " ", s).strip(" .;,")
    return s


def crossref(q: str) -> dict | None:
    url = (
        "https://api.crossref.org/works?"
        + urllib.parse.urlencode({"query.bibliographic": q, "rows": 1, "mailto": MAILTO})
    )
    req = urllib.request.Request(url, headers={"User-Agent": f"tesis-forams/1.0 (mailto:{MAILTO})"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            items = json.load(r).get("message", {}).get("items", [])
    except Exception as exc:  # noqa: BLE001
        print(f"    fallo CrossRef: {exc}", file=sys.stderr)
        return None
    if not items:
        return None
    it = items[0]
    autores = []
    for a in it.get("author", []) or []:
        fam = a.get("family") or a.get("name") or ""
        ini = "".join(p[0] + "." for p in (a.get("given") or "").split() if p)
        autores.append(f"{fam}, {ini}".strip(", "))
    year = None
    for k in ("published-print", "published-online", "issued", "created"):
        parts = (it.get(k) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            year = parts[0][0]
            break
    return {
        "titulo_crossref": (it.get("title") or [None])[0],
        "autores": autores,
        "anio": year,
        "revista": (it.get("container-title") or [None])[0],
        "doi": it.get("DOI"),
        "volumen": it.get("volume"),
        "paginas": it.get("page"),
        "score": it.get("score"),
    }


def main() -> int:
    bib = json.loads((PRIV / "bibliografia_clean.json").read_text(encoding="utf-8"))
    counts = Counter(r["estudio"] for r in bib if r.get("estudio"))

    out = []
    for i, (titulo, n) in enumerate(sorted(counts.items(), key=lambda x: -x[1]), 1):
        limpio = limpiar_titulo(titulo)
        print(f"  [{i:2d}/{len(counts)}] {limpio[:70]}…")
        cr = crossref(limpio)
        out.append({
            "id": f"E{i:02d}",
            "titulo_original": titulo,
            "titulo_limpio": limpio,
            "n_registros": n,
            "crossref": cr,
        })
        time.sleep(0.6)

    (PRIV / "estudios_crossref.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    ok = sum(1 for o in out if o["crossref"] and o["crossref"].get("doi"))
    alto = sum(1 for o in out if o["crossref"] and (o["crossref"].get("score") or 0) > 80)
    print(f"\n{len(out)} estudios · {ok} con DOI · {alto} con score CrossRef > 80")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
