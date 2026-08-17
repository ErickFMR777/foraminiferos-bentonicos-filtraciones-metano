"""
20_build.py — Produce los datasets públicos que consume el dashboard.

Sólo escribe en data/derived/. Nada de lo que sale de aquí permite
reconstruir los documentos originales: son agregados, índices y tablas
derivadas. Los archivos fuente (PDF y Excel) no se publican ni se enlazan.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caribe_referencia as CAR  # noqa: E402
import localidades as LOC  # noqa: E402
import taxonomy as T  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PRIV = ROOT / "data" / "private"
DERIV = ROOT / "data" / "derived"

LATS = ["0-15", "15-30", "30-60", "60-90"]
PROFS = ["< 150 m", "150-500 m", "> 500 m"]


def shannon(counts: list[float]) -> float:
    tot = sum(counts)
    return -sum((c / tot) * math.log(c / tot) for c in counts if c > 0)


def simpson(counts: list[float]) -> float:
    tot = sum(counts)
    return sum((c / tot) ** 2 for c in counts if c > 0)


def main() -> int:
    bib = json.loads((PRIV / "bibliografia_clean.json").read_text(encoding="utf-8"))
    msh = json.loads((PRIV / "msh_clean.json").read_text(encoding="utf-8"))
    raw_msh = json.loads((PRIV / "msh_raw.json").read_text(encoding="utf-8"))
    xref = json.loads((PRIV / "estudios_crossref.json").read_text(encoding="utf-8"))
    DERIV.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- estudios
    by_title = {e["titulo_original"]: e for e in xref}
    estudios = []
    for titulo, n in Counter(r["estudio"] for r in bib).most_common():
        e = by_title.get(titulo, {})
        cr = e.get("crossref") or {}
        doi = cr.get("doi")
        loc = LOC.LOCALIDADES.get(doi) or LOC.SIN_DOI.get(e.get("titulo_limpio", ""), {})
        # el estudio del Mar de China sin DOI fiable se identifica por título
        if not loc:
            for k, v in LOC.SIN_DOI.items():
                if k[:50].lower() in (e.get("titulo_limpio") or "").lower():
                    loc = v
                    break
        fiable = doi and doi != "10.1021/acsestwater.3c00740.s001"
        tipo = loc.get("tipo", "frio")
        estudios.append({
            "id": e.get("id"),
            "titulo": e.get("titulo_limpio") or titulo,
            "autores": cr.get("autores") if fiable else None,
            "anio": cr.get("anio") if fiable else None,
            "revista": cr.get("revista") if fiable else None,
            "doi": doi if fiable else None,
            "referencia_verificada": bool(fiable),
            "n_registros": n,
            "tipo_filtracion": tipo,
            "es_filtracion": tipo != "no_filtracion",
            "sitios": loc.get("sitios"),
            **{k: loc.get(k) for k in
               ("localidad", "region", "lat", "lon", "prof_m", "confianza", "fuente")},
        })

    # Estudios que NO documentan filtraciones: sus registros son fauna de
    # referencia de márgenes normales, no fauna de seep. Se conservan y se
    # marcan, pero quedan fuera de los agregados que describen filtraciones.
    # El emparejamiento va por el título original, que es la llave real entre
    # los registros y la tabla de estudios.
    titulos_no_seep = {
        e["titulo_original"] for e in xref
        if LOC.LOCALIDADES.get(
            (e.get("crossref") or {}).get("doi"), {}).get("tipo") == "no_filtracion"
    }
    seep = [r for r in bib if r["estudio"] not in titulos_no_seep]
    n_no_seep = len(bib) - len(seep)
    (DERIV / "estudios.json").write_text(
        json.dumps(estudios, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------- matriz latitud x profundidad
    # La matriz describe filtraciones, así que se construye sólo con los
    # estudios que efectivamente las documentan.
    celdas = []
    for la in LATS:
        for pr in PROFS:
            sub = [r for r in seep if r["lat_banda"] == la and r["prof_banda"] == pr]
            celdas.append({
                "lat": la, "prof": pr,
                "registros": len(sub),
                "taxones": len({r["taxon"] for r in sub}),
                "estudios": len({r["estudio"] for r in sub}),
            })
    (DERIV / "matriz_lat_prof.json").write_text(
        json.dumps({
            "celdas": celdas,
            "registros_no_filtracion": n_no_seep,
            "nota_no_filtracion":
                "Se excluyen los registros de estudios que no documentan "
                "filtraciones (fauna de referencia de márgenes normales).",
            "lats": LATS, "profs": PROFS,
            # Claves explícitas: 'banda_lat' y 'lat' son cosas distintas (la
            # banda de la matriz y la coordenada geográfica). Fusionarlas con
            # un spread hacía que la coordenada pisara la banda en silencio.
            "sitio_tesis": {
                "banda_lat": "0-15",
                "banda_prof": "< 150 m",
                **LOC.MSH_BC_21,
            },
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------------ taxones global
    tx = defaultdict(lambda: {"registros": 0, "estudios": set(), "lats": set(),
                              "profs": set(), "micro": set(), "pared": None,
                              "subtipo": None, "genero": None, "genero_label": None,
                              "rango": None, "familia": None, "aphia": None,
                              "verificado": True})
    for r in bib:
        t = tx[r["taxon"]]
        t["registros"] += 1
        t["estudios"].add(r["estudio"])
        if r["lat_banda"]:
            t["lats"].add(r["lat_banda"])
        if r["prof_banda"]:
            t["profs"].add(r["prof_banda"])
        if r.get("microhabitat"):
            t["micro"].add(r["microhabitat"])
        t["pared"] = r["pared"]
        t["subtipo"] = r["subtipo"]
        t["genero"] = r["genero"]
        t["genero_label"] = r["genero_label"]
        t["rango"] = r["rango"]
        t["familia"] = r["familia"]
        t["aphia"] = r["aphia_id"]
        t["verificado"] = t["verificado"] and r["verificado_worms"]
    # Ordenado por nº de ESTUDIOS, no de registros: es la métrica robusta para
    # «el taxón más reportado». El recuento de registros depende de cuántas
    # bandas o microhábitats desglose cada artículo, y por tanto premia a los
    # estudios más detallados en lugar de a los taxones más frecuentes.
    taxones = sorted(
        [{"taxon": k, "rango": v["rango"], "registros": v["registros"],
          "n_estudios": len(v["estudios"]),
          "lats": sorted(v["lats"]), "profs": sorted(v["profs"]),
          "microhabitats": sorted(v["micro"]), "pared": v["pared"],
          "subtipo": v["subtipo"], "genero": v["genero_label"],
          "familia": v["familia"], "aphia_id": v["aphia"],
          "verificado_worms": v["verificado"]}
         for k, v in tx.items()],
        key=lambda d: (-d["n_estudios"], -d["registros"], d["taxon"]))
    (DERIV / "taxones_global.json").write_text(
        json.dumps(taxones, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------- pared por banda
    pared_banda = []
    for eje, valores, campo in (("latitud", LATS, "lat_banda"), ("profundidad", PROFS, "prof_banda")):
        for v in valores:
            sub = [r for r in bib if r[campo] == v]
            c = Counter(r["pared"] for r in sub)
            s = sum(c.values())
            pared_banda.append({
                "eje": eje, "banda": v, "n": s,
                "calcareo": round(100 * c.get("Calcareo", 0) / s, 1) if s else None,
                "aglutinado": round(100 * c.get("Aglutinado", 0) / s, 1) if s else None,
                "subtipos": dict(Counter(r["subtipo"] for r in sub if r["subtipo"])),
            })
    (DERIV / "pared_por_banda.json").write_text(
        json.dumps(pared_banda, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------------- MSH-BC-21
    total = sum(r["conteo"] for r in msh)
    especies = sorted(
        [{"taxon": r["taxon"], "taxon_original": r["taxon_original"],
          "rango": r["rango"],
          "conteo": r["conteo"], "abundancia_rel": round(100 * r["conteo"] / total, 3),
          "pared": r["pared"], "subtipo": r["subtipo"], "genero": r["genero_label"],
          "familia": r["familia"], "aphia_id": r["aphia_id"]}
         for r in msh], key=lambda d: -d["conteo"])
    cnt = [r["conteo"] for r in msh]
    H = shannon(cnt)
    S = len(msh)
    pared = Counter()
    sub = Counter()
    for r in msh:
        pared[r["pared"]] += r["conteo"]
        sub[r["subtipo"] or r["pared"]] += r["conteo"]

    # abundancias por cm y fracción
    ab = defaultdict(dict)
    for row in raw_msh["abundancias"]:
        ab[row["muestra"]][row["variable"]] = row["valores"]

    (DERIV / "msh_bc21.json").write_text(json.dumps({
        "sitio": LOC.MSH_BC_21,
        "especies": especies,
        "total_ponderado": round(total, 4),
        "indices": {
            "riqueza_S": S,
            "shannon_H": round(H, 4),
            "equidad_J": round(H / math.log(S), 4),
            "simpson_D": round(simpson(cnt), 4),
            "dominancia_top5": round(100 * sum(sorted(cnt, reverse=True)[:5]) / total, 1),
        },
        "pared": {k: round(100 * v / total, 2) for k, v in pared.items()},
        "subtipo": {k: round(100 * v / total, 2) for k, v in sub.items()},
        "pared_n_especies": dict(Counter(r["pared"] for r in msh)),
        "abundancias": ab,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # --------------------------------------------------------------- solape
    gl_bin = {T.binomen(r["taxon"]) for r in bib}
    gl_gen = {r["genero"] for r in bib}
    ms_bin = {T.binomen(r["taxon"]) for r in msh}
    ms_gen = {r["genero"] for r in msh}
    peso = defaultdict(float)
    for r in msh:
        peso[r["genero"]] += r["conteo"]
    cap = str.capitalize
    (DERIV / "solape.json").write_text(json.dumps({
        "especies": {
            "compartidas": sorted(cap(b) for b in gl_bin & ms_bin),
            "n_msh": len(ms_bin), "n_global": len(gl_bin), "n_compartidas": len(gl_bin & ms_bin),
        },
        "generos": {
            "compartidos": sorted(cap(g) for g in gl_gen & ms_gen),
            "exclusivos_msh": sorted(cap(g) for g in ms_gen - gl_gen),
            "n_msh": len(ms_gen), "n_global": len(gl_gen),
            "n_compartidos": len(gl_gen & ms_gen),
            "pct_abundancia_compartida": round(
                100 * sum(v for k, v in peso.items() if k in gl_gen) / total, 1),
        },
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------ referencia Caribe
    car = []
    for l in CAR.LOCALIDADES_CARIBE:
        car.append({**{k: v for k, v in l.items() if k != "taxones"},
                    "taxones": [{"taxon": t, "abundancia_rel": p} for t, p in l["taxones"]]})
    # añadir MSH-BC-21 como una localidad más para el contraste
    car.append({
        "id": "msh_bc21", "nombre": "MSH-BC-21 (presunta filtración)",
        "ambiente": "Plataforma / presunto seep", "fuente": "Este trabajo",
        "cita_en_tesis": "cap. 6.2",
        "lat": LOC.MSH_BC_21["lat"], "lon": LOC.MSH_BC_21["lon"],
        "nota": "52 especies; Shannon 3,43; 87% calcáreos",
        "taxones": [{"taxon": e["taxon"], "abundancia_rel": e["abundancia_rel"]}
                    for e in especies[:13]],
    })
    (DERIV / "caribe_referencia.json").write_text(
        json.dumps(car, ensure_ascii=False, indent=1), encoding="utf-8")

    print("DATASETS PÚBLICOS GENERADOS")
    for f in sorted(DERIV.glob("*.json")):
        print(f"  {f.name:28s} {f.stat().st_size / 1024:7.1f} KB")
    print(f"\n  Total: {sum(f.stat().st_size for f in DERIV.glob('*.json')) / 1024:.1f} KB")
    print(f"  Estudios georreferenciados: "
          f"{sum(1 for e in estudios if e.get('lat') is not None)}/{len(estudios)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
