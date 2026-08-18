# CHECKPOINT — Dashboard Tesis Foraminíferos

**Última actualización:** 2026-08-17 · Fase 0 y Fase 1 COMPLETAS · DESPLEGADO
**Novedad:** integrado Barragán y Bernal (2024), que resuelve la tensión de la Historia 2.

Documento de continuidad: si la sesión se corta, esto es lo que hace falta
para retomar sin releer nada.

> **Cifras verificadas contra `data/derived/` el 2026-08-17**, después de
> ampliar la base. Este documento ya ha tenido cifras obsoletas tres veces:
> si cambias el pipeline, **regenera los §4 y §5 desde los datos**, no los
> edites a mano. `python pipeline/99_auditoria.py` debe salir en 0 antes de
> dar por buena cualquier cifra de aquí.

---

## 1. Qué es esto

Dashboard interactivo bilingüe (ES/EN) sobre la tesis de grado de Erick
Francisco Mendoza Rivero (Ing. Geológico, UNAL Medellín, 2022):
*«Análisis de las asociaciones de foraminíferos bentónicos en filtraciones de
metano: comparación entre distintas localidades y la plataforma continental
del Caribe colombiano»*. Directora: Ph.D. Gladys Rocío Bernal Franco.
Marco: proyecto MSH (*Methane Seep Hunting*).

**Destino:** Vercel. **Públicos:** comunidad académica internacional +
reclutadores de tech/datos.

---

## 1 bis. Despliegue

**En línea y protegido con contraseña:** https://foraminiferos-caribe-colombiano.vercel.app
Proyecto de Vercel `foraminiferos-caribe-colombiano` (cuenta erickfmr777).
El proyecto anterior `foraminiferos-caribe` se eliminó: Vercel no permite
renombrar proyectos desde la CLI, así que hubo que recrearlo.

La autenticación es HTTP básica en `src/middleware.ts`, con las credenciales
en las variables de entorno `DASHBOARD_USUARIO` y `DASHBOARD_CLAVE` de Vercel
(definidas en production, preview y development). Si no están definidas el
sitio queda abierto, que es lo cómodo en local.

**Por qué no es `output: "export"`.** Un export puramente estático no admite
middleware, y una contraseña en el navegador sería decorativa: el dataset
viaja dentro del bundle. Las páginas se siguen prerenderizando; sólo se añade
la puerta en el edge.

**El matcher protege TODO menos el favicon, y eso es deliberado.** Excluir
`_next/static` parecía inofensivo y no lo era: el dataset viaja en el chunk de
la página, de modo que `/_next/static/chunks/app/page-*.js` servía los datos
completos sin pedir credenciales. Se detectó probando el despliegue real, no
razonando sobre él. **Si alguien vuelve a excluir los assets del matcher,
reabre la fuga.**

Para abrir el sitio al público: borrar `src/middleware.ts` y devolver
`output: "export"` a `next.config.ts`.

---

## 2. REGLAS DE CONFIDENCIALIDAD (no negociables)

- `Data_nosubiralrepo/` NUNCA se sube. Contiene la tesis en PDF y dos Excel
  con datos primarios inéditos del proyecto MSH.
- `data/private/` NUNCA se sube (extracciones intermedias).
- Ya están en `.gitignore`, junto con `*.xlsx`, `*.pdf`, `.env*`.
- **Y también en `.vercelignore`, que es OTRO archivo y es imprescindible.**
  El CLI de Vercel no lee `.gitignore`. Del 2026-08-17 al 2026-08-18, sin ese
  archivo, `vercel deploy` subió la carpeta entera a Vercel: los dos Excel
  inéditos, los 47 PDF y todo `data/private/`. Nunca estuvieron servidos en
  una URL —no están en `public/` y el middleware devolvía 401— pero sí
  almacenados fuera del equipo. Corregido: se creó `.vercelignore`, se
  redesplegó limpio (39 archivos, 0 confidenciales, verificado contra la API)
  y **se eliminó el despliegue que guardaba las copias**.
- **SÍ se publica:** los agregados de `data/derived/` y las 38 referencias
  bibliográficas (el usuario lo autorizó explícitamente el 2026-08-16,
  rectificando una instrucción previa).
- **NO se publica:** ningún enlace de descarga a la tesis ni a los Excel.
- Verificar siempre con `git status --porcelain --ignored | grep '^!!'`
  antes de cualquier push.

---

## 3. Estado del pipeline (FUNCIONA, no tocar sin motivo)

Ejecutar en orden desde la raíz del proyecto:

```bash
python pipeline/00_extract.py    # Excel -> data/private/*_raw.json
python pipeline/05_worms.py      # resolución taxonómica WoRMS (cacheado)
python pipeline/06_estudios.py   # resolución bibliográfica CrossRef
python pipeline/10_clean.py      # aplica correcciones -> *_clean.json
python pipeline/07_pdfs.py       # identifica los PDF y extrae evidencia
python pipeline/08_organizar.py  # renombra y separa «Referencias excluidas»
python pipeline/09_verificar_pdfs.py  # nombre vs contenido + duplicados
python pipeline/20_build.py      # -> data/derived/*.json (público)
python pipeline/40_taxones_pdf.py    # lee los artículos completos (WoRMS)
python pipeline/50_estadisticas.py   # -> taxones_completo.json
python pipeline/30_informe.py    # -> Informe_curacion_datos.pdf
python pipeline/60_excel.py      # -> los dos Excel corregidos (carpeta privada)
python pipeline/99_auditoria.py  # 76 comprobaciones; código 1 si algo falla
```

**Ejecutar `99_auditoria.py` después de cualquier cambio en el pipeline.**
Re-lee los Excel originales y verifica de forma independiente: conservación
de registros, que toda diferencia esté documentada en el log, la aritmética
recalculada desde cero, la coherencia entre datasets, la validez de los
campos que alimentan gráficos y que ningún dataset público filtre rutas.

Dependencias: `pip install openpyxl` únicamente (pypdf sólo si hace falta
releer la tesis; ningún script del pipeline usa pandas).
`05_worms.py` y `06_estudios.py` requieren red. El caché de WoRMS vive en
`data/private/worms_cache.json`; borrarlo fuerza la reconsulta.

### Módulos de referencia (curados a mano, son la fuente de verdad)

| Archivo | Contenido |
|---|---|
| `pipeline/taxonomy.py` | Tablas género→pared, planctónicos, normalización |
| `pipeline/corrections.py` | Registro auditable de TODAS las correcciones |
| `pipeline/localidades.py` | Georreferenciación por DOI + sitio MSH-BC-21 |
| `pipeline/caribe_referencia.py` | Fauna del Caribe extraída del cap. 4.2 |

---

## 3 bis. Los Excel corregidos

`60_excel.py` devuelve las correcciones al formato original, en dos archivos
NUEVOS dentro de `Data_nosubiralrepo/` (los originales no se tocan):

- **`BD FORAMS AMBTE FILTRACION - CORREGIDA.xlsx`** — Léeme · Base corregida
  (327 registros × 27 columnas) · Estudios · Taxones de la base · Taxones
  leídos de los artículos (515) · Correcciones (85).
- **`Coleccion MSH-BC-21 - CORREGIDA.xlsx`** — Léeme · Clasificación corregida
  · Índices recalculados · Abundancias · Correcciones.

Cada libro abre con una hoja «Léeme» que explica qué cambió, qué se añadió y
**qué no se pudo reconstruir**, para que el archivo se entienda sin el código
delante.

---

## 4. Los datos (data/derived/, 191 KB total)

| Archivo | Qué tiene |
|---|---|
| `estudios.json` | 40 estudios: cita, DOI, localidad, lat/lon, fluido, morfología, sitios, confianza |
| `taxones_global.json` | 197 taxones: recuentos curado y ampliado, bandas, microhábitats, pared, rango, AphiaID |
| `matriz_lat_prof.json` | Matriz 4×3 curada y ampliada + sitio de la tesis |
| `pared_por_banda.json` | % calcáreo/aglutinado por banda, con n |
| `msh_bc21.json` | 52 especies, índices, pared, abundancias por cm/fracción |
| `solape.json` | Intersección MSH ↔ literatura global |
| `caribe_referencia.json` | 5 localidades caribeñas + MSH-BC-21 |
| `correcciones.json` | 85 correcciones documentadas + resumen de impacto |
| `sinu_2024.json` | Barragán y Bernal 2024: 18 estaciones, δ13C, rango Shannon del campo |
| `taxones_completo.json` | 515 taxones leídos de los artículos; rankings de especies y géneros, dominancia declarada, estadísticas por estudio |

**Volumen decisivo:** 191 KB. Todo va en el bundle estático. NO hace falta
base de datos, ni API, ni Supabase.

---

## 5. Cifras clave ya verificadas (úsalas, no las recalcules)

- **40 estudios** (39 de filtración + 1 de fauna de referencia; 2 reincorporados).
  **197 taxones** (173 especies + 24 entradas de género). **39/40 georreferenciados**.
- Dos vistas de la base, y el dashboard ofrece la curada por defecto:
  **curada 257 registros** (la que sustenta la tesis) · **ampliada 309**
  (con los dos estudios reincorporados).
- Matriz latitud × profundidad: **6 de 12 celdas** en la curada, **8 de 12** en
  la ampliada. **El 80% de los registros procede de >500 m.**
- **LA CELDA 0-15° / <150 m ESTÁ EN CERO EN AMBAS VISTAS.** Ahí cae el Caribe
  colombiano. Que siga vacía al ampliar la base es la prueba de que el vacío
  es real y no un artefacto de la curación. Es el argumento más fuerte del
  trabajo.
- En la base curada la franja tropical (0-15°) se sostiene sobre **un único
  registro**; los 8 que aparentaban cubrirla venían de McCorkle 1990, que no
  es un estudio de filtración.
- **El ranking va por nº de ESTUDIOS, no de registros.** El recuento de
  registros premia a los artículos que desglosan más bandas. Top:
  *Uvigerina peregrina* (14 estudios) · *Lobatula wuellerstorfi* (10) ·
  *Globobulimina pacifica* (9).
- MSH-BC-21: S=52, **H'=3,4325**, J'=0,8687, Simpson D=0,0454,
  top-5 = 38,5% de la abundancia.
- MSH-BC-21 pared: **87,0% calcáreo / 13,0% aglutinado**
  (hialino 70,53 · porcelanáceo 13,13 · monocristalino 3,35 · aglutinado 13,0).
- Solape con la literatura, **contra la base curada**: 14/52 especies,
  19/41 géneros, **55,2% de la abundancia** de MSH-BC-21 en géneros ya
  reportados en filtraciones. Contra la ampliada: 18/52, 21/41, 56,8%.
- Log de correcciones: **85 entradas**. De ellas, **23 son errores reales del
  manuscrito** (6 erratas + 5 reclasificaciones de pared + 12 duplicados) que
  afectan **24 de los 293 registros = 8,2%**. Las 62 restantes no son errores
  del autor: nomenclatura abierta, actualizaciones de WoRMS posteriores a
  2022, exclusiones, taxones no verificables, notas aritméticas y las dos
  reincorporaciones.

---

## 6. Hallazgos que corrigen el manuscrito

1. **Tabla 1 mal ordenada.** `Cibicidoides wuellerstorfi` + `Cibicides
   wuellerstorfi` + `Planulina wüllerstorfi` son la MISMA especie; WoRMS la
   llama hoy **`Lobatula wuellerstorfi`** (ADN, Schweizer et al. 2009).
   Unificadas suman 11 registros → pasa a ser el 2º taxón mundial.
   *Refuerza* el argumento de la tesis.
2. **FBC/FBA 88,8% → 87,0%**, por reclasificar `Ammodiscus` (aglutinado, no
   porcelanáceo). El texto de la tesis dice «cerca de un 80%»: es incorrecto
   en ambos sentidos. Se publica el valor calculado (decisión del autor).
3. **Tasa de error real: 8,2%** — 23 entradas de corrección (6 erratas + 5
   reclasificaciones de pared + 12 duplicados) que afectan **24 de los 293
   registros**. Las otras 51 entradas del log no son errores del autor.
4. **12 filas duplicadas exactas** (mismo estudio, taxón, banda latitudinal,
   banda de profundidad y microhábitat). Eliminadas. Se conservan en cambio
   las 14 repeticiones de un taxón dentro de un estudio cuando cambia la
   banda: ahí el artículo reporta la especie en dos estratos distintos y son
   observaciones separadas, no duplicados.
5. **El ranking por nº de registros estaba sesgado.** Ahora se ordena por nº
   de estudios. *Globobulimina affinis* salía en el top-5 con 7 registros
   procedentes de sólo 3 estudios; con la métrica robusta baja de posición.
4. **`Cassidulina` es homónimo**: WoRMS devuelve un equinoideo. Filtrado por
   phylum en `05_worms.py::pick_foram`. No quitar ese filtro.
5. **`McCorkle et al. 1990` no es un estudio de filtración** (microhábitats,
   multi-sitio Atlántico/Pacífico). Aporta 18 registros. Pendiente decidir si
   se marca aparte.

---

## 7. PENDIENTE — requiere respuesta del usuario

### 7.1 Localidades — RESUELTO (2026-08-17)
El usuario aportó las coordenadas exactas. **37 de 38 estudios
georreferenciados.** El único sin coordenada es McCorkle et al. (1990), y es
correcto: es multi-sitio y además no documenta filtraciones.

Añadido el campo `tipo` en `localidades.py`: `frio` (35 estudios),
`hidrotermal` (Herguera 2014, Cuenca de Guaymas), `mixto` (Burkett 2018,
Costa Rica + Hydrate Ridge) y `no_filtracion` (McCorkle 1990). Burkett 2018
lleva además una lista `sitios` con sus 8 posiciones.

### 7.2 Estado de los PDF (2026-08-17)
45 artículos reunidos. 39 de los 40 estudios de la base tienen su PDF.
Renombrados a «Autor Año - Título.pdf»; tres movidos a
`Data_nosubiralrepo/Referencias excluidas/` (McCorkle 1990, no es filtración;
Gracia 2012, moluscos; Puerres 2022, revisión sin datos primarios).
Cuatro pendientes de integrar: Barragán y Bernal 2024, Babineaux 2025,
Fiorini 2015, Li 2021.

**Cuidado con el emparejador**: la firma de título debe buscarse SÓLO en la
primera página. Buscarla en tres capturó una cita de la bibliografía y
archivó el resumen P-43 de Panieri (2000) con el nombre de Sen Gupta y
Aharon (1994). `09_verificar_pdfs.py` existe para detectar eso; ejecutarlo
siempre después de `08_organizar.py`.

### 7.3 Referencia recuperada — RESUELTO (2026-08-17)
El estudio que no aparecía en CrossRef es **Chiang, M.-T., Thomas, E., Wei,
K.-Y., Lin, Y.-S., Lin, S. y Lin, A.T.-S. (2015)**, *EGU General Assembly
Conference Abstracts*. Es un resumen de congreso, de ahí que no tenga DOI. Se
recuperó de la bibliografía de Zhang et al. (2018). Son los mismos autores de
la referencia de proporciones de pared que usa la tesis (68/32 frente a
24/76). **Las 40 referencias están verificadas.**

### 7.3 bis Morfologías sin determinar (7 de 40)
Documentadas una a una en `tipologia.SIN_MORFOLOGIA`. En varios casos el texto
sí menciona pockmarks o volcanes de lodo, pero **la mención está en una tabla
comparativa de otras localidades o en la lista de referencias**, no en la
descripción del sitio muestreado. Asignarla sería inventar.

### 7.4 Antigua sección — una referencia no localizable
*«Diversity and Characteristics of Benthic Foraminifera in Cold Seep Areas in
the Active Margin of the northeastern South China Sea»* (4 registros).
No está en CrossRef ni aparece en búsqueda web. CrossRef devolvió una
coincidencia falsa (parafinas cloradas) que ya está anulada en `20_build.py`.

### 7.5 Ampliar la base de estudios
Propuesta hecha, sin respuesta: buscar de forma **dirigida** trabajos en
**0-15° de latitud y <150 m** (el hueco), en vez de ampliar en general.

---

## 8. Próximo paso: Fase 1 (UI)

Repo vacío de frontend. Nada de Next.js creado todavía.

**Stack acordado:** Next.js 15 (App Router) + TypeScript + export estático ·
Tailwind v4 + tokens CSS · Observable Plot (85% de los gráficos) + D3 puntual
(treemap, UpSet) · d3-geo + TopoJSON para el mapa (sin tiles externos) ·
`next/font` self-hosted · bilingüe ES/EN desde el inicio · deploy a Vercel.

**Herramientas verificadas disponibles:** node v24.18.0, npm 11.16.0,
git 2.55.0, gh 2.96.0 (autenticado como `ErickFMR777`), Vercel CLI 57.0.0,
Python 3.14.6 con pandas 3.0.5 y openpyxl.

**Orden sugerido:**
1. Andamiaje Next.js + sistema de diseño (tokens, tipografía, doble tema).
2. Matriz lat×prof (Historia 1) — la de mayor impacto y menor esfuerzo.
3. Barras de pared por banda (Historia 4).
4. Mapa mundial de estudios.
5. Resto de historias (ver §9).

---

## 9. Las 6 historias de datos aprobadas

| # | Historia | Esfuerzo | Datos |
|---|---|---|---|
| 1 | El punto ciego (matriz lat×prof + mapa) | Bajo/Alto | `matriz_lat_prof`, `estudios` |
| 2 | ¿Qué tan *seep* se ve MSH-BC-21? (4 criterios) | Medio | `msh_bc21` + umbrales de literatura |
| 3 | Fauna de seep o de plataforma tropical | Medio | `solape`, `taxones_global`, `msh_bc21` |
| 4 | La firma de la pared (FBC/FBA por banda) | Bajo | `pared_por_banda` |
| 5 | El Caribe contra sí mismo | Alto | `caribe_referencia` |
| 6 | Dentro del testigo (2 cm × 3 fracciones) | Bajo | `msh_bc21.abundancias` |

**Historia 1 — encuadre correcto:** el titular NO es «sólo 3 de 12 celdas»
(eso era un error, son 6). El argumento sólido es doble: (a) el 82% de los
registros procede de >500 m y 3 de las 4 bandas latitudinales carecen por
completo de datos someros; (b) la celda 0-15° / <150 m está vacía, y es
justo donde cae el Caribe colombiano. Usar esas dos cifras, no la primera.

**Historia 2 — RESUELTA por Barragán y Bernal (2024).** La tesis trató su
H'=3,43 como una anomalía frente a la literatura, que predice diversidad baja
en filtraciones. Ese trabajo mide **Shannon de 3,0 a 3,8 en las 18 estaciones
del mismo campo del Sinú**, incluidas las de actividad alta. Es decir: en esta
plataforma tropical la diversidad alta es lo normal Y es compatible con
filtración activa. El valor de la tesis deja de ser una anomalía y pasa a
estar dentro del rango esperable. Los datos están en `sinu_2024.json`; la
narrativa correcta ya no es «3 de 4 criterios» sino «los 4 se cumplen una vez
que existe una línea base local».

---

## 10. Dirección visual acordada

Concepto: **el microscopio**. El activo dominante es la lámina SEM de la
tesis (p. 35: 8 especies × 3 vistas, grises sobre negro, barras de escala).

- Base oscura `#0B0D0E` / superficies `#16191B` / texto `#E8E6E3`.
  Modo claro derivado (crema `#FAF8F5`) para impresión.
- El color **codifica variables, nunca decora**: hialino `#5B8DB8` ·
  porcelanáceo `#5AA08C` · aglutinado `#C9903F` · acento seep `#E8873A` ·
  sin datos `#2A2F33` con trama (debe leerse VACÍO, no cero).
- Serif editorial en titulares (Source Serif 4 / Newsreader), sans neutral en
  cuerpo (Inter), `tabular-nums` en cifras.
- **Nombres de especies siempre en cursiva** — componente `<Taxon>`.
- Doble modo: `Narrativa` (una idea por pantalla, jerga glosada) ↔
  `Exploración` (n visible, filtros, tablas, notas de método).
- Accesibilidad: contraste AA, no depender sólo de color, teclado,
  `prefers-reduced-motion`.

---

## 11. Decisiones del usuario (2026-08-16)

- Mostrar **valores reales**, no los del manuscrito, donde difieran.
- **Documentar todas las correcciones** como ajustes al trabajo original.
- Bilingüe ES/EN. Deploy en Vercel.
- No hay datos de isótopos (δ13C): no se trabajaron.
- No hay más data cruda: una sola muestra (MSH-BC-21), sin sitios de control.
- Las referencias SÍ se publican (rectificación explícita).
