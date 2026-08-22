"""
08_organizar.py — Renombra los PDF y separa los que no alimentan el análisis.

Renombra a «Autor Año - Título.pdf» y mueve a «Referencias excluidas/» los
que no aportan datos a la base, cada uno con su motivo.

Escribe un manifiesto con el mapeo nombre antiguo -> nombre nuevo, de modo
que la operación sea reversible y quede constancia de qué se movió y por qué.

Idempotente: si un archivo ya tiene el nombre correcto, no hace nada.
"""

from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("THESIS_DATA_DIR", ROOT / "Data_nosubiralrepo"))
EXCL_DIR = DATA_DIR / "Referencias excluidas"
PRIV = ROOT / "data" / "private"
DERIV = ROOT / "data" / "derived"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# PDF que NO alimentan el análisis, con el motivo que se publica en el informe
EXCLUIDOS: dict[str, dict] = {
    "10.1029/pa005i002p00161": dict(
        autor="McCorkle", anio=1990,
        titulo="The influence of microhabitats on the carbon isotopic composition "
               "of deep-sea benthic foraminifera",
        motivo="No es un estudio de filtración. Son testigos de caja en márgenes "
               "continentales normales del Atlántico y el Pacífico; documenta el "
               "gradiente δ13C entre taxones infaunales y epifaunales, que es la "
               "línea base frente a la que se mide una señal de metano, no la "
               "señal misma. Aportaba 18 registros a la base, 8 de ellos en la "
               "banda tropical 0-15°, lo que hacía parecer esa franja mejor "
               "cubierta de lo que está."),
    "10.1017/s0025315411001421": dict(
        autor="Gracia", anio=2012,
        titulo="Methane seep molluscs from the Sinu-San Jacinto fold belt in the "
               "Caribbean Sea of Colombia",
        motivo="No trata foraminíferos sino moluscos quimiosimbiontes. Es "
               "evidencia independiente valiosa de que la filtración existe en el "
               "área de estudio de la tesis, pero no aporta taxones a la base. Se "
               "conserva como respaldo de la narrativa, no como dato."),
    "10.15446/rbct.n51.96150": dict(
        autor="Puerres, Barragán-Jacksson y Bernal", anio=2022,
        titulo="Review of foraminifera methodologies related to hydrocarbon seeps "
               "on the ocean floor - implications for the Colombian Caribbean",
        motivo="Revisión metodológica sin datos primarios propios: no reporta "
               "asociaciones de foraminíferos de las que extraer taxones. Útil "
               "para contrastar criterios de muestreo. Del mismo grupo y el mismo "
               "año que la tesis, por lo que además conviene revisarlo para "
               "descartar circularidad entre ambas fuentes."),
}

# PDF que sí se usan pero todavía no están en la base: pendientes de integrar
PENDIENTES: dict[str, dict] = {
    "10.1016/j.jsames.2024.105103": dict(
        autor="Barragán-Jacksson y Bernal", anio=2024,
        titulo="Benthic foraminifera as bioindicators of gas seep intensity in the "
               "offshore zone of the Sinu fold belt"),
    "10.1016/j.epsl.2025.119558": dict(
        autor="Babineaux", anio=2025,
        titulo="Decoupling short- and long-term methane seepage dynamics - Pyrgo "
               "spp. d13C records at Woolsey Mound, Gulf of Mexico"),
    "10.1016/j.jsames.2015.03.003": dict(
        autor="Fiorini", anio=2015,
        titulo="Recent benthic foraminifera from the Caribbean continental slope "
               "and shelf off west of Colombia"),
    "10.1016/j.oregeorev.2021.104247": dict(
        autor="Li", anio=2021,
        titulo="Impact of methane seepage dynamics on the abundance of benthic "
               "foraminifera in gas hydrate bearing sediments"),
}


def limpiar(s: str, maxlen: int = 105) -> str:
    """Nombre de archivo válido en Windows y legible."""
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r'[<>:"/\\|?*]', "-", s)
    s = re.sub(r"[\x00-\x1f]", "", s)
    s = re.sub(r"\s+", " ", s).strip(" .")
    if len(s) > maxlen:
        s = s[:maxlen].rsplit(" ", 1)[0] + "…"
    return s


def nombre(autor: str, anio, titulo: str) -> str:
    a = (autor or "Anonimo").split(",")[0].strip()
    return limpiar(f"{a} {anio or 's.f.'} - {titulo}") + ".pdf"


def main() -> int:
    ev = json.loads((PRIV / "pdfs_evidencia.json").read_text(encoding="utf-8"))
    estudios = {e["doi"]: e for e in
                json.loads((DERIV / "estudios.json").read_text(encoding="utf-8"))
                if e.get("doi")}

    # En varias entradas la hoja original guardaba la cita APA completa en vez
    # del título. Para nombrar archivos se prefiere el título que devolvió
    # CrossRef, que es el real.
    xref = json.loads((PRIV / "estudios_crossref.json").read_text(encoding="utf-8"))
    titulo_real = {}
    for x in xref:
        cr = x.get("crossref") or {}
        if cr.get("doi") and cr.get("titulo_crossref"):
            titulo_real[cr["doi"].lower()] = cr["titulo_crossref"]

    EXCL_DIR.mkdir(exist_ok=True)
    manifiesto, sin_clasificar = [], []

    for r in ev:
        src = DATA_DIR / r["archivo"]
        if not src.exists():
            continue
        doi = (r.get("doi_pdf") or "").lower()

        # El emparejado por prefijo es DELIBERADO: el DOI leído del PDF llega
        # a menudo truncado por un salto de línea (Fontanier 2014 se leía
        # `…dsr.2014.08.01`, sin el último dígito). Pero un prefijo corto
        # emparejaría con el primer estudio que empiece igual, que es la clase
        # de falso positivo que ya archivó un artículo con el nombre de otro.
        # De ahí el mínimo: por debajo se exige coincidencia exacta.
        MIN_PREFIJO = 12

        def casa(k: str) -> bool:
            k = k.lower()
            if not doi:
                return False
            if doi == k:
                return True
            largo = min(len(doi), len(k))
            return largo >= MIN_PREFIJO and (doi.startswith(k) or k.startswith(doi))

        excl = next((v for k, v in EXCLUIDOS.items() if casa(k)), None)
        pend = next((v for k, v in PENDIENTES.items() if casa(k)), None)
        est = next((e for k, e in estudios.items() if casa(k)), None)
        canonico = next((k for k in estudios if casa(k)), None)

        if excl:
            nuevo, destino, estado = nombre(excl["autor"], excl["anio"], excl["titulo"]), \
                EXCL_DIR, "excluido"
            motivo = excl["motivo"]
        elif pend:
            nuevo, destino, estado = nombre(pend["autor"], pend["anio"], pend["titulo"]), \
                DATA_DIR, "pendiente de integrar"
            motivo = "Cumple los criterios pero todavía no se han extraído sus taxones."
        elif est:
            autor = (est.get("autores") or ["Anonimo"])[0].split(",")[0]
            t = titulo_real.get((est.get("doi") or "").lower()) or est["titulo"]
            t = re.sub(r"<[^>]+>", "", t)          # CrossRef mete <sup>…</sup>
            nuevo, destino, estado = nombre(autor, est.get("anio"), t), \
                DATA_DIR, "en uso"
            motivo = f"Aporta {est['n_registros']} registros a la base."
        else:
            sin_clasificar.append(r["archivo"])
            continue

        dst = destino / nuevo
        if src.resolve() == dst.resolve():
            accion = "sin cambios"
        else:
            if dst.exists():
                dst = destino / (dst.stem + f" ({doi[-6:]})" + dst.suffix)
            src.rename(dst)
            accion = "renombrado" + (" y movido" if destino != DATA_DIR else "")
        manifiesto.append({
            "antes": r["archivo"], "despues": dst.name,
            "carpeta": "Referencias excluidas" if destino == EXCL_DIR else ".",
            # El DOI del manifiesto es el CANÓNICO del estudio, no el que se
            # leyó del PDF: ese puede venir truncado, y entonces cualquier
            # cruce posterior por este campo pierde el estudio en silencio.
            "doi": canonico or doi or None,
            "doi_leido_del_pdf": doi or None,
            "estado": estado, "motivo": motivo, "accion": accion,
        })

    (PRIV / "manifiesto_pdfs.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter
    c = Counter(m["estado"] for m in manifiesto)
    print(f"{len(manifiesto)} PDF procesados")
    for k, v in c.most_common():
        print(f"  {k:<24} {v}")
    if sin_clasificar:
        print(f"\nSIN CLASIFICAR ({len(sin_clasificar)}):")
        for f in sin_clasificar:
            print(f"   {f}")
    print(f"\nManifiesto -> {PRIV / 'manifiesto_pdfs.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
