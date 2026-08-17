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

# --- Estudios recuperados del borrador -----------------------------------
# Seis estudios del libro borrador no pasaron a la hoja filtrada. Revisadas
# sus condiciones, tres exclusiones son metodológicamente correctas según el
# criterio que declara la propia tesis («condiciones oceánicas actuales y
# foraminíferos recientes superficiales») y dos son discutibles.
#
# Se recuperan marcados con recuperado=True, de modo que el dashboard pueda
# mostrar la base tal como la curó el autor o la base ampliada, y la decisión
# quede a la vista en lugar de enterrada en el proceso.
#
# ATENCIÓN: la hoja borrador no tiene columna de tipo de pared. Para estos
# registros la pared se DERIVA de la posición sistemática del género
# (taxonomy.py), no se lee del original. Van marcados pared_derivada=True.
RECUPERAR = {
    "Benthic foraminifera from the deep-water Niger delta": dict(
        motivo="Estudio de pockmarks de hidratos con actividad actual "
               "(«present-day activity») y discriminación vivos/muertos, es decir "
               "fauna reciente teñida. Cumple el criterio declarado en la "
               "metodología de la tesis. Aporta 22 registros a la banda tropical "
               "0-15°, que sin ellos se sostiene sobre un único registro.",
        confianza="alta",
    ),
    "Natural and anthropogenic oil impacts on benthic foraminifera": dict(
        motivo="Exclusión inconsistente: la base sí incluye otros estudios de "
               "filtración de hidrocarburos del Golfo de México (Sen Gupta & "
               "Aharon 1994; Sen Gupta et al. 1997; Lobegeier & Sen Gupta 2008). "
               "La diferencia defendible es el componente antropogénico, que "
               "confunde la señal natural. Se recupera marcado con ese reparo: "
               "aporta 29 registros someros (<500 m), donde la base es más débil.",
        confianza="media",
        reparo="Mezcla filtraciones naturales con contaminación por petróleo; "
               "la señal no es atribuible sólo a la filtración.",
    ),
}

# Exclusiones que SÍ se mantienen, con su razón. Se documentan para que la
# curación quede trazable y no parezca arbitraria.
EXCLUSIONES_CONFIRMADAS = {
    "Stable carbon isotope records of carbonates tracing fossil seep activity":
        "Actividad de filtración FÓSIL. La tesis restringe el análisis a "
        "condiciones oceánicas actuales.",
    "Relationships between the stable isotopic signatures of living and fossil":
        "Incluye fauna fósil junto a la viva; no separable desde la hoja.",
    "The benthic foraminiferal δ34S records flux and timing of paleo methane":
        "Emisiones de PALEO-metano. Fuera del alcance temporal declarado.",
    "GISCHLER": "No es un estudio de filtración sino de ambientes deposicionales "
                "carbonatados. Sus taxones (Amphistegina gibbosa, Archaias "
                "angulatus, Homotrema rubrum) son fauna arrecifal caribeña: sirve "
                "como referencia regional comparable con MSH-BC-21, no como "
                "fauna de seep.",
}

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
