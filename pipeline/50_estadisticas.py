"""
50_estadisticas.py — Estadísticas de taxones, por estudio y del conjunto.

Consume la extracción completa de los artículos (40_taxones_pdf.py) y produce
lo que el dashboard necesita para responder: qué especies y géneros reporta
cada estudio, cuáles dominan en cada uno y cuáles en el conjunto.

TRES SEÑALES, y no valen lo mismo. El dashboard debe distinguirlas:

  presencia   el taxón aparece en el artículo. Señal sólida.
  menciones   cuántas veces. Proxy DÉBIL de importancia: un artículo repite un
              nombre en la introducción, en la discusión y al citar a otros.
              Sirve para ordenar dentro de un artículo, no para comparar entre
              artículos de distinta extensión.
  dominante   el propio texto lo afirma («dominant», «most abundant»…). Es la
              señal más fuerte, y la única que puede llamarse dominancia.

La base de la tesis se conserva aparte: es una selección de las cinco
principales especies por filtro, hecha a mano, y sigue siendo la referencia.
Esta extracción la complementa, no la sustituye.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIV = ROOT / "data" / "private"
DERIV = ROOT / "data" / "derived"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    tp = json.loads((PRIV / "taxones_pdf.json").read_text(encoding="utf-8"))
    regs = tp["registros"]
    estudios = {e["id"]: e for e in
                json.loads((DERIV / "estudios.json").read_text(encoding="utf-8"))}
    base = json.loads((DERIV / "taxones_global.json").read_text(encoding="utf-8"))
    msh = json.loads((DERIV / "msh_bc21.json").read_text(encoding="utf-8"))
    en_base = {t["taxon"] for t in base}
    en_msh = {e["taxon"] for e in msh["especies"]}

    # ------------------------------------------------ por estudio
    por_est = defaultdict(list)
    for r in regs:
        por_est[r["estudio_id"]].append(r)

    estudios_out = []
    for eid, rs in sorted(por_est.items()):
        e = estudios.get(eid, {})
        esp = [r for r in rs if r["rango"] == "especie"]
        dom = [r for r in rs if r["dominante_declarado"]]
        estudios_out.append({
            "estudio_id": eid,
            "titulo": e.get("titulo"),
            "autores": (e.get("autores") or [None])[0],
            "anio": e.get("anio"),
            "localidad": e.get("localidad"),
            "tipo_filtracion": e.get("tipo_filtracion"),
            "morfologia": e.get("morfologia_label"),
            "n_taxones": len({r["taxon"] for r in rs}),
            "n_especies": len({r["taxon"] for r in esp}),
            "n_generos": len({r["genero"] for r in rs if r["genero"]}),
            "n_en_base_tesis": e.get("n_registros"),
            "top_menciones": [
                {"taxon": r["taxon"], "menciones": r["menciones"],
                 "dominante": r["dominante_declarado"]}
                for r in sorted(rs, key=lambda x: -x["menciones"])[:10]],
            "dominantes_declarados": sorted({r["taxon"] for r in dom}),
            "generos": [g for g, _ in Counter(
                r["genero"] for r in rs if r["genero"]).most_common(12)],
        })

    # ------------------------------------------------ globales
    t_est = defaultdict(set)
    t_men = Counter()
    t_dom = defaultdict(set)
    t_meta = {}
    for r in regs:
        t_est[r["taxon"]].add(r["estudio_id"])
        t_men[r["taxon"]] += r["menciones"]
        if r["dominante_declarado"]:
            t_dom[r["taxon"]].add(r["estudio_id"])
        t_meta[r["taxon"]] = {"rango": r["rango"], "genero": r["genero"],
                              "familia": r["familia"], "orden": r["orden"],
                              "aphia_id": r["aphia_id"]}

    taxones = sorted(
        [{"taxon": k, **t_meta[k],
          "n_estudios": len(v), "menciones": t_men[k],
          "n_estudios_dominante": len(t_dom.get(k, ())),
          "en_base_tesis": k in en_base,
          "en_msh_bc21": k in en_msh}
         for k, v in t_est.items()],
        key=lambda d: (-d["n_estudios"], -d["n_estudios_dominante"], d["taxon"]))

    g_est = defaultdict(set)
    g_taxa = defaultdict(set)
    for r in regs:
        if r["genero"]:
            g_est[r["genero"]].add(r["estudio_id"])
            g_taxa[r["genero"]].add(r["taxon"])
    generos = sorted(
        [{"genero": g, "n_estudios": len(v), "n_taxones": len(g_taxa[g]),
          "en_msh_bc21": any(t in en_msh for t in g_taxa[g])}
         for g, v in g_est.items()],
        key=lambda d: (-d["n_estudios"], -d["n_taxones"], d["genero"]))

    fam = Counter(r["familia"] for r in regs if r["familia"])
    orden = Counter(r["orden"] for r in regs if r["orden"])

    resumen = {
        "articulos_leidos": tp["n_articulos"],
        "articulos_sin_texto": tp["escaneados"],
        "candidatos_evaluados": tp["n_candidatos"],
        "taxones_validados": len(taxones),
        "especies": sum(1 for t in taxones if t["rango"] == "especie"),
        "generos": len(generos),
        "taxones_base_tesis": len(en_base),
        "factor_ampliacion": round(len(taxones) / len(en_base), 1),
        "taxones_con_dominancia_declarada":
            sum(1 for t in taxones if t["n_estudios_dominante"]),
        "solape_con_msh": sum(1 for t in taxones if t["en_msh_bc21"]),
        "nota_metodo":
            "Presencia y menciones se extraen del texto completo de cada "
            "artículo y se validan contra WoRMS. Las menciones son un proxy "
            "débil de importancia: sirven para ordenar dentro de un artículo, "
            "no para comparar entre artículos de distinta extensión. Sólo "
            "'dominante' —afirmado por el propio texto— puede leerse como "
            "dominancia.",
    }

    # --- unión con la base de la tesis ---------------------------------
    # Ninguna de las dos fuentes contiene a la otra: la extracción no lee el
    # PDF escaneado ni los artículos sin PDF, y la base recoge taxones que
    # aparecen en tablas que el extractor no capta. La unión es mejor que
    # cualquiera de las dos por separado.
    union = defaultdict(lambda: {"base": False, "pdf": False, "n_estudios": set()})
    for t in base:
        union[t["taxon"]]["base"] = True
        union[t["taxon"]]["n_estudios"].update([f"base:{t['taxon']}"])
    for r in regs:
        u = union[r["taxon"]]
        u["pdf"] = True
        u["n_estudios"].add(r["estudio_id"])
    solo_base = sorted(k for k, v in union.items() if v["base"] and not v["pdf"])
    solo_pdf = sorted(k for k, v in union.items() if v["pdf"] and not v["base"])
    resumen["union_taxones"] = len(union)
    resumen["solo_en_base"] = len(solo_base)
    resumen["solo_en_pdf"] = len(solo_pdf)
    resumen["en_ambas"] = len(union) - len(solo_base) - len(solo_pdf)

    # rankings separados: una entrada de género agrupa un conjunto de especies
    # y no es comparable con una especie concreta
    solo_especies = [t for t in taxones if t["rango"] == "especie"]

    (DERIV / "taxones_completo.json").write_text(json.dumps({
        "resumen": resumen,
        "taxones": taxones,
        "ranking_especies": solo_especies[:120],
        "generos": generos,
        "union": {
            "total": len(union),
            "solo_en_base_tesis": solo_base,
            "solo_en_articulos": len(solo_pdf),
            "nota": "La base de la tesis y la extracción de los artículos no se "
                    "contienen la una a la otra: el extractor no lee el PDF "
                    "escaneado ni los artículos sin PDF, y la base recoge taxones "
                    "de tablas que el extractor no capta.",
        },
        "familias": [{"familia": k, "ocurrencias": v} for k, v in fam.most_common()],
        "ordenes": [{"orden": k, "ocurrencias": v} for k, v in orden.most_common()],
        "por_estudio": estudios_out,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print("ESTADÍSTICAS DE TAXONES")
    for k, v in resumen.items():
        if k != "nota_metodo":
            print(f"  {k:<34} {v}")
    print("\nTop 12 por nº de estudios que lo reportan:")
    for t in taxones[:12]:
        marcas = ("·tesis" if t["en_base_tesis"] else "      ") + \
                 (" ·MSH" if t["en_msh_bc21"] else "     ")
        print(f"  {t['taxon']:<34} {t['n_estudios']:>3} est · "
              f"{t['n_estudios_dominante']:>2} dom {marcas}")
    print("\nTop 10 géneros:")
    for g in generos[:10]:
        print(f"  {g['genero']:<22} {g['n_estudios']:>3} estudios · "
              f"{g['n_taxones']:>3} taxones{' ·MSH' if g['en_msh_bc21'] else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
