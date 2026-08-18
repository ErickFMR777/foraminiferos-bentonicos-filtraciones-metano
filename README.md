# Foraminíferos bentónicos en filtraciones de metano

Dashboard editorial bilingüe (ES/EN) que compara **lo que la literatura mundial
ha publicado sobre foraminíferos bentónicos en filtraciones de metano** con una
muestra de la plataforma continental del Caribe colombiano.

No es un panel de indicadores. Cada sección es una historia de datos con su
método declarado, su tamaño de muestra a la vista y sus límites escritos.

**En línea:** <https://foraminiferos-caribe-colombiano.vercel.app> — acceso
libre. Lo que se publica son agregados y tablas derivadas; los datos primarios
del proyecto siguen inéditos y no salen de aquí.

---

## De dónde sale

A partir de la tesis de grado de **Erick Francisco Mendoza Rivero**, Ingeniero
Geólogo — *«Análisis de las asociaciones de foraminíferos bentónicos en
filtraciones de metano: comparación entre distintas localidades y la plataforma
continental del Caribe colombiano»*. Universidad Nacional de Colombia, sede
Medellín, Facultad de Minas, Departamento de Geociencias y Medio Ambiente,
2023. Directora: Ph.D. Gladys Rocío Bernal Franco.

> La portada del manuscrito indica 2022 por un error del propio documento. El
> trabajo de grado (3007442) se entregó en el primer período académico de 2023.

Realizada en el marco del proyecto **Methane seep hunting: A multi-scale and
multi method approach**, del Programa Nacional de Ciencia, Tecnología e
Innovación en Geociencias (Minciencias), convocatoria 877-2020, contrato
80740-143-2021. Financiado con recursos del **Convenio 785/668 de 2019**,
suscrito entre la **Agencia Nacional de Hidrocarburos**, el **Ministerio de
Ciencia, Tecnología e Innovación** y el **Fondo Nacional de Financiamiento para
la Ciencia, la Tecnología y la Innovación Francisco José de Caldas**. Grupo de
investigación **OCEÁNICOS**. Entidades ejecutoras y beneficiarias: **UNAL ·
UPB · GMAS · GEOMARES · ACGGP**.

---

## Qué ofrece

Ocho secciones en scroll, todas bilingües y con su bloque «Cómo se lee».

| # | Sección | Qué responde |
|---|---|---|
| 01 | **El vacío** | Matriz latitud × profundidad y mapa mundial con zoom: dónde se ha estudiado esto y dónde no |
| 02 | **La firma de la pared** | Proporción calcáreo / aglutinado por banda, la señal más fiable de filtración |
| 03 | **La muestra** | Qué hay dentro de MSH-BC-21: composición e interior del testigo |
| 04 | **El veredicto** | Cuatro criterios de la literatura contrastados con lo que la muestra mide |
| 05 | **La continuación** | Barragán y Bernal (2024): 18 estaciones del mismo campo, con isótopos |
| 06 | **El catálogo** | Explorador de los taxones: buscar, filtrar y ordenar |
| 07 | **El Caribe contra sí mismo** | La muestra frente a la fauna de fondo regional |
| 08 | **Límites** | Lo que estos datos **no** pueden decir |

### Los hallazgos que sostienen la narrativa

- **La celda 0-15° / <150 m está vacía**, y sigue vacía al ampliar la base con
  los estudios reincorporados. Que sobreviva a la ampliación es la prueba de
  que el vacío es real y no un artefacto de la curación. Ahí cae el Caribe
  colombiano.
- **El 80 % de los registros procede de más de 500 m.** Tres de las cuatro
  bandas latitudinales no tienen ni un dato somero.
- **`Cibicidoides wuellerstorfi`, `Cibicides wuellerstorfi` y `Planulina
  wüllerstorfi` son la misma especie**, hoy `Lobatula wuellerstorfi`.
  Unificadas, pasa a ser el segundo taxón más reportado del mundo — lo que
  *refuerza* el argumento de la tesis.
- **La diversidad de MSH-BC-21 (H′ = 3,4325) deja de ser una anomalía.**
  Barragán y Bernal miden Shannon de 3,0 a 3,8 en las 18 estaciones del mismo
  campo, incluidas las de actividad alta.
- **En el Caribe colombiano, una sola especie se lleva entre el 29 y el 61 %
  de la asociación** —manglares, estuarios, arrecifes—. En MSH-BC-21 la más
  abundante no llega al 11 %. Lo que distingue la muestra no es *qué* especies
  hay, sino que **ninguna manda**: es exactamente lo que mide su equidad de
  Pielou, J′ = 0,8687.

---

## Las cifras

| | |
|---|---|
| Estudios en la base | **40** (39 de filtración + 1 de fauna de referencia) |
| Georreferenciados | 39 / 40 |
| Con morfología asignada | 32 / 40 |
| Taxones de la base de la tesis | **197** |
| Taxones leídos del texto completo | **531** (unión de ambas fuentes: 566) |
| Artículos leídos íntegros | **38** |
| Correcciones documentadas | **85** |
| MSH-BC-21 | S = 52 · H′ = 3,4325 · J′ = 0,8687 |
| Pared de MSH-BC-21 | 87,0 % calcáreo / 13,0 % aglutinado |
| Solape con la literatura | 14 / 52 especies |
| δ¹³C extraído de tablas | 19 pares taxón-estudio, 5 estudios |
| Abundancias extraídas | 200 pares, 6 estudios |
| Índices de diversidad | 8 valores, 6 estudios |
| Peso del dataset público | 555 KB (~440 KB llegan al navegador) |

---

## Cómo funciona

Dos mitades independientes. **No hay base de datos, ni API, ni consultas en
runtime**: el pipeline produce JSON y el frontend los importa en tiempo de
build.

```
Data_nosubiralrepo/*.xlsx ──00──▶ data/private/*_raw.json
                                        │
      WoRMS ─05─┐                       │
    CrossRef ─06─┼──▶ data/private/ ──10──▶ *_clean.json
        PDF ─07─┘    (nunca se publica)      │
                                             ▼
                                 20/45/50 ──▶ data/derived/*.json
                                                  │  (público)
                                                  ▼
                              import x from "@datos/nombre.json"
                                                  │
                                       build estático de Next.js
```

### El pipeline (Python, sin pandas)

| Etapa | Qué hace |
|---|---|
| `00_extract` | Lee los Excel; propaga celdas combinadas y recupera la columna de microhábitat perdida |
| `05_worms` | Resuelve cada nombre contra WoRMS, filtrando por `phylum == Foraminifera` |
| `06_estudios` | Resuelve cada estudio a una referencia citable vía CrossRef |
| `07_pdfs` | Empareja cada PDF con su estudio por el DOI de la **primera** página |
| `08_organizar` | Renombra a «Autor Año - Título» y separa las referencias excluidas |
| `09_verificar_pdfs` | Comprueba que cada PDF contiene lo que su nombre dice |
| `10_clean` | Aplica el registro de correcciones |
| `20_build` | Emite los agregados públicos |
| `40_taxones_pdf` | Lee los artículos completos: presencia, menciones y dominancia |
| `45_tablas_pdf` | Lee las **tablas**: δ¹³C, abundancias e índices de diversidad |
| `50_estadisticas` | Rankings, asociaciones dominantes y estadísticas por estudio |
| `30_informe` | Genera el informe de curación en PDF |
| `60_excel` | Devuelve las correcciones a los Excel del autor |
| `99_auditoria` | **92 comprobaciones independientes**; sale con código 1 si algo falla |

Los módulos sin número —`taxonomy`, `corrections`, `localidades`, `tipologia`,
`caribe_referencia`, `estudios_nuevos`— son tablas de referencia **curadas a
mano**: no se generan, se editan, y son la fuente de verdad.

### El frontend

Next.js 15 (App Router) + TypeScript + Tailwind v4 con tokens CSS. Todos los
gráficos son **SVG escrito a mano**: ninguna librería de charts. El mapa usa
`d3-geo` con `world-atlas` empaquetado, sin tiles externos, de modo que el
dashboard no hace ni una petición a terceros.

El mapa tiene **zoom y arrastre propios**, y agrupa por distancia **en
pantalla**: doce de los treinta y nueve estudios comparten coordenada con otro
—tres en Hydrate Ridge, tres en Vestnesa Ridge— porque la posición es la de la
localidad, no la del testigo. Los solapados salen como un círculo con su
número y al acercar se van separando. Cuando la coordenada es **idéntica** no
hay zoom que los separe, así que al pulsar el círculo se despliega su lista.
**Ningún punto se desplaza nunca de su posición real**, y un `clipPath` impide
que nada se dibuje fuera del marco.

---

## Cómo se construyó: el método

Lo que distingue este trabajo de un simple volcado de datos.

### Toda corrección queda registrada

`corrections.py` es la pieza central: cada diferencia entre los Excel del autor
y los datos publicados pasa por ahí, con su motivo y su fuente, y el registro
se publica. Los tipos distinguen cosas que **no** son equivalentes:

- `errata` — error del manuscrito
- `actualizacion` — WoRMS reclasificó después de nov-2022; **no** es un error
  del autor
- `exclusion`, `reclasificacion_pared`, `aritmetica`, `duplicado`,
  `recuperacion`, `sin_verificar`

De las 85 entradas, **23 son errores reales del manuscrito** que afectan al
8,2 % de los registros. Las demás no lo son.

### Tres señales que no valen lo mismo

En la lectura de los artículos se distingue con cuidado:

- **Presencia** — el taxón aparece. Señal sólida.
- **Menciones** — cuántas veces. Proxy **débil**: un artículo repite un nombre
  al citar a otros. Sirve para ordenar dentro de un artículo, no para comparar
  entre artículos de distinta extensión.
- **Dominancia declarada** — el propio texto lo afirma. La única que puede
  llamarse dominancia.

La dominancia se atribuye por **cláusula**, no por frase: en *«Bolivina
dominated the assemblage, whereas Uvigerina was rare»*, sólo *Bolivina* es
dominante. Se descartan además las cláusulas negadas, las que atribuyen el
hallazgo a otro trabajo (*«Rathburn et al. (2000) found…»*) y aquellas en que
«dominant» califica algo que no es fauna (la litología, un proceso geoquímico,
la dirección de enrollamiento). Cada marca guarda **la cláusula literal que la
afirma**, para poder auditarla una a una.

### Validación taxonómica con guarda de género

Los nombres se resuelven contra WoRMS. La coincidencia aproximada rescata
erratas de OCR reales —`Sfainforfhia fisiformis` → *Stainforthia fusiformis*—
pero puede saltar de un género a otro: `Bolivina tenuata` acabó emparejado con
*Bulimina* tenuata. Ahora una coincidencia difusa debe respetar el género, con
un umbral de **0,80 medido sobre los 87 nombres difusos de esta base**.

### Las trampas del PDF, y cómo se sortean

- **Ligaduras.** Los PDF emiten `wuellerstor ﬁ` con espacios espurios. Sin
  repararlo, *Cibicidoides wuellerstorfi* se pierde entero.
- **La bibliografía.** Las listas de referencias citan títulos que llevan
  nombres de especies: contarlas daba por «reportado» un taxón que el artículo
  sólo nombraba al citar a un tercero. Se recorta antes de contar.
- **Abreviaturas.** `U. peregrina` se expande a *Uvigerina peregrina*, pero
  sólo cuando inicial y epíteto identifican un único binomio de ese artículo.
- **El símbolo por mil.** En varios artículos el `‰` de los δ¹³C sale del PDF
  convertido en `%`, de modo que «1,26 ± 0,15 %» es un valor isotópico y no una
  abundancia. Por eso las abundancias sólo se aceptan cuando el pie de tabla lo
  dice, y cada cifra debe caer en el **rango físico** de su variable.
- **Tablas sin bordes.** `pypdf` devuelve el texto en orden de lectura y una
  tabla se vuelve una ristra de números sin columnas. `45_tablas_pdf` usa
  `pdfplumber`, que da la posición de cada palabra: agrupando por coordenada
  vertical se recupera la fila.

### Dónde va cada dato, y por qué

No todo lo extraído entra en el mismo sitio, y la decisión se tomó **midiendo
el solape**, no por comodidad:

- **δ¹³C → la base principal.** Comparte grano con ella (una medida por taxón
  dentro de un estudio) y el **73 %** de los valores cae sobre registros que la
  base ya tiene. Son columnas nuevas, no filas nuevas.
- **Abundancias → la vista ampliada.** Sólo el **17 %** solapa: la base de la
  tesis recoge «las 5 principales especies» por filtro y las tablas listan la
  asociación entera. Meterlas en la base obligaría a tirar el 83 % o a añadir
  166 filas que la curación excluyó a propósito.
- **Fauna de referencia del Caribe → dataset de contraste, nunca fusionado.**
  Las cinco localidades caen en la banda 0-15° y son someras: fusionarlas
  llenaría con fauna de manglar y arrecife **justamente la celda que el trabajo
  señala como vacía**, y convertiría en falso el hallazgo central. Es el mismo
  error que ya se corrigió con McCorkle (1990), que figuraba como estudio de
  filtración sin serlo.

### La morfología debe verse en el propio artículo

Cada morfología asignada tiene que aparecer en el **cuerpo** del artículo que la
justifica —descartando su bibliografía—, y la auditoría lo comprueba. La regla
nació de dos errores reales: un estudio figuraba como «pingo de hidratos de
Storfjordrenna» cuando su texto no dice «pingo» ni una vez y estudia los
pockmarks de Vestnesa, **a 330 km de donde estaba situado en el mapa**; y otro
figuraba como «pockmark» porque esa palabra aparecía una sola vez… en su propia
lista de referencias, citando a un tercero.

Las pocas asignaciones que descansan en que la localidad esté documentada en la
literatura, y no en el texto, van declaradas una a una en
`tipologia.JUSTIFICADA_POR_LOCALIDAD`. La auditoría las admite pero vigila que
no se multipliquen.

### La auditoría no se fía del pipeline

`99_auditoria.py` **vuelve a leer los Excel originales** y verifica de forma
independiente la conservación de registros, la aritmética recalculada desde
cero, la coherencia entre datasets, los rangos físicos de lo extraído de las
tablas y la ausencia de fugas de datos confidenciales. Son **92
comprobaciones** y han atrapado errores reales, incluido uno introducido
mientras se ampliaba el propio Excel.

### Verificación inversa: ningún valor inventado

La auditoría comprueba que lo extraído sea coherente. Falta la pregunta
contraria —¿está cada cifra publicada realmente en su artículo?—, y se
respondió al revés: tomando los **991 valores** de tabla y los **9 índices** ya
extraídos y buscándolos en la página que cada uno cita de su PDF.

**991 de 991 y 9 de 9 se encuentran donde dicen estar.** Las 166 que fallaron
en la primera pasada eran el signo menos Unicode (`−`, U+2212) que usan las
revistas frente al guion ASCII: un fallo de la sonda, no del dato.

Conviene decir cómo NO se puede verificar esto. Se intentaron dos sondas
independientes —lectura por líneas y `extract_tables()` de pdfplumber— y las
dos daban cero incluso en los estudios donde el pipeline sí extrae datos. Es
decir: **el control positivo falló y el resultado no valía**. Estas tablas sólo
se dejan leer agrupando las palabras por coordenada vertical, que es
precisamente por lo que el pipeline lo hace así.

---

## Límites declarados

Un trabajo serio dice lo que **no** puede decir.

- **Una sola muestra propia.** MSH-BC-21 es un testigo, sin réplicas ni sitios
  de control propios.
- **Sin isótopos propios.** La tesis no midió δ¹³C. Los primeros valores del
  área son los de Barragán y Bernal (2024).
- **Extracción cuantitativa parcial, y declarada.** δ¹³C, abundancias e
  índices sólo se pudieron extraer de 5 a 6 estudios cada uno. El pipeline no
  lo disimula: publica en `tablas_pdf.json` la lista nominal de los **29
  estudios sin tabla legible por máquina** —tablas rasterizadas, columnas
  entrelazadas o cabecera que no sobrevive a la extracción—. **Por eso no se
  hizo un análisis multivariante con esas variables**: imputar el 85 % de la
  matriz no describe los datos, inventa la estructura.
- **Presencia no es abundancia.** Del texto se extrae qué taxones aparecen, no
  cuánto pesa cada uno.
- **Dos estudios sin PDF** (E05, E26) y **8 de 40 sin morfología**, porque la
  mención estaba en una tabla comparativa de otras localidades y asignarla
  sería inventar.
- **La fauna de referencia caribeña viene de fuentes secundarias** —la tesis
  citando a terceros— con métodos y fracciones de tamaño distintos entre sí.
  Ese contraste es indicativo, no cuantitativamente estricto.
- **El registro mundial está sesgado.** Comparar una plataforma tropical con
  filtraciones profundas de latitudes altas tiene un límite.

---

## Confidencialidad

Los datos primarios son inéditos (proyecto MSH).

| Ruta | Estado |
|---|---|
| `Data_nosubiralrepo/` | **Nunca** se publica: tesis, artículos y los Excel |
| `data/private/` | **Nunca** se publica: extracciones que citan texto literal |
| `data/derived/` | Público: sólo agregados y tablas derivadas |
| `Informe_curacion_datos.pdf` | Público |

Hacen falta **dos** archivos de exclusión y no son intercambiables: el CLI de
Vercel **no lee `.gitignore`**, sólo `.vercelignore`. Las referencias
bibliográficas sí se publican; lo que no se publica son los archivos.

**El sitio es público.** Lo fue tras una etapa con contraseña: la tesis está
entregada desde 2023 y el dashboard pasa a ser parte del portafolio del autor.
Lo que se abrió es el dashboard, no los datos — la tabla de arriba sigue
gobernando, y `data/derived/` siempre estuvo pensado para verse.

Sin barrera detrás, dos comprobaciones de la auditoría dejan de ser red de
seguridad y pasan a ser la única defensa: que ningún dataset público lleve
texto literal de los artículos, y que ninguno exponga rutas del sistema de
archivos.

---

## Ejecutar

```bash
npm install
npm run dev          # servidor de desarrollo
npm run build        # build de producción
npm run verificar    # comprobación de tipos — ESTE es el gate
npm run auditoria    # las 91 comprobaciones del pipeline
```

El pipeline necesita `openpyxl`, `pypdf`, `fpdf2` y `pdfplumber`, y lee los
originales desde `THESIS_DATA_DIR` (por defecto `./Data_nosubiralrepo`). El
orden completo de etapas está en [CLAUDE.md](CLAUDE.md); el estado del proyecto
y las decisiones tomadas, en [CHECKPOINT.md](CHECKPOINT.md).

No hacen falta variables de entorno para el frontend: `output: "export"` deja
el sitio entero en `out/`, sin servidor ni consultas en runtime.
