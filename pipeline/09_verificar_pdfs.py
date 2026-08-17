"""
09_verificar_pdfs.py — Comprueba que cada PDF contiene lo que su nombre dice.

Existe porque el emparejador falló una vez de forma silenciosa: la firma de
texto se buscaba en tres páginas y capturó una cita de la bibliografía, de
modo que el resumen P-43 de Panieri (2000) acabó archivado con el nombre de
Sen Gupta & Aharon (1994), a quien simplemente citaba.

La comprobación es independiente del emparejador: toma el apellido y el año
del nombre del archivo y los busca en la PRIMERA página del propio PDF.
"""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("THESIS_DATA_DIR", ROOT / "Data_nosubiralrepo"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Nombres cuya primera página no contiene el año (portadas de editorial, etc.)
TOLERAR_SIN_ANIO = {"Jones", "Lobegeier", "McGann"}


def sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def detectar_duplicados(archivos: list[Path]) -> list[tuple[str, list[Path]]]:
    """Duplicados por contenido idéntico (hash) y por mismo DOI.

    Un mismo artículo archivado dos veces duplicaría sus taxones al extraer
    las listas de especies, inflando la base sin que se note.
    """
    import hashlib
    from collections import defaultdict

    por_hash: dict[str, list[Path]] = defaultdict(list)
    por_doi: dict[str, list[Path]] = defaultdict(list)
    for p in archivos:
        if p.name.startswith("TDG-ERICKFMR"):
            continue
        por_hash[hashlib.sha256(p.read_bytes()).hexdigest()].append(p)
        try:
            t = PdfReader(str(p)).pages[0].extract_text() or ""
        except Exception:  # noqa: BLE001
            continue
        m = re.search(r"10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+", t)
        if m:
            por_doi[m.group(0).lower().rstrip(".,;)")].append(p)

    dup = [("contenido idéntico", v) for v in por_hash.values() if len(v) > 1]
    dup += [(f"mismo DOI ({k})", v) for k, v in por_doi.items()
            if len(v) > 1 and not any(set(v) == set(g) for _, g in dup)]
    return dup


def main() -> int:
    problemas, revisar, ok = [], [], 0
    archivos = sorted(DATA_DIR.glob("*.pdf")) + \
        sorted((DATA_DIR / "Referencias excluidas").glob("*.pdf"))

    dups = detectar_duplicados(archivos)
    print("DUPLICADOS")
    if not dups:
        print("  ninguno\n")
    for motivo, grupo in dups:
        print(f"  {motivo}:")
        for p in grupo:
            print(f"     {p.name[:76]}  ({p.stat().st_size // 1024} KB)")
        print()

    for p in archivos:
        if p.name.startswith("TDG-ERICKFMR"):
            continue
        m = re.match(r"(.+?)\s+(\d{4})\s+-\s+", p.name)
        if not m:
            problemas.append((p.name, "el nombre no sigue «Autor Año - Título»"))
            continue
        autor, anio = m.group(1), m.group(2)
        apellido = sin_acentos(autor.split(" y ")[0].split(",")[0]).lower()

        try:
            t = sin_acentos(PdfReader(str(p)).pages[0].extract_text() or "").lower()
        except Exception as exc:  # noqa: BLE001
            problemas.append((p.name, f"ilegible: {exc}"))
            continue

        if not t.strip():
            revisar.append((p.name, "PDF escaneado sin capa de texto"))
            continue

        hay_autor = apellido in t.replace(" ", "") or apellido in t
        hay_anio = anio in t
        if hay_autor and (hay_anio or autor.split()[0] in TOLERAR_SIN_ANIO):
            ok += 1
        elif hay_autor:
            revisar.append((p.name, f"autor «{autor}» sí, año {anio} no aparece"))
        else:
            problemas.append((p.name, f"el apellido «{autor}» NO aparece en la portada"))

    print(f"VERIFICACIÓN DE {len(archivos) - 1} PDF\n")
    print(f"  Coinciden autor y año : {ok}")
    print(f"  A revisar             : {len(revisar)}")
    print(f"  Problemas             : {len(problemas)}")
    for n, r in revisar:
        print(f"\n  REVISAR  {n[:74]}\n           {r}")
    for n, r in problemas:
        print(f"\n  PROBLEMA {n[:74]}\n           {r}")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
