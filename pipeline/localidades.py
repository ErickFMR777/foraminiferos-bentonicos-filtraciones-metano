"""
localidades.py — Georreferenciación de los estudios de la base bibliográfica.

La base original no tiene campo de localidad: la metodología de la tesis
menciona «15 localidades» pero esa información sólo vive en los títulos y en
los textos de los artículos. Aquí se reconstruye.

IMPORTANTE sobre las coordenadas: son la posición REPRESENTATIVA de la
localidad de filtración nombrada (Hydrate Ridge, Blake Ridge, Håkon Mosby…),
no la posición exacta del testigo de cada estudio. Sirven para situar los
trabajos en un mapa mundial, no para análisis espacial fino. Cada entrada
lleva su nivel de confianza:

  alta   la localidad se nombra en el título o en el resumen del artículo
  media  se infiere del grupo de investigación y del contexto del trabajo
  nula   no determinada: requiere consultar el artículo original

Los estudios marcados 'nula' aparecen en el dashboard como pendientes, no se
inventa una posición para ellos.
"""

from __future__ import annotations

# doi -> (localidad, region, lat, lon, prof_m_aprox, confianza, fuente)
LOCALIDADES: dict[str, dict] = {
    "10.1016/s0377-8398(00)00005-0": dict(
        localidad="Cuenca del río Eel, margen norte de California", region="Pacífico NE",
        lat=40.80, lon=-124.60, prof_m=520, confianza="alta", fuente="título"),
    "10.1016/j.marmicro.2006.05.008": dict(
        localidad="Pockmark del Adriático central", region="Mediterráneo",
        lat=44.00, lon=13.50, prof_m=80, confianza="alta", fuente="título"),
    "10.2113/gsjfr.38.2.93": dict(
        localidad="Talud de Luisiana (Green Canyon), Golfo de México", region="Atlántico NW",
        lat=27.78, lon=-91.50, prof_m=550, confianza="alta", fuente="título"),
    "10.1029/pa005i002p00161": dict(
        localidad="Márgenes continentales del Atlántico y el Pacífico (multi-sitio)",
        region="Multi-sitio", lat=None, lon=None, prof_m=None, confianza="nula",
        fuente="resumen CrossRef: no es un estudio de filtración, sino de microhábitats"),
    "10.1016/j.margeo.2009.03.024": dict(
        localidad="Margen de Hikurangi, Nueva Zelanda", region="Pacífico SW",
        lat=-40.05, lon=178.15, prof_m=660, confianza="alta", fuente="título"),
    "10.1029/2002pa000824": dict(
        localidad="Hydrate Ridge, Oregón", region="Pacífico NE",
        lat=44.57, lon=-125.15, prof_m=800, confianza="alta", fuente="resumen CrossRef"),
    "10.1016/j.jseaes.2018.05.007": dict(
        localidad="Área de Dongsha, Mar de China Meridional NE", region="Pacífico NW",
        lat=22.10, lon=119.28, prof_m=770, confianza="alta", fuente="título"),
    "10.1016/j.dsr2.2018.01.011": dict(
        localidad="Kimki Ridge, borderland del sur de California", region="Pacífico NE",
        lat=32.90, lon=-118.90, prof_m=500, confianza="alta", fuente="título"),
    "10.1029/2003gc000595": dict(
        localidad="Bahía de Monterey, California", region="Pacífico NE",
        lat=36.77, lon=-122.08, prof_m=950, confianza="alta", fuente="título"),
    "10.1016/j.epsl.2010.07.048": dict(
        localidad="Hydrate Ridge, margen de Cascadia", region="Pacífico NE",
        lat=44.57, lon=-125.15, prof_m=800, confianza="media",
        fuente="grupo de investigación y continuidad con Torres et al. 2003"),
    "10.1016/j.marmicro.2007.08.002": dict(
        localidad="Montículo de hidratos de Blake Ridge", region="Atlántico NW",
        lat=32.49, lon=-76.19, prof_m=2155, confianza="alta", fuente="título"),
    "10.1016/j.dsr2.2017.12.011": dict(
        localidad="Mar de Mármara", region="Mediterráneo",
        lat=40.80, lon=27.80, prof_m=500, confianza="alta", fuente="título"),
    "10.1016/j.dsr2.2019.104723": dict(
        localidad="Perturbación de Palmahim, costa afuera de Israel", region="Mediterráneo",
        lat=32.00, lon=34.35, prof_m=1000, confianza="alta", fuente="título"),
    "10.3997/2214-4609.201406085": dict(
        localidad="Pockmark del Mar Adriático", region="Mediterráneo",
        lat=44.00, lon=13.50, prof_m=80, confianza="alta", fuente="título"),
    "10.1007/bf01203719": dict(
        localidad="Escapes batiales de hidrocarburos, Golfo de México", region="Atlántico NW",
        lat=27.70, lon=-91.50, prof_m=650, confianza="alta", fuente="título"),
    "10.2113/gsjfr.27.4.292": dict(
        localidad="Talud del Golfo de México (tapetes bacterianos)", region="Atlántico NW",
        lat=27.70, lon=-91.50, prof_m=650, confianza="alta", fuente="título"),
    "10.1029/2010pa001930": dict(
        localidad="Filtraciones de hidrocarburos (sitio no determinado)", region="No determinada",
        lat=None, lon=None, prof_m=None, confianza="nula",
        fuente="el título no nombra localidad; sin resumen en CrossRef"),
    "10.1016/s0967-0637(01)00017-6": dict(
        localidad="Bahía de Monterey, California", region="Pacífico NE",
        lat=36.77, lon=-122.08, prof_m=950, confianza="alta", fuente="título"),
    "10.1016/j.pocean.2008.12.002": dict(
        localidad="Margen de las Aleutianas", region="Pacífico N",
        lat=54.00, lon=-165.00, prof_m=3400, confianza="alta", fuente="título"),
    "10.1007/978-94-017-0763-3_3": dict(
        localidad="Mar del Norte (escape de gas biogénico)", region="Atlántico NE",
        lat=57.00, lon=1.50, prof_m=150, confianza="alta", fuente="título"),
    "10.1007/s00367-019-00635-6": dict(
        localidad="Ártico y Atlántico Norte (Vestnesa / Storfjordrenna)", region="Ártico",
        lat=78.50, lon=9.00, prof_m=900, confianza="media",
        fuente="título; el estudio abarca varios sitios árticos"),
    "10.3389/fmars.2019.00765": dict(
        localidad="Pingos de hidratos de Storfjordrenna, Mar de Barents", region="Ártico",
        lat=76.10, lon=16.03, prof_m=380, confianza="alta", fuente="título y resumen"),
    "10.1002/2013pa002457": dict(
        localidad="Ambientes de escape de metano (sitio no determinado)", region="No determinada",
        lat=None, lon=None, prof_m=None, confianza="nula",
        fuente="el título no nombra localidad; sin resumen en CrossRef"),
    "10.1016/j.marpetgeo.2014.06.006": dict(
        localidad="Adriático somero frente a Italia", region="Mediterráneo",
        lat=44.30, lon=12.50, prof_m=20, confianza="alta", fuente="título"),
    "10.1016/s0377-8398(03)00032-x": dict(
        localidad="Canal de Santa Bárbara, California", region="Pacífico NE",
        lat=34.35, lon=-119.85, prof_m=500, confianza="alta", fuente="título"),
    "10.1016/j.geobios.2003.10.004": dict(
        localidad="Depresión de Rockall, Atlántico NE", region="Atlántico NE",
        lat=55.50, lon=-15.80, prof_m=700, confianza="alta", fuente="título"),
    "10.1016/j.margeo.2014.03.020": dict(
        localidad="Diapiro de Blake Ridge", region="Atlántico NW",
        lat=32.49, lon=-76.19, prof_m=2155, confianza="alta", fuente="título"),
    "10.1111/j.1439-0485.2006.00143.x": dict(
        localidad="Mar Negro noroccidental", region="Mar Negro",
        lat=44.50, lon=31.80, prof_m=200, confianza="alta", fuente="título"),
    "10.1016/j.apgeochem.2011.01.032": dict(
        localidad="Bahía de Monterey, California", region="Pacífico NE",
        lat=36.77, lon=-122.08, prof_m=950, confianza="alta", fuente="título"),
    "10.1016/j.gca.2004.07.012": dict(
        localidad="Hydrate Ridge, Pacífico NE", region="Pacífico NE",
        lat=44.57, lon=-125.15, prof_m=800, confianza="alta", fuente="título"),
    "10.1029/2005pa001196": dict(
        localidad="Volcán de lodo Håkon Mosby, norte de Noruega", region="Ártico",
        lat=72.00, lon=14.72, prof_m=1250, confianza="alta", fuente="resumen CrossRef"),
    "10.1038/s41598-022-05175-1": dict(
        localidad="Vestnesa Ridge, 79° N, Svalbard", region="Ártico",
        lat=79.00, lon=6.90, prof_m=1200, confianza="alta", fuente="título"),
    "10.1016/j.marpetgeo.2018.02.037": dict(
        localidad="Filtraciones de metano e hidrotermales (multi-sitio)", region="No determinada",
        lat=None, lon=None, prof_m=None, confianza="nula",
        fuente="el título no nombra localidad; sin resumen en CrossRef"),
    "10.46427/gold2020.1503": dict(
        localidad="Mar de China Meridional", region="Pacífico NW",
        lat=22.00, lon=119.00, prof_m=1100, confianza="media",
        fuente="título; resumen de congreso sin detalle de sitio"),
    "10.1007/s12665-012-2201-2": dict(
        localidad="Depresión de Baiyun, Mar de China Meridional N", region="Pacífico NW",
        lat=20.00, lon=115.50, prof_m=1500, confianza="alta", fuente="título"),
    "10.1016/j.dsr.2016.08.011": dict(
        localidad="Filtraciones y zonas adyacentes en ambientes disóxicos (no determinada)",
        region="No determinada", lat=None, lon=None, prof_m=None, confianza="nula",
        fuente="el título no nombra localidad; sin resumen en CrossRef"),
    "10.1016/j.dsr.2017.03.001": dict(
        localidad="Vestnesa Ridge, NW de Svalbard", region="Ártico",
        lat=79.00, lon=6.90, prof_m=1200, confianza="alta", fuente="título"),
}

# Estudio sin DOI resuelto de forma fiable: CrossRef devolvió una coincidencia
# incorrecta (un artículo sobre parafinas cloradas). Se identifica por título.
SIN_DOI = {
    "Diversity and Characteristics of Benthic Foraminifera in Cold Seep Areas in the Active "
    "Margin of the northeastern South China Sea": dict(
        localidad="Margen activo del Mar de China Meridional NE", region="Pacífico NW",
        lat=22.00, lon=119.00, prof_m=1100, confianza="media",
        fuente="título; referencia no localizable en CrossRef ni en búsqueda web"),
}

# El sitio de la propia tesis, para situarlo en el mismo mapa.
MSH_BC_21 = dict(
    localidad="MSH-BC-21, plataforma frente al Golfo de Morrosquillo",
    region="Caribe colombiano",
    lat=9.54, lon=-76.23, prof_m=75, confianza="alta",
    fuente="Área de estudio declarada en la tesis (cap. 3): W 76°08'–76°20', N 9°30'–9°35'8\"",
)
