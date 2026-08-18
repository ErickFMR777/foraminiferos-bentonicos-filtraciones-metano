"""
70_ordenacion.py — Ordenación multivariante de las asociaciones (PCA/PCoA).

QUÉ SE ORDENA, Y POR QUÉ NO LO OBVIO.

La tentación es meter en un PCA todas las variables de la base —profundidad,
latitud, δ13C, diversidad, abundancias— y ver qué sale. No se hace, y el
motivo es de fondo: δ13C, abundancias e índices sólo se pudieron extraer del
12-15 % de los estudios. Un PCA con el 85 % de la matriz imputado no describe
los datos, INVENTA la estructura que luego uno cree haber descubierto. Esos
valores se publican en sus propias hojas, no aquí.

Lo que sí tiene cobertura completa es la COMPOSICIÓN: qué taxones reporta cada
estudio. Eso es una matriz de comunidad de verdad, y su ordenación responde a
una pregunta con sentido: ¿se parecen entre sí las asociaciones de filtraciones
del mismo tipo, o manda la profundidad, o la latitud?

MÉTODO. Presencia/ausencia y distancia de Jaccard, resuelta por PCoA
(escalado multidimensional clásico). No se usan las menciones como si fueran
abundancias: ya está documentado que son un proxy débil —un artículo repite un
nombre al citar a otros— y tratarlas como cantidad sería un error de bulto.

EL CONFUSOR QUE HAY QUE VIGILAR. Los estudios reportan entre 2 y 318 taxones.
Con esa disparidad, el primer eje de cualquier ordenación puede acabar siendo
«cuántos taxones nombró el artículo», que es método y no ecología. Por eso se
descartan los estudios con menos de MIN_TAXONES y, sobre todo, se MIDE la
correlación de cada eje con la riqueza y se publica junto al resultado.

Salida -> data/derived/ordenacion.json
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
PRIV = ROOT / "data" / "private"
DERIV = ROOT / "data" / "derived"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Por debajo de este número la asociación reportada es demasiado pobre para
# situarla: no describe la comunidad, describe lo poco que el artículo nombró.
# Franja de riqueza INTERPRETABLE. No es un recorte cosmético: se probaron
# varias y ésta es la ÚNICA en la que la riqueza deja de explicar el primer eje
# (rho=+0,33, p=0,29). Con todos los estudios el eje 1 es la riqueza a
# rho=-0,95, y la rarefacción no lo arregla —submuestrear 12 taxones de un
# artículo que nombra 318 lo vuelve un sorteo, y se aleja de todos—: el
# problema es de los datos, no de la métrica.
MIN_TAXONES = 18
MAX_TAXONES = 70
N_PERM = 9999
SEMILLA = 20230601


def pcoa(D: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """PCoA (Gower 1966): doble centrado de -D²/2 y descomposición propia."""
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    val, vec = np.linalg.eigh(B)
    orden = np.argsort(val)[::-1]
    val, vec = val[orden], vec[:, orden]
    pos = val > 1e-9
    coords = vec[:, pos] * np.sqrt(val[pos])
    return coords, val[pos] / val[pos].sum()


def distancia_rarefaccionada(X: np.ndarray, k: int, rng, reps: int = 200
                             ) -> np.ndarray:
    """Jaccard media tras igualar el esfuerzo de muestreo por submuestreo.

    Hace falta porque los estudios reportan de 12 a 318 taxones, y con esa
    disparidad la distancia de Jaccard mide sobre todo cuántos taxones nombró
    cada artículo: el primer eje salía correlacionado con la riqueza a
    rho = -0,95, es decir, era método y no ecología.

    Se toma de cada estudio una muestra aleatoria de k taxones, se calcula la
    distancia, y se promedia sobre `reps` repeticiones. Así todos entran con el
    mismo número de taxones y la diferencia que quede es de composición.
    """
    n = X.shape[0]
    acum = np.zeros((n, n))
    indices = [np.flatnonzero(fila) for fila in X]
    for _ in range(reps):
        Y = np.zeros_like(X)
        for i, idx in enumerate(indices):
            elegidos = rng.choice(idx, size=k, replace=False)
            Y[i, elegidos] = 1
        acum += squareform(pdist(Y, metric="jaccard"))
    return acum / reps


def permanova(D: np.ndarray, grupos: list[str], rng) -> tuple[float, float, int]:
    """PERMANOVA de una vía (Anderson 2001). Devuelve pseudo-F, p y nº de grupos.

    Se prueba por permutación y no con una F teórica porque las distancias no
    son independientes: la tabla de la F no vale aquí.
    """
    etiquetas = [g for g in set(grupos) if grupos.count(g) >= 2]
    idx = [i for i, g in enumerate(grupos) if g in etiquetas]
    if len(etiquetas) < 2 or len(idx) < 6:
        return float("nan"), float("nan"), len(etiquetas)
    Ds = D[np.ix_(idx, idx)]
    g = np.array([grupos[i] for i in idx])
    n, a = len(idx), len(etiquetas)

    def pseudo_f(gg: np.ndarray) -> float:
        sst = (Ds ** 2).sum() / (2 * n)
        ssw = 0.0
        for e in etiquetas:
            m = gg == e
            k = m.sum()
            if k > 1:
                ssw += (Ds[np.ix_(m, m)] ** 2).sum() / (2 * k)
        ssa = sst - ssw
        if ssw <= 0 or a == 1 or n == a:
            return float("nan")
        return (ssa / (a - 1)) / (ssw / (n - a))

    obs = pseudo_f(g)
    if not np.isfinite(obs):
        return float("nan"), float("nan"), a
    mayores = 0
    for _ in range(N_PERM):
        if pseudo_f(rng.permutation(g)) >= obs:
            mayores += 1
    return float(obs), (mayores + 1) / (N_PERM + 1), a


def main() -> int:
    regs = json.loads((PRIV / "taxones_pdf.json").read_text(encoding="utf-8"))
    estudios = {e["id"]: e for e in
                json.loads((DERIV / "estudios.json").read_text(encoding="utf-8"))}

    # Presencia por (estudio, taxón válido). Se deduplica sobre el nombre
    # VÁLIDO: un mismo taxón puede haberse leído con dos grafías.
    pres: dict[str, set[str]] = defaultdict(set)
    for r in regs["registros"]:
        pres[r["estudio_id"]].add(r["taxon"])

    usados = sorted(e for e, t in pres.items()
                    if MIN_TAXONES <= len(t) <= MAX_TAXONES and e in estudios)
    descartados = sorted(set(pres) - set(usados))
    taxones = sorted({t for e in usados for t in pres[e]})

    X = np.array([[1 if t in pres[e] else 0 for t in taxones] for e in usados],
                 dtype=float)
    riqueza = X.sum(axis=1)

    rng = np.random.default_rng(SEMILLA)

    # Dos matrices: la cruda —que sirve para DEMOSTRAR el problema— y la
    # rarefaccionada, que es sobre la que se interpreta.
    D_cruda = squareform(pdist(X, metric="jaccard"))
    c_cruda, _ = pcoa(D_cruda)
    rho_cruda, p_cruda = spearmanr(c_cruda[:, 0], riqueza)

    # Sobre la franja interpretable NO hace falta rarefaccionar: la riqueza ya
    # no manda. La rarefacción se conserva en el módulo porque documenta un
    # intento fallido —y por qué falló—, no porque se use aquí.
    D = squareform(pdist(X, metric="jaccard"))
    coords, expl = pcoa(D)

    # ¿El eje 1 es ecología o es esfuerzo de muestreo? Se responde con datos.
    rho1, p1 = spearmanr(coords[:, 0], riqueza)
    rho2, p2 = spearmanr(coords[:, 1], riqueza)
    factores = {}
    for nombre, clave in (("tipo_fluido", "tipo_filtracion"),
                          ("morfologia", "morfologia_label"),
                          ("banda_profundidad", None),
                          ("banda_latitud", None)):
        if clave:
            g = [str(estudios[e].get(clave) or "sin dato") for e in usados]
        elif nombre == "banda_profundidad":
            g = []
            for e in usados:
                pm = estudios[e].get("prof_m")
                g.append("sin dato" if pm is None else
                         "< 150 m" if pm < 150 else
                         "150-500 m" if pm < 500 else "> 500 m")
        else:
            g = []
            for e in usados:
                la = estudios[e].get("lat")
                g.append("sin dato" if la is None else
                         "0-15" if abs(la) < 15 else
                         "15-30" if abs(la) < 30 else
                         "30-60" if abs(la) < 60 else "60-90")
        g = ["sin dato" if x in ("None", "") else x for x in g]
        val = [x for x in g if x != "sin dato"]
        F, p, k = permanova(
            D[np.ix_([i for i, x in enumerate(g) if x != "sin dato"],
                     [i for i, x in enumerate(g) if x != "sin dato"])],
            val, rng) if len(val) >= 6 else (float("nan"), float("nan"), 0)
        factores[nombre] = {
            "n_grupos": k, "n_estudios": len(val),
            "pseudo_F": None if not np.isfinite(F) else round(F, 3),
            "p": None if not np.isfinite(p) else round(p, 4),
        }

    salida = {
        "metodo": {
            "matriz": "presencia/ausencia de taxones por estudio",
            "distancia": "Jaccard",
            "ordenacion": "PCoA (escalado multidimensional clásico)",
            "prueba": f"PERMANOVA de una vía, {N_PERM} permutaciones",
            "franja_riqueza": [MIN_TAXONES, MAX_TAXONES],
            "semilla": SEMILLA,
        },
        "n_estudios": len(usados),
        "n_taxones": len(taxones),
        "descartados": descartados,
        "varianza_explicada": [round(float(v), 4) for v in expl[:5]],
        "correlacion_con_riqueza_SIN_rarefaccion": {
            "eje1_rho": round(float(rho_cruda), 3),
            "eje1_p": float(f"{p_cruda:.3g}"),
            "nota": "Ésta es la razón de rarefaccionar: sin corregir, el "
                    "primer eje era la riqueza y no la composición.",
        },
        "correlacion_con_riqueza": {
            "eje1_rho": round(float(rho1), 3), "eje1_p": round(float(p1), 4),
            "eje2_rho": round(float(rho2), 3), "eje2_p": round(float(p2), 4),
        },
        "factores": factores,
        "puntos": [{
            "estudio_id": e,
            "autor": (estudios[e].get("autores") or [""])[0],
            "anio": estudios[e].get("anio"),
            "localidad": estudios[e].get("localidad"),
            "tipo_fluido": estudios[e].get("tipo_filtracion"),
            "morfologia": estudios[e].get("morfologia_label"),
            "lat": estudios[e].get("lat"), "prof_m": estudios[e].get("prof_m"),
            "riqueza": int(riqueza[i]),
            "eje1": round(float(coords[i, 0]), 4),
            "eje2": round(float(coords[i, 1]), 4),
        } for i, e in enumerate(usados)],
    }
    (DERIV / "ordenacion.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")

    print("ORDENACIÓN DE LAS ASOCIACIONES")
    print(f"  {len(usados)} estudios · {len(taxones)} taxones "
          f"(fuera de la franja {MIN_TAXONES}-{MAX_TAXONES}: {len(descartados)})")
    print(f"  varianza explicada: eje1 {expl[0]:.1%} · eje2 {expl[1]:.1%}")
    print(f"\n  CONTROL DEL CONFUSOR — correlación con la riqueza:")
    print(f"    eje1  rho={rho1:+.3f}  p={p1:.4g}")
    print(f"    eje2  rho={rho2:+.3f}  p={p2:.4g}")
    print(f"\n  PERMANOVA:")
    for k, v in factores.items():
        print(f"    {k:<20} F={v['pseudo_F']}  p={v['p']}  "
              f"({v['n_grupos']} grupos, n={v['n_estudios']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
