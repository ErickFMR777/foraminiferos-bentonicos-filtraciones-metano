"""
taxonomy.py — Tablas de referencia taxonómica y normalización.

Base: clasificación suprageneríca estándar de foraminíferos (Loeblich & Tappan
1987; actualizada según WoRMS / World Foraminifera Database). Se usa para
detectar de forma sistemática — no a ojo — tres clases de error presentes en
las hojas originales:

  a) especies planctónicas dentro de una base declarada de bentónicos,
  b) géneros con el tipo de pared mal asignado,
  c) sinónimos y erratas que inflan el conteo de especies.

Cada corrección aplicada queda registrada en corrections.py con su motivo.
"""

from __future__ import annotations

import re
import unicodedata

# --- Pared aglutinada (test construido con partículas cementadas) ----------
AGLUTINADOS = {
    "adercotryma", "alveolophragmium", "ammobaculites",
    "ammodiscus", "ammolagena", "ammomarginulina", "ammoscalaria", "ammotium",
    "arenoparrella", "aschemocella", "astrorhiza", "barbourinella", "bathysiphon",
    "bigenerina", "bolivinopsis", "clavulina", "cribrostomoides", "crithionina",
    "cyclammina", "deuterammina", "dorothia", "eggerella", "gaudryina",
    "glomospira", "haplophragmoides", "hormosina", "hormosinella", "hyperammina",
    "karreriella", "karrerotextularia", "labrospira", "lagenammina",
    "leptohalysis", "marsipella", "martinottiella", "miliammina", "nodulina",
    "nouria", "orectostomina", "paratrochammina", "parvigenerina", "pelosina",
    "placopsilina", "plotnikovina", "portatrochammina", "psammosphaera",
    "pseudoclavulina", "recurvoides", "reophanus", "reophax", "repmanina",
    "rhabdammina", "rhizammina", "saccammina", "sahulia", "siphotextularia",
    "spiroplectammina", "spiroplectinella", "subreophax", "technitella",
    "textularia", "textulariopsis", "tholosina", "thurammina", "tritaxis",
    "trochammina", "turritellella", "usbekistania", "valvulina", "veleroninoides",
    "verneuilinulla",
}

# --- Pared calcárea porcelanácea (Miliolida) -------------------------------
PORCELANACEOS = {
    "adelosina", "affinetrina", "agglutinella", "amphisorus", "archaias",
    "articulina", "biloculinella", "borelis", "cribromiliolinella", "cycloforina",
    "edentostomina", "hauerina", "idalina", "lachlanella", "massilina", "miliola",
    "miliolinella", "nodobaculariella", "nummoloculina", "peneroplis",
    "pseudotriloculina", "pyrgo", "quinqueloculina", "schlumbergerina",
    "sigmoilina", "sigmoilinita", "sigmoilinopsis", "sigmoilopsis", "sorites",
    "spiroloculina", "triloculina", "vertebralina", "wiesnerella",
}

# --- Pared calcárea aragonítica -------------------------------------------
ARAGONITICOS = {
    "ceratobulimina", "epistomina", "hoeglundina", "lamarckina", "robertina",
    "robertinoides",
}

# --- Pared calcárea monocristalina (Spirillinata) --------------------------
# Estrictamente no es hialina lamelar ni porcelanácea. Para el análisis
# FBC/FBA agrupa con los calcáreos; se documenta la distinción.
MONOCRISTALINOS = {"mychostomina", "patellina", "spirillina", "turrispirillina"}

# --- Géneros PLANCTÓNICOS: no pertenecen a una base de bentónicos ----------
# Ojo: Globocassidulina y Globobulimina son BENTÓNICOS pese al prefijo.
PLANCTONICOS = {
    "beella", "berggrenia", "candeina", "catapsydrax", "dentoglobigerina",
    "globigerina", "globigerinatella", "globigerinella", "globigerinita",
    "globigerinoides", "globoconella", "globoquadrina", "globorotalia",
    "globorotaloides", "globoturborotalita", "hastigerina", "hastigerinella",
    "hirsutella", "menardella", "neogloboquadrina", "orbulina", "praeorbulina",
    "pulleniatina", "sphaeroidinella", "sphaeroidinellopsis", "tenuitella",
    "trilobatus", "truncorotalia", "turborotalita",
}

# Todo lo demás calcáreo se asume hialino (Rotaliida, Buliminida, Lagenida…)


LIGADURAS = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
             "ﬅ": "ft", "ﬆ": "st"}
_LIG = "".join(LIGADURAS)


def normalizar_pdf(s: str) -> str:
    """Repara el texto extraído de un PDF antes de buscar nombres en él.

    Los PDF de editorial usan ligaduras tipográficas y los extractores suelen
    dejar espacios espurios alrededor: «wuellerstor ﬁ» en vez de
    «wuellerstorfi», «identi ﬁcation» en vez de «identification». Sin esta
    reparación, Cibicidoides wuellerstorfi —el segundo taxón más reportado del
    mundo— aparece truncado 188 veces y se pierde.
    """
    s = re.sub(rf"(?<=\w)\s+(?=[{_LIG}])", "", s)
    s = re.sub(rf"(?<=[{_LIG}])\s+(?=\w)", "", s)
    for k, v in LIGADURAS.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", " ", s)


def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def normalize(name: str) -> str:
    """Normaliza un nombre para comparación: sin acentos, sin sufijos abiertos."""
    s = strip_accents(str(name)).lower().strip()
    s = re.sub(r"\(\?\)|\?", " ", s)
    s = re.sub(r"\b(spp?|sp)\b\.?", " ", s)
    s = re.sub(r"\bsubsp\b\.?", " ", s)
    s = re.sub(r"\b(cf|aff)\b\.?", " ", s)
    s = re.sub(r",.*$", "", s)          # quita autoría: "Reuss, 1862"
    s = re.sub(r"[^a-z ]", " ", s)
    return " ".join(s.split())


def genus_of(name: str) -> str:
    """Género en minúscula, para comparar y agrupar."""
    n = normalize(name)
    return n.split()[0] if n else ""


def genus_label(name: str) -> str:
    """Género con inicial mayúscula, para mostrar en la interfaz.

    Los nombres de género se escriben capitalizados por convención
    taxonómica; usar la forma normalizada en las etiquetas produciría
    'uvigerina' en los gráficos.
    """
    g = genus_of(name)
    return g.capitalize() if g else ""


def rango(name: str) -> str:
    """'especie' si el nombre es binomial, 'genero' si es nomenclatura abierta.

    Importa para el ranking: una entrada de género agrupa un conjunto de
    especies y no es comparable con una especie concreta.
    """
    return "especie" if len(normalize(name).split()) >= 2 else "genero"


def binomen(name: str) -> str:
    """Devuelve 'genero especie' o sólo el género si es una entrada abierta."""
    return " ".join(normalize(name).split()[:2])


def expected_wall(name: str) -> tuple[str | None, str | None]:
    """(pared, subtipo) esperados según el género. None si no hay regla."""
    g = genus_of(name)
    if not g:
        return None, None
    if g in PLANCTONICOS:
        return "PLANCTONICO", None
    if g in AGLUTINADOS:
        return "Aglutinado", None
    if g in PORCELANACEOS:
        return "Calcareo", "Porcelanaceo"
    if g in ARAGONITICOS:
        return "Calcareo", "Aragonito"
    if g in MONOCRISTALINOS:
        return "Calcareo", "Monocristalino"
    return None, None


def canon_wall(raw: str | None) -> str | None:
    """Unifica el vocabulario divergente entre los dos libros."""
    if not raw:
        return None
    s = strip_accents(str(raw)).lower().strip()
    if s.startswith("aglut"):
        return "Aglutinado"
    if s.startswith("calc"):
        return "Calcareo"
    return raw.strip()


def canon_subtype(raw: str | None) -> str | None:
    """'Porcelanacea' / 'Porecelanaceo' / 'Porcelanáceo' -> 'Porcelanaceo'."""
    if not raw:
        return None
    s = strip_accents(str(raw)).lower().strip()
    if s.startswith(("porcel", "porecel", "porcl")):
        return "Porcelanaceo"
    if s.startswith("hialin"):
        return "Hialino"
    if s.startswith("aragon"):
        return "Aragonito"
    if s.startswith("monocrist"):
        return "Monocristalino"
    return raw.strip()
