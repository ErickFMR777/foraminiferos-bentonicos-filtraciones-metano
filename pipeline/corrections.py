"""
corrections.py — Registro explícito y auditable de correcciones.

Toda desviación respecto de los archivos originales de la tesis queda aquí,
con su motivo, su fuente y la cifra del manuscrito que altera. El dashboard
publica este registro: el objetivo no es disimular los errores del trabajo
original sino dejar la trazabilidad a la vista.

Se distinguen cinco tipos, y la distinción importa:

  errata                 el nombre estaba mal escrito o mal transcrito
  actualizacion          el nombre era correcto en nov-2022 (fecha declarada
                         en la tesis) pero WoRMS lo ha reclasificado desde
                         entonces. NO es un error del autor.
  exclusion              el registro no pertenece a la base (planctónicos en
                         una base de bentónicos, marcadores de posición)
  reclasificacion_pared  el tipo de pared contradice la posición sistemática
                         del género
  aritmetica             inconsistencia numérica interna del libro
"""

from __future__ import annotations

# --- Exclusiones ----------------------------------------------------------
# Géneros planctónicos dentro de una base declarada de foraminíferos
# BENTÓNICOS. Su presencia infla la riqueza y distorsiona los porcentajes.
EXCLUIR_PLANCTONICOS = {
    "Neogloboquadrina pachyderma",
    "Globigerinoides ruber",
    "Globorotalia menardii",
    "Globigerinella obesa",
}

# Marcadores de posición sin valor taxonómico
EXCLUIR_PLACEHOLDER = {"Unknown calcareous"}

# --- Reclasificaciones de pared ------------------------------------------
# (nombre tal como aparece, archivo, pared correcta, subtipo, motivo)
PARED: list[tuple[str, str, str, str | None, str]] = [
    (
        "Glomospira irregularis", "A", "Aglutinado", None,
        "Glomospira es un género aglutinado (Ammodiscidae, orden Lituolida); "
        "la hoja lo registra como calcáreo porcelanáceo.",
    ),
    (
        "Glomospira gordialis", "A", "Aglutinado", None,
        "Glomospira es un género aglutinado (Ammodiscidae, orden Lituolida); "
        "la hoja lo registra como calcáreo porcelanáceo.",
    ),
    (
        "Triloculina sp.", "A", "Calcareo", "Porcelanaceo",
        "Triloculina es un miliólido de pared porcelanácea; "
        "la hoja lo registra como hialino.",
    ),
    (
        "Ammodiscus sp. Reuss, 1862", "B", "Aglutinado", None,
        "Ammodiscus es un género aglutinado (Ammodiscidae); la hoja lo "
        "registra como calcáreo porcelanáceo. Es la corrección de mayor "
        "impacto numérico del trabajo.",
    ),
    (
        "Spirillina sp.", "B", "Calcareo", "Monocristalino",
        "Spirillina (Spirillinida) tiene pared calcárea monocristalina, no "
        "porcelanácea. Sigue contando como calcárea para la razón FBC/FBA, "
        "por lo que este cambio no altera ese porcentaje.",
    ),
]

# --- Resoluciones taxonómicas manuales ------------------------------------
# Casos donde la coincidencia exacta falla y se verificó una grafía
# alternativa contra WoRMS. 'confianza' media = cambio de género, conviene
# contrastar con la fuente primaria antes de publicar.
MANUAL: dict[str, dict] = {
    "Globobulimina spinifera": {
        "valid_name": "Praeglobobulimina spinescens",
        "via": "Globobulimina spinescens",
        "tipo": "errata",
        "confianza": "media",
    },
    "Loxostomum pseudobeyrichi": {
        "valid_name": "Euloxostomum pseudobeyrichi",
        "via": "Bolivina pseudobeyrichi",
        "tipo": "actualizacion",
        "confianza": "media",
    },
    "Parafissurina kerguelenensis": {
        "valid_name": "Fissurina staphyllearia",
        "via": "Fissurina kerguelenensis",
        "tipo": "actualizacion",
        "confianza": "media",
    },
    "Valvulineria auricana": {
        "valid_name": "Valvulineria araucana",
        "via": "Valvulineria araucana",
        "tipo": "errata",
        "confianza": "alta",
    },
}

# Taxones que WoRMS no reconoce bajo ninguna grafía probada. Se conservan con
# su nombre original y se marcan como no verificados: descartarlos en
# silencio sería peor que mostrarlos con la advertencia.
NO_VERIFICADOS = {
    "Bolivina tumida",
    "Cassidulina reflexa",
    "Eponides leviculus",
    "Globocassidulina braziliensis",
    "Gyroidinoides turgidus",
    "Uvigerina cocoaensis",
    "Glomospira irregularis",
}

# --- Duplicación de registros -------------------------------------------
# La hoja maestra repite 12 filas idénticas en estudio, taxón, banda
# latitudinal, banda de profundidad y microhábitat. Son error de captura y se
# eliminan: contar dos veces la misma observación infla el ranking global.
#
# NO se eliminan las repeticiones de un mismo taxón dentro de un estudio
# cuando cambia la banda o el microhábitat (14 registros): ahí el artículo
# reporta la especie en dos estratos distintos y son observaciones separadas.
DEDUPLICAR = True
CLAVE_DUPLICADO = ("estudio", "taxon", "lat_banda", "prof_banda", "discriminacion")

# --- Vocabulario controlado de microhábitat ------------------------------
# La columna 'Discriminacion Adicional' del libro borrador usa etiquetas
# libres y con erratas para conceptos que se repiten. Se normalizan sin
# perder el matiz original.
DISCRIMINACION_VOCAB = {
    "Vivos": ("biocenosis", "Fauna viva (teñida con rosa de Bengala)"),
    "Muertos": ("tanatocenosis", "Fauna muerta"),
    "Infauna": ("infaunal", "Microhábitat infaunal"),
    "Epifauna": ("epifaunal", "Microhábitat epifaunal"),
    "Lecho de al mejas": ("banco_bivalvos", "Banco de bivalvos quimiosimbiontes"),
    "Muestras de bancos de mejillones": ("banco_bivalvos", "Banco de bivalvos quimiosimbiontes"),
    "Estera bacteriana": ("tapete_bacteriano", "Tapete bacteriano"),
    "Muestras de tapetes bacterianos": ("tapete_bacteriano", "Tapete bacteriano"),
}

# --- Inconsistencias aritméticas detectadas (se reportan, no se "arreglan") -
ARITMETICA = [
    {
        "archivo": "B",
        "donde": "Clasificacion fila 54 vs Graficas E2:F3",
        "detalle": "El total de Clasificacion es 1214,125 pero Calcáreo (1078) "
                   "+ Aglutinado (135,9375) da 1213,9375: faltan 0,1875.",
        "efecto": "Desfase del 0,015%. No altera ninguna conclusión.",
    },
    {
        "archivo": "B",
        "donde": "Clasificacion columna G",
        "detalle": "La suma de abundancias relativas da 1,0001 en vez de 1.",
        "efecto": "Error de redondeo acumulado. Se recalcula desde los conteos.",
    },
    {
        "archivo": "manuscrito",
        "donde": "Discusión, p. 43",
        "detalle": "El texto afirma «cerca de un 80%» de predominancia de FBC "
                   "sobre FBA; el valor que arrojan los datos es 88,8% "
                   "(86,99% tras reclasificar Ammodiscus).",
        "efecto": "Se publica el valor calculado, no el del texto.",
    },
]
