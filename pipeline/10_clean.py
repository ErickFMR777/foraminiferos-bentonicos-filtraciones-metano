"""
10_clean.py — Aplica el registro de correcciones y produce el dataset limpio.

Entrada : data/private/{bibliografia_raw,msh_raw,worms_resolved}.json
Salida  : data/private/{bibliografia_clean,msh_clean}.json   (privado)
          data/derived/correcciones.json                     (público)

El log de correcciones es público a propósito: es la pieza que permite a un
lector reconstruir la distancia entre el manuscrito de 2023 y estos datos.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corrections as C  # noqa: E402
import taxonomy as T  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PRIV = ROOT / "data" / "private"
DERIV = ROOT / "data" / "derived"

LOG: list[dict] = []


def log(tipo: str, archivo: str, desde: str, hacia: str | None, motivo: str,
        fuente: str = "", impacto: str = "", confianza: str = "alta", n: int = 1) -> None:
    LOG.append({
        "tipo": tipo, "archivo": archivo, "desde": desde, "hacia": hacia,
        "motivo": motivo, "fuente": fuente, "impacto": impacto,
        "confianza": confianza, "registros_afectados": n,
    })


def build_taxon_map(worms: dict) -> dict[str, dict]:
    """nombre crudo -> taxón canónico, registrando cada cambio."""
    tmap: dict[str, dict] = {}
    for raw, w in worms.items():
        manual = C.MANUAL.get(raw)
        if manual:
            tmap[raw] = {
                "nombre": manual["valid_name"],
                "aphia": None,
                "verificado": True,
                "confianza": manual["confianza"],
            }
            continue
        if not w.get("found"):
            tmap[raw] = {
                "nombre": raw, "aphia": None,
                "verificado": False, "confianza": "sin_verificar",
            }
            continue
        valid = w.get("valid_name") or w.get("matched") or raw
        tmap[raw] = {
            "nombre": valid,
            "aphia": w.get("valid_aphia") or w.get("aphia"),
            "verificado": True,
            "confianza": "alta",
            "rank": w.get("rank"),
            "family": w.get("family"),
            "order": w.get("order"),
            "status_original": w.get("status"),
            "unaccept_reason": w.get("unaccept_reason"),
        }
    return tmap


def clean_bibliografia(rows: list[dict], tmap: dict) -> list[dict]:
    out, excl = [], Counter()
    pared_idx = {(n, a): (p, s, m) for n, a, p, s, m in C.PARED}

    for r in rows:
        raw = (r.get("especie_raw") or "").strip()
        if not raw:
            continue
        if raw in C.EXCLUIR_PLANCTONICOS:
            excl["planctonico:" + raw] += 1
            continue
        if raw in C.EXCLUIR_PLACEHOLDER:
            excl["placeholder:" + raw] += 1
            continue

        tx = tmap.get(raw, {"nombre": raw, "verificado": False, "confianza": "sin_verificar"})
        pared = T.canon_wall(r.get("pared_raw"))
        sub = T.canon_subtype(r.get("subtipo_raw"))

        fix = pared_idx.get((raw, "A"))
        if fix:
            pared, sub = fix[0], fix[1]

        disc = r.get("discriminacion")
        disc_cod, disc_lbl = C.DISCRIMINACION_VOCAB.get(disc, (None, None))

        out.append({
            "estudio": r.get("titulo"),
            "taxon_original": raw,
            "taxon": tx["nombre"],
            "aphia_id": tx.get("aphia"),
            "verificado_worms": tx.get("verificado", False),
            "confianza": tx.get("confianza", "alta"),
            "genero": T.genus_of(tx["nombre"]),
            "genero_label": T.genus_label(tx["nombre"]),
            "rango": T.rango(tx["nombre"]),
            "familia": tx.get("family"),
            "orden": tx.get("order"),
            "pared": pared,
            "subtipo": sub if pared == "Calcareo" else None,
            "lat_banda": r.get("lat_banda"),
            "prof_banda": r.get("prof_banda"),
            "discriminacion": disc,
            "microhabitat": disc_cod,
            "microhabitat_label": disc_lbl,
        })

    # --- deduplicación de filas idénticas -------------------------------
    if C.DEDUPLICAR:
        vistos: set[tuple] = set()
        unicos, dups = [], []
        for r in out:
            k = tuple(r[c] for c in C.CLAVE_DUPLICADO)
            if k in vistos:
                dups.append(r)
            else:
                vistos.add(k)
                unicos.append(r)
        for r in dups:
            log("duplicado", "A", f"{r['taxon']} — {(r['estudio'] or '')[:45]}", None,
                "Fila idéntica en estudio, taxón, banda latitudinal, banda de "
                "profundidad y microhábitat. Contar dos veces la misma observación "
                "infla el ranking global de taxones.",
                "Detección automática por clave compuesta",
                "Reduce el total de registros; no altera el nº de estudios por taxón.")
        out = unicos

    for k, n in excl.items():
        kind, name = k.split(":", 1)
        if kind == "planctonico":
            log("exclusion", "A", name, None,
                "Especie planctónica en una base declarada de foraminíferos bentónicos.",
                "WoRMS / posición sistemática",
                "Reduce la riqueza global de 175 a 171 taxones antes de sinonimizar.",
                n=n)
        else:
            log("exclusion", "A", name, None,
                "Marcador de posición sin contenido taxonómico.", "", "", n=n)
    return out


def recuperar_del_borrador(borrador: list[dict], maestra: list[dict],
                           tmap: dict) -> list[dict]:
    """Reincorpora los estudios descartados que sí cumplen el criterio.

    La hoja borrador carece de columna de tipo de pared, así que aquí se
    DERIVA de la posición sistemática del género. Es una propiedad taxonómica
    estable, no una observación de campo, por lo que derivarla es legítimo —
    pero queda marcado con pared_derivada para no confundirla con un dato
    leído del original.
    """
    en_maestra = {(r["titulo"] or "")[:60].lower() for r in maestra}
    out = []
    n_antes = 0
    for clave, meta in C.RECUPERAR.items():
        filas = [r for r in borrador
                 if clave.lower() in (r["titulo"] or "").lower()
                 and (r["titulo"] or "")[:60].lower() not in en_maestra]
        if not filas:
            continue
        for r in filas:
            raw = (r.get("especie_raw") or "").strip()
            if not raw or raw in (C.EXCLUIR_PLANCTONICOS | C.EXCLUIR_PLACEHOLDER):
                continue
            tx = tmap.get(raw, {"nombre": raw, "verificado": False,
                                "confianza": "sin_verificar"})
            pared, sub = T.expected_wall(tx["nombre"])
            if pared == "PLANCTONICO":
                continue
            if pared is None:            # sin regla de género: hialino por defecto
                pared, sub = "Calcareo", "Hialino"
            disc = r.get("discriminacion")
            disc_cod, disc_lbl = C.DISCRIMINACION_VOCAB.get(disc, (None, None))
            out.append({
                "estudio": r.get("titulo"),
                "taxon_original": raw,
                "taxon": tx["nombre"],
                "aphia_id": tx.get("aphia"),
                "verificado_worms": tx.get("verificado", False),
                "confianza": tx.get("confianza", "alta"),
                "genero": T.genus_of(tx["nombre"]),
                "genero_label": T.genus_label(tx["nombre"]),
                "rango": T.rango(tx["nombre"]),
                "familia": tx.get("family"),
                "orden": tx.get("order"),
                "pared": pared,
                "subtipo": sub if pared == "Calcareo" else None,
                "pared_derivada": True,
                "lat_banda": r.get("lat_banda"),
                "prof_banda": r.get("prof_banda"),
                "discriminacion": disc,
                "microhabitat": disc_cod,
                "microhabitat_label": disc_lbl,
                "recuperado": True,
                "recuperado_confianza": meta["confianza"],
                "recuperado_reparo": meta.get("reparo"),
            })
        añadidos = len(out) - n_antes
        n_antes = len(out)
        log("recuperacion", "A", clave, "reincorporado", meta["motivo"],
            "Revisión de las exclusiones del filtrado original",
            f"Añade {añadidos} registros a la base ampliada "
            f"(de {len(filas)} filas del borrador; el resto eran planctónicos "
            "o filas sin taxón).",
            confianza=meta["confianza"], n=añadidos)
    return out


def clean_msh(rows: list[dict], tmap: dict) -> list[dict]:
    out = []
    pared_idx = {(n, a): (p, s, m) for n, a, p, s, m in C.PARED}
    for r in rows:
        raw = (r.get("especie_raw") or "").strip()
        tx = tmap.get(raw, {"nombre": raw, "verificado": False, "confianza": "sin_verificar"})
        pared = T.canon_wall(r.get("pared_raw"))
        sub = T.canon_subtype(r.get("subtipo_raw"))
        fix = pared_idx.get((raw, "B"))
        if fix:
            pared, sub = fix[0], fix[1]
        out.append({
            "taxon_original": raw,
            "taxon": tx["nombre"],
            "aphia_id": tx.get("aphia"),
            "verificado_worms": tx.get("verificado", False),
            "genero": T.genus_of(tx["nombre"]),
            "genero_label": T.genus_label(tx["nombre"]),
            "rango": T.rango(tx["nombre"]),
            "familia": tx.get("family"),
            "orden": tx.get("order"),
            "pared": pared,
            "subtipo": sub if pared == "Calcareo" else None,
            "conteo": r["total"],
        })
    return out


def main() -> int:
    raw_bib = json.loads((PRIV / "bibliografia_raw.json").read_text(encoding="utf-8"))
    raw_msh = json.loads((PRIV / "msh_raw.json").read_text(encoding="utf-8"))
    worms = json.loads((PRIV / "worms_resolved.json").read_text(encoding="utf-8"))

    tmap = build_taxon_map(worms)

    # --- registrar cambios de nombre ---
    counts = Counter(r["especie_raw"] for r in raw_bib["maestra"] if r.get("especie_raw"))
    counts.update(r["especie_raw"] for r in raw_msh["especies"] if r.get("especie_raw"))
    excluidos = C.EXCLUIR_PLANCTONICOS | C.EXCLUIR_PLACEHOLDER
    for raw, tx in sorted(tmap.items()):
        if tx["nombre"] == raw or raw in excluidos:
            continue  # los excluidos ya se registran como exclusión
        w = worms.get(raw, {})
        manual = C.MANUAL.get(raw)
        # Distinguir qué clase de cambio es realmente. Tratar
        # "Uvigerina spp." -> "Uvigerina" como una actualización taxonómica
        # exageraría los errores del manuscrito: es sólo nomenclatura abierta.
        raw_core = T.normalize(raw)          # ya elimina sp./spp./(?)/autoría
        valid_core = T.normalize(tx["nombre"])
        mismo_genero = T.genus_of(raw) == T.genus_of(tx["nombre"])

        if manual:
            tipo, motivo = manual["tipo"], f"Resuelto vía «{manual['via']}» contra WoRMS."
        elif raw_core == valid_core or raw_core.startswith(valid_core + " "):
            # el segundo caso cubre la autoría residual: "Ammodiscus Reuss"
            tipo = "normalizacion"
            motivo = ("Nomenclatura abierta: se retira el calificador (sp., spp., «?», "
                      "autoría) para unificar el taxón. No es un error del manuscrito.")
        elif T.strip_accents(raw_core) == T.strip_accents(valid_core):
            tipo = "errata"
            motivo = "Diferencia de acentuación respecto de la grafía latina válida."
        elif w.get("status") in ("unaccepted", "superseded combination") and not mismo_genero:
            tipo = "actualizacion"
            motivo = (f"WoRMS marca el nombre como «{w.get('status')}»"
                      + (f": {w['unaccept_reason']}" if w.get("unaccept_reason") else "")
                      + ". El nombre era de uso corriente cuando se escribió la tesis.")
        elif w.get("match_type") in ("phonetic", "near_1", "near_2") or mismo_genero:
            tipo = "errata"
            motivo = ("Grafía incorrecta del epíteto; WoRMS remite a la forma válida "
                      "dentro del mismo género.")
        else:
            tipo = "actualizacion"
            motivo = "Nombre no aceptado; WoRMS remite al taxón válido."
        log(tipo, "A/B", raw, tx["nombre"], motivo,
            f"WoRMS AphiaID {tx.get('aphia')}" if tx.get("aphia") else "WoRMS",
            confianza=tx.get("confianza", "alta"), n=counts.get(raw, 0))

    # --- registrar reclasificaciones de pared ---
    for nombre, arch, pared, sub, motivo in C.PARED:
        log("reclasificacion_pared", arch, nombre,
            f"{pared}/{sub}" if sub else pared, motivo,
            "Loeblich & Tappan (1987); WoRMS", n=counts.get(nombre, 0))

    # --- no verificados ---
    for nombre in sorted(C.NO_VERIFICADOS):
        log("sin_verificar", "A", nombre, nombre,
            "WoRMS no reconoce este binomio bajo ninguna grafía probada. Se conserva "
            "el nombre original y se marca como no verificado.",
            "WoRMS", confianza="sin_verificar", n=counts.get(nombre, 0))

    # --- aritmética ---
    for a in C.ARITMETICA:
        log("aritmetica", a["archivo"], a["donde"], None, a["detalle"], "", a["efecto"])

    bib = clean_bibliografia(raw_bib["maestra"], tmap)
    for r in bib:
        r.setdefault("recuperado", False)
        r.setdefault("pared_derivada", False)
    recuperados = recuperar_del_borrador(raw_bib["borrador"], raw_bib["maestra"], tmap)
    bib = bib + recuperados
    msh = clean_msh(raw_msh["especies"], tmap)

    # exclusiones que se mantienen: se registran para dejar trazable la curación
    for clave, motivo in C.EXCLUSIONES_CONFIRMADAS.items():
        log("exclusion_confirmada", "A", clave, None, motivo,
            "Revisión de las exclusiones del filtrado original",
            "Se mantiene fuera de la base.", n=0)

    # --- efecto medible de las correcciones ---
    def wall_split(rows, weight=None):
        tot = Counter()
        for r in rows:
            tot[r["pared"]] += r[weight] if weight else 1
        s = sum(tot.values())
        return {k: round(100 * v / s, 2) for k, v in tot.items()}, s

    antes_msh = Counter()
    for r in raw_msh["especies"]:
        antes_msh[T.canon_wall(r["pared_raw"])] += r["total"]
    s0 = sum(antes_msh.values())
    despues_msh, s1 = wall_split(msh, "conteo")

    resumen = {
        "riqueza_global_antes": len({r["especie_raw"] for r in raw_bib["maestra"] if r.get("especie_raw")}),
        "riqueza_global_despues": len({r["taxon"] for r in bib}),
        "registros_globales_antes": len(raw_bib["maestra"]),
        "registros_globales_despues": len(bib),
        "msh_fbc_antes": round(100 * antes_msh["Calcareo"] / s0, 2),
        "msh_fbc_despues": despues_msh.get("Calcareo"),
        "msh_fba_antes": round(100 * antes_msh["Aglutinado"] / s0, 2),
        "msh_fba_despues": despues_msh.get("Aglutinado"),
        "msh_riqueza_antes": len(raw_msh["especies"]),
        "msh_riqueza_despues": len({r["taxon"] for r in msh}),
    }

    PRIV.mkdir(parents=True, exist_ok=True)
    DERIV.mkdir(parents=True, exist_ok=True)
    (PRIV / "bibliografia_clean.json").write_text(json.dumps(bib, ensure_ascii=False, indent=1), encoding="utf-8")
    (PRIV / "msh_clean.json").write_text(json.dumps(msh, ensure_ascii=False, indent=1), encoding="utf-8")
    (DERIV / "correcciones.json").write_text(
        json.dumps({"resumen": resumen, "correcciones": LOG}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    print("LIMPIEZA COMPLETA")
    print(f"  Registros globales : {resumen['registros_globales_antes']} -> {resumen['registros_globales_despues']}")
    print(f"  Riqueza global     : {resumen['riqueza_global_antes']} -> {resumen['riqueza_global_despues']} taxones")
    print(f"  MSH riqueza        : {resumen['msh_riqueza_antes']} -> {resumen['msh_riqueza_despues']}")
    print(f"  MSH calcáreos      : {resumen['msh_fbc_antes']}% -> {resumen['msh_fbc_despues']}%")
    print(f"  MSH aglutinados    : {resumen['msh_fba_antes']}% -> {resumen['msh_fba_despues']}%")
    print(f"  Correcciones registradas: {len(LOG)}")
    print("  " + " · ".join(f"{k}={v}" for k, v in Counter(c['tipo'] for c in LOG).most_common()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
