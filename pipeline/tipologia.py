"""
tipologia.py — Dos ejes independientes para clasificar cada filtración.

Mezclar «filtración fría» con «pockmark» en un solo campo confunde dos cosas
distintas: de qué está hecho el fluido y qué forma toma el fondo marino donde
sale. Un pockmark puede ser frío o termogénico; un volcán de lodo puede
expulsar metano biogénico o termogénico. Son ejes ortogonales y el dashboard
los filtra por separado.

Sólo se asigna un valor cuando el título del artículo lo declara o cuando la
localidad está documentada de forma inequívoca en la literatura (Håkon Mosby
es un volcán de lodo; Storfjordrenna, pingos de hidratos). Donde habría que
adivinar se deja en None y el dashboard lo muestra como pendiente: inventar
una morfología es peor que admitir que falta.
"""

from __future__ import annotations

# --- Eje 1: naturaleza del fluido ----------------------------------------
FLUIDOS = {
    "frio": "Filtración fría",
    "termogenico": "Hidrocarburo termogénico",
    "biogenico": "Gas biogénico",
    "hidrotermal": "Escape hidrotermal",
    "mixto": "Varios tipos",
    "no_filtracion": "No es una filtración",
}

# --- Eje 2: expresión geomorfológica del escape --------------------------
MORFOLOGIAS = {
    "pockmark": "Pockmark",
    "volcan_lodo": "Volcán de lodo",
    "monticulo_hidratos": "Montículo de hidratos",
    "pingo_hidratos": "Pingo de hidratos",
    "diapiro": "Diapiro",
    "escarpe": "Escarpe",
    "tapete_bacteriano": "Tapete bacteriano",
    "banco_bivalvos": "Banco de bivalvos",
    "respiradero_hidrotermal": "Respiradero hidrotermal",
    "campo_filtracion": "Campo de filtración sin morfología distintiva",
    "no_aplica": "No aplica",
}

# doi -> (fluido, morfologia, confianza, fuente)
# confianza: 'alta' = declarado en el título o verificado por el autor de la
# tesis; 'media' = localidad inequívoca en la literatura; None = sin asignar.
TIPOLOGIA: dict[str, dict] = {
    # --- morfología declarada en el propio título ---
    "10.3997/2214-4609.201406085": dict(
        fluido="frio", morfologia="pockmark", confianza="alta",
        fuente="el título dice «Adriatic Sea Pockmark»"),
    "10.1016/j.marmicro.2006.05.008": dict(
        fluido="frio", morfologia="pockmark", confianza="media",
        fuente="mismo sitio adriático que Panieri et al. (2000), descrito allí como pockmark"),
    "10.1016/j.marmicro.2007.08.002": dict(
        fluido="frio", morfologia="monticulo_hidratos", confianza="alta",
        fuente="el título dice «Blake Ridge hydrate mound»"),
    "10.1016/j.margeo.2014.03.020": dict(
        fluido="frio", morfologia="diapiro", confianza="alta",
        fuente="el título dice «Blake Ridge diapir»"),
    "10.1016/j.marpetgeo.2014.06.006": dict(
        fluido="termogenico", morfologia=None, confianza="alta",
        fuente="el título dice «thermogenic hydrocarbon seep»; morfología sin declarar"),
    "10.1007/978-94-017-0763-3_3": dict(
        fluido="biogenico", morfologia=None, confianza="alta",
        fuente="el título dice «Biogenic Gas Seep»; morfología sin declarar"),
    "10.2113/gsjfr.27.4.292": dict(
        fluido="termogenico", morfologia="tapete_bacteriano", confianza="alta",
        fuente="el título dice «hydrocarbon-seep bacterial mats»"),

    # --- localidad inequívoca en la literatura ---
    "10.1029/2005pa001196": dict(
        fluido="frio", morfologia="volcan_lodo", confianza="alta",
        fuente="el resumen sitúa el estudio en el volcán de lodo Håkon Mosby"),
    "10.3389/fmars.2019.00765": dict(
        fluido="frio", morfologia="pingo_hidratos", confianza="alta",
        fuente="Storfjordrenna: campo de pingos de hidratos de gas"),
    "10.1016/j.dsr.2017.03.001": dict(
        fluido="frio", morfologia="pockmark", confianza="media",
        fuente="Vestnesa Ridge: campo de pockmarks activos bien documentado"),
    "10.1038/s41598-022-05175-1": dict(
        fluido="frio", morfologia="pockmark", confianza="media",
        fuente="Vestnesa Ridge, 79° N: campo de pockmarks"),
    "10.1029/2002pa000824": dict(
        fluido="frio", morfologia="monticulo_hidratos", confianza="media",
        fuente="Hydrate Ridge: montículo de hidratos con pavimentos carbonatados"),
    "10.1016/j.gca.2004.07.012": dict(
        fluido="frio", morfologia="monticulo_hidratos", confianza="media",
        fuente="Hydrate Ridge"),
    "10.1016/j.epsl.2010.07.048": dict(
        fluido="frio", morfologia="monticulo_hidratos", confianza="media",
        fuente="Hydrate Ridge"),
    "10.1016/j.dsr.2016.08.011": dict(
        fluido="frio", morfologia="monticulo_hidratos", confianza="media",
        fuente="Hydrate Ridge, sectores norte y sur"),

    # --- aportados por el autor de la tesis ---
    "10.1002/2013pa002457": dict(
        fluido="hidrotermal", morfologia="respiradero_hidrotermal", confianza="alta",
        fuente="respiradero Pinkies, Cuenca de Guaymas (dato del autor)"),
    "10.1029/2010pa001930": dict(
        fluido="frio", morfologia="banco_bivalvos", confianza="alta",
        fuente="Clam Flats, Bahía de Monterey (dato del autor)"),
    "10.1016/j.marpetgeo.2018.02.037": dict(
        fluido="mixto", morfologia=None, confianza="alta",
        fuente="el título contrasta filtraciones de metano con hidrotermales"),

    # --- hidrocarburos declarados, morfología sin determinar ---
    "10.2113/gsjfr.38.2.93": dict(
        fluido="termogenico", morfologia=None, confianza="alta",
        fuente="el título dice «hydrocarbon seeps»"),
    "10.1007/bf01203719": dict(
        fluido="termogenico", morfologia=None, confianza="alta",
        fuente="el título dice «bathyal hydrocarbon vents»"),
    "10.1016/j.geobios.2003.10.004": dict(
        fluido="termogenico", morfologia=None, confianza="alta",
        fuente="el título dice «hydrocarbon seep»"),

    # --- estudios recuperados del borrador ---
    "10.1016/j.dsr.2014.08.011": dict(
        fluido="frio", morfologia="pockmark", confianza="alta",
        fuente="el título dice «hydrate pockmarks»"),
    "10.1016/j.marenvres.2019.06.006": dict(
        fluido="termogenico", morfologia=None, confianza="alta",
        fuente="filtraciones naturales de petróleo; el título declara además un "
               "componente antropogénico que confunde la señal"),

    # --- no es una filtración ---
    "10.1029/pa005i002p00161": dict(
        fluido="no_filtracion", morfologia="no_aplica", confianza="alta",
        fuente="estudio de microhábitats en márgenes continentales normales"),
}

# Por defecto: filtración fría (es el objeto de la tesis) con morfología sin
# determinar. Se marca así para que el dashboard distinga «frío por defecto»
# de «frío verificado».
DEFECTO = dict(fluido="frio", morfologia=None, confianza="nula",
               fuente="sin declarar en el título; requiere consultar el artículo")
