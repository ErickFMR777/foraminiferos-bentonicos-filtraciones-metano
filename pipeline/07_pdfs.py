"""
07_pdfs.py — Identifica los PDF de la carpeta privada y extrae evidencia.

Hace dos cosas:

  1. Empareja cada PDF con un estudio de la base. La única señal fiable es el
     DOI de la PRIMERA página: buscarlo en todo el texto falla, porque la
     lista de referencias de cada artículo cita a los demás y el emparejador
     acaba asignando el mismo PDF a media base.
  2. Extrae la evidencia necesaria para completar la tipología: menciones de
     morfología del fondo (pockmark, volcán de lodo, montículo de hidratos…),
     coordenadas, profundidades y el número de especies que reporta el
     artículo.

Salida -> data/private/pdfs_evidencia.json  (privado: cita texto literal)
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("THESIS_DATA_DIR", ROOT / "Data_nosubiralrepo"))
PRIV = ROOT / "data" / "private"
DERIV = ROOT / "data" / "derived"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Algunos PDF no traen el DOI en el texto. Se identifican por una firma del
# contenido, NO por el nombre del archivo: los archivos se renombran en
# 08_organizar.py y cualquier mapeo por nombre quedaría roto al día siguiente.
MANUAL_FIRMA = [
    ("monterey bay cold-seep biota", "10.1016/s0967-0637(01)00017-6"),
    ("preliminary observations on benthonic foraminifera", "10.1007/978-94-017-0763-3_3"),
    ("preliminary observations on benthonic foramininera", "10.1007/978-94-017-0763-3_3"),
    ("foraminifera of hydrocarbon seeps, gulf of mexico", "10.2113/gsjfr.38.2.93"),
    ("cold methane seeps on the northern california margin", "10.1016/s0377-8398(00)00005-0"),
    ("bathyal hydrocarbon vents of the gulf", "10.1007/bf01203719"),
    ("influence of microhabitats on the carbon isotopic", "10.1029/pa005i002p00161"),
    ("benthic foraminifera assemblage in adriatic", "10.3997/2214-4609.201406085"),
    ("foraminiferal colonization of hydrocarbon-seep bacterial mats",
     "10.2113/gsjfr.27.4.292"),
    ("southeast seep on kimki ridge", "10.1016/j.dsr2.2018.01.011"),
    ("southeast cold seep on kimki ridge", "10.1016/j.dsr2.2018.01.011"),
]

# PDF sin capa de texto (escaneados). No se les puede extraer evidencia:
# se identifican por el nombre y se marcan para revisión manual.
ESCANEADOS = [
    ("McGann 2018", "10.1016/j.dsr2.2018.01.011"),
]

MORFOLOGIA_CLAVES = {
    "pockmark": r"pockmark",
    "volcan_lodo": r"mud volcano|mud-volcano|mud diapir",
    "monticulo_hidratos": r"hydrate mound|gas hydrate mound|carbonate mound",
    "pingo_hidratos": r"pingo",
    "diapiro": r"\bdiapir",
    "escarpe": r"escarpment|scarp\b",
    "tapete_bacteriano": r"bacterial mat|microbial mat",
    "banco_bivalvos": r"clam (bed|field|flat)|mussel bed|vesicomyid|bathymodiol",
    "respiradero_hidrotermal": r"hydrothermal vent|hydrothermal chimney",
    "carbonato": r"authigenic carbonate|carbonate pavement|carbonate crust",
}
FLUIDO_CLAVES = {
    "termogenico": r"thermogenic",
    "biogenico": r"biogenic gas|microbial methane",
    "hidrotermal": r"hydrothermal",
}


def texto(p: Path, paginas: int | None = None) -> str:
    try:
        r = PdfReader(str(p))
        pgs = r.pages if paginas is None else r.pages[:paginas]
        return re.sub(r"\s+", " ", " ".join((x.extract_text() or "") for x in pgs))
    except Exception as exc:  # noqa: BLE001
        print(f"  ERROR leyendo {p.name}: {exc}", file=sys.stderr)
        return ""


def doi_de(p: Path) -> str | None:
    """DOI de la PRIMERA página, o firma de contenido si no lo trae.

    Buscar el DOI en todo el texto no sirve: la bibliografía de cada artículo
    cita a los demás, y el emparejador acabaría asignando el mismo PDF a media
    base.
    """
    # SÓLO la primera página. Buscar la firma en más páginas hace que la
    # bibliografía del artículo, que cita a los demás, dispare una coincidencia
    # ajena: así el resumen P-43 de Panieri (2000) acabó identificado como
    # Sen Gupta & Aharon (1994), a quien simplemente citaba.
    low = texto(p, paginas=1).lower()
    encontradas = [(low.find(f), d) for f, d in MANUAL_FIRMA if f in low]
    if encontradas:
        return min(encontradas)[1]      # la que aparece antes: el título
    m = re.search(r"10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+", texto(p, paginas=1))
    if m:
        return m.group(0).lower().rstrip(".,;)")
    # Último recurso para PDF escaneados, sin ninguna capa de texto: el nombre
    # del archivo, que en ese punto ya lo asignó 08_organizar.py. De estos no
    # se puede extraer evidencia automáticamente; quedan marcados como tales.
    for firma, doi in ESCANEADOS:
        if firma.lower() in p.name.lower():
            return doi
    return None


def casa(doi_pdf: str | None, doi_est: str) -> bool:
    if not doi_pdf or not doi_est:
        return False
    a, b = doi_pdf.lower(), doi_est.lower()
    return a == b or a.startswith(b) or b.startswith(a)


def main() -> int:
    estudios = json.loads((DERIV / "estudios.json").read_text(encoding="utf-8"))
    pdfs = [p for p in sorted(DATA_DIR.glob("*.pdf"))
            if not p.name.startswith("TDG-ERICKFMR")]

    print(f"{len(pdfs)} PDF en la carpeta, {len(estudios)} estudios en la base\n")

    out, usados = [], set()
    for p in pdfs:
        d = doi_de(p)
        est = next((e for e in estudios if casa(d, e.get("doi") or "")), None)
        t = texto(p)
        low = t.lower()

        morf = {}
        for clave, patron in MORFOLOGIA_CLAVES.items():
            hits = [m.start() for m in re.finditer(patron, low)]
            if hits:
                morf[clave] = {
                    "n": len(hits),
                    "contexto": [t[max(0, h - 110):h + 110] for h in hits[:2]],
                }
        fluido = {k: len(re.findall(v, low)) for k, v in FLUIDO_CLAVES.items()
                  if re.search(v, low)}

        coords = re.findall(
            r"\d{1,3}\s*[°º]\s*\d{1,2}(?:[.,]\d+)?\s*['′]?\s*(?:\d{1,2}(?:[.,]\d+)?\s*[\"″])?\s*[NSEW]",
            t)
        profs = re.findall(r"(\d{2,5})\s*(?:-|–|to)\s*(\d{2,5})\s*m\b", t)
        n_sp = re.findall(r"([A-Za-z-]+|\d+)\s+species of benthic foraminifera", t)

        reg = {
            "archivo": p.name,
            "doi_pdf": d,
            "estudio_id": est["id"] if est else None,
            "estudio_titulo": est["titulo"] if est else None,
            "paginas": len(PdfReader(str(p)).pages),
            "morfologia_detectada": morf,
            "fluido_detectado": fluido,
            "coordenadas": coords[:12],
            "rangos_profundidad": profs[:8],
            "n_especies_declarado": n_sp[:3],
        }
        out.append(reg)
        if est:
            usados.add(est["id"])

        etq = est["id"] if est else "SIN CASAR"
        top = max(morf, key=lambda k: morf[k]["n"]) if morf else "-"
        print(f"  {etq:<10} {p.name[:48]:<50} morf={top:<20} fluido={list(fluido) or '-'}")

    PRIV.mkdir(parents=True, exist_ok=True)
    (PRIV / "pdfs_evidencia.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    sin_pdf = [e for e in estudios if e["id"] not in usados]
    print(f"\nEmparejados: {len(usados)}/{len(estudios)} estudios")
    print(f"Sin PDF: {[e['id'] for e in sin_pdf]}")
    print(f"PDF sin casar: {[r['archivo'][:40] for r in out if not r['estudio_id']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
