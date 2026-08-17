"""
caribe_referencia.py — Fauna de referencia del Caribe colombiano.

Estos datos NO existían en ninguna base: están en prosa, dentro del capítulo
4.2 de la tesis («Foraminíferos en el Caribe colombiano»), como porcentajes
citados de trabajos del grupo OCEÁNICOS. Aquí se estructuran por primera vez
para poder contrastarlos con MSH-BC-21.

Advertencia metodológica que el dashboard debe mostrar: estas cifras son
abundancias relativas tomadas de fuentes secundarias (la tesis citando a
terceros), con métodos de muestreo, fracciones de tamaño y ambientes
distintos entre sí y distintos de MSH-BC-21. La comparación es indicativa,
no cuantitativamente estricta. Ninguno de estos sitios es un ambiente de
filtración: son la fauna de fondo regional.
"""

from __future__ import annotations

LOCALIDADES_CARIBE = [
    dict(
        id="urabá_golfo", nombre="Golfo de Urabá (cuerpo de agua principal)",
        ambiente="Estuarino", fuente="Vargas (2011)", cita_en_tesis="cap. 4.2, p. 20",
        lat=8.20, lon=-76.85, nota="60 especies; abundancias de 1 a 20.000 ind/g; fracción >63 µm",
        taxones=[
            ("Ammonia beccarii", 31.4), ("Nonionella atlantica", 21.8),
            ("Fursenkoina pontoni", 13.4), ("Trochammina inflata", 9.7),
            ("Karreriella bradyi", 5.0), ("Bolivina lowmani", 3.3),
        ],
    ),
    dict(
        id="urabá_manglar", nombre="Manglares del Golfo de Urabá",
        ambiente="Manglar", fuente="Gómez (2011)", cita_en_tesis="cap. 4.2, p. 20",
        lat=8.05, lon=-76.75, nota="Shannon máximo de 1; 45-100% de formas aglutinadas",
        taxones=[
            ("Miliammina fusca", 61.0), ("Haplophragmoides canariensis", 7.0),
            ("Ammotium exiguus", 7.0), ("Trochammina squamata", 5.0),
            ("Ammobaculites exiliis", 5.0), ("Ammotium salsum", 3.0),
            ("Ammobaculites americanus", 3.0), ("Arenoparrella mexicana", 2.0),
            ("Ammonia beccarii", 2.0), ("Trochammina inflata", 1.0),
            ("Haplophragmoides wilbertii", 1.0),
        ],
    ),
    dict(
        id="cispata", nombre="Bahía de Cispatá",
        ambiente="Manglar", fuente="Bernal et al. (2008)", cita_en_tesis="cap. 4.2, p. 22",
        lat=9.40, lon=-75.82, nota="T. inflata propuesta como bioindicadora de manglar",
        taxones=[
            ("Trochammina inflata", 29.0), ("Arenoparrella mexicana", 15.0),
            ("Trochammina squamata", 13.0), ("Haplophragmoides canariensis", 7.2),
            ("Cyclammina trullissata", 5.0), ("Eponides parantillarum", 4.2),
            ("Ammotium salsum", 4.0), ("Palmerinella palmerae", 2.6),
            ("Haplophragmoides sp.", 2.5), ("Elphidium williamsoni", 2.0),
        ],
    ),
    dict(
        id="salmedina", nombre="Bancos de Salmedina",
        ambiente="Arrecifal / plataforma", fuente="López (2004); Bernal et al. (2006)",
        cita_en_tesis="cap. 4.2, p. 23",
        lat=10.30, lon=-75.75,
        nota="68 especies; 4 subambientes definidos; es la referencia de plataforma "
             "carbonatada más comparable con MSH-BC-21",
        taxones=[
            ("Amphistegina gibbosa", 55.4), ("Archaias angulatus", 4.23),
            ("Eponides sp.", 4.07), ("Rosalina sp.", 4.04),
            ("Anomalina globulosa", 3.31), ("Gyroidina broeckhiana", 2.91),
            ("Quinqueloculina granulocostata", 1.92), ("Quinqueloculina auberiana", 1.62),
            ("Borelis pulchra", 1.52), ("Quinqueloculina lamarckiana", 1.45),
            ("Hanzawaia sp.", 1.33), ("Cibicides tenuimargo", 1.26),
            ("Textularia agglutinans", 1.10),
        ],
    ),
    dict(
        id="rosario", nombre="Islas del Rosario (cordones de playa)",
        ambiente="Arrecifal", fuente="Puerres (2016)", cita_en_tesis="cap. 4.2, p. 21",
        lat=10.17, lon=-75.75,
        nota="Abundancias bajas (máx. 51 FB/g); 15 especies dominan el registro",
        taxones=[("Amphistegina lessonii", 49.0)],
    ),
]
