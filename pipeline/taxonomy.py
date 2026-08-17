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
    n = normalize(name)
    return n.split()[0] if n else ""


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
