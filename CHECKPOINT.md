# CHECKPOINT — Dashboard Tesis Foraminíferos

**Última actualización:** 2026-08-18 · COMPLETO Y DESPLEGADO · auditoría 89/89
**Novedad:** auditoría integral del repositorio, limpieza de código muerto y
README. Ver §12.

Documento de continuidad: si la sesión se corta, esto es lo que hace falta
para retomar sin releer nada.

> **Cifras verificadas contra `data/derived/` el 2026-08-17**, después de
> ampliar la base. Este documento ya ha tenido cifras obsoletas tres veces:
> si cambias el pipeline, **regenera los §4 y §5 desde los datos**, no los
> edites a mano. `python pipeline/99_auditoria.py` debe salir en 0 antes de
> dar por buena cualquier cifra de aquí.

---

## 1. Qué es esto

Dashboard interactivo bilingüe (ES/EN) sobre la tesis de grado de **Erick
Francisco Mendoza Rivero, Ingeniero Geólogo** (Universidad Nacional de
Colombia, sede Medellín, Facultad de Minas, Departamento de Geociencias y
Medio Ambiente, 2023): *«Análisis de las asociaciones de foraminíferos
bentónicos en filtraciones de metano: comparación entre distintas localidades
y la plataforma continental del Caribe colombiano»*. Directora: Ph.D. Gladys
Rocío Bernal Franco.

**Alcance mundial**, con el Caribe colombiano como localidad propia — no es un
estudio local, y el titular del dashboard lo dice desde 2026-08-18.

Marco, verificado contra el informe técnico final de la beca-pasantía
(`Data_nosubiralrepo/Informe_tecnico_avance_final_jovenes_investigadores_UNAL-EFMR.pdf`):

| | |
|---|---|
| Proyecto | Methane seep hunting: A multi-scale and multi method approach |
| Programa CTeI | Programa Nacional de Ciencia, Tecnología e Innovación en Geociencias |
| Convocatoria | 877-2020 (geociencias para el sector de hidrocarburos) |
| Contrato / convenio | 80740-143-2021 (Minciencias — Entidad) |
| **Financiación** | **Convenio 785/668 de 2019**, suscrito entre la **Agencia Nacional de Hidrocarburos (ANH)**, el **Ministerio de Ciencia, Tecnología e Innovación** y el **Fondo Francisco José de Caldas** |
| Grupo | OCEÁNICOS |
| Entidades ejecutoras y beneficiarias | UNAL · UPB · GMAS · GEOMARES · ACGGP (la UNAL va primero) |
| Vinculación | Jóvenes Investigadores, 21-08-2021 a 31-03-2024 |

La ficha completa se publica en el pie del dashboard y en el informe en PDF.
Las cédulas del informe técnico son datos personales: no se publican.

**Destino:** Vercel. **Públicos:** comunidad académica internacional +
reclutadores de tech/datos.

---

## 1 bis. Despliegue

**En línea y de acceso libre:** https://foraminiferos-bentonicos-filtraciones-metano.vercel.app
**Repositorio:** https://github.com/ErickFMR777/foraminiferos-bentonicos-filtraciones-metano

Proyecto de Vercel `foraminiferos-bentonicos-filtraciones-metano` (cuenta erickfmr777), **conectado a GitHub**: el
despliegue lo dispara el push, no `vercel deploy`.

Los nombres anteriores —`foraminiferos-caribe` y luego
`foraminiferos-caribe-colombiano`— reducían al Caribe un trabajo de alcance
mundial, el mismo error que ya se corrigió en el titular de la página. El
nombre actual nombra el organismo y el ambiente, que es lo que el trabajo
estudia, y es el mismo en el repositorio, en el proyecto de Vercel y en el
dominio.

Nota histórica que ha caducado: antes hubo que recrear el proyecto porque el
CLI no sabía renombrar. **Ya sí**: `vercel project rename viejo nuevo` (CLI 57).

**Dos cosas que el renombrado NO hace solo**, y costaron un 404 y un 302:

1. **No crea el dominio nuevo.** Renombrar el proyecto deja
   `<nombre-nuevo>.vercel.app` sin asignar: hay que crearlo con
   `vercel alias set <deployment> <dominio>`. El dominio viejo sigue vivo
   apuntando al mismo despliegue, así que ningún enlace ya compartido se rompe.
2. **El proyecto tenía protección SSO** (`ssoProtection.deploymentType =
   all_except_custom_domains`), heredada de la etapa con contraseña. El dominio
   viejo estaba exento por ser el de producción, pero el nuevo alias caía en
   ella y devolvía 302 a `vercel.com/sso-api`: el sitio parecía roto estando
   bien. Se retiró con `vercel project protection disable <proyecto> --sso`.
   **Si algún día vuelve a cerrarse el sitio, esta es la palanca**, no el
   middleware.

### Historial: la etapa con contraseña (retirada el 2026-08-18, ver §16)

Lo que sigue **ya no está en el código**. Se conserva porque describe una
decisión razonada y porque, si el sitio vuelve a cerrarse, esto es el plano.

**Autenticación con sesión de cookie.** Antes era HTTP
básica; se cambió porque la básica no admite cambiar la contraseña: el
navegador cachea las credenciales, no existe cerrar sesión, y la clave vivía
en una variable de entorno que sólo se toca redesplegando.

- La cookie va firmada con HMAC-SHA256 (`SESION_SECRETO`) y dura 12 horas. El
  middleware valida la firma en el edge **sin leer el almacén**.
- La contraseña vive en un almacén **Vercel Blob privado**, como derivación
  PBKDF2-SHA256 (210.000 iteraciones) con sal. Su token alcanza sólo a ese
  almacén; se descartó Edge Config y la variable de entorno porque escribir en
  ellas exige un token con poder sobre TODA la cuenta.
- Se cambia desde la sección **08 · Cuenta** del dashboard.
- **Cambiarla exige además la respuesta a una pregunta de seguridad**
  (`DASHBOARD_RESPUESTA`), para poder compartir el acceso sin ceder el
  control: quien reciba la contraseña lo ve todo, pero no puede cambiarla.
  Distingue mayúsculas, se guarda derivada y **sobrevive al cambio de
  contraseña**. Sin ella configurada, el cambio queda bloqueado.
- `DASHBOARD_USUARIO` / `DASHBOARD_CLAVE` sólo siembran el almacén la primera
  vez. **Recuperación si se olvida la contraseña:** borrar el blob
  `auth/credenciales.json` y vuelven a mandar esas dos variables.
- Si falta `SESION_SECRETO` el sitio queda abierto, que es lo cómodo en local.

Probado de extremo a extremo contra producción: contraseña incorrecta,
demasiado corta, igual a la actual, cambio válido, la antigua deja de entrar,
la nueva entra, y cambiar la clave sin sesión responde 401.

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
python pipeline/45_tablas_pdf.py     # TABLAS: d13C, abundancias, indices
python pipeline/50_estadisticas.py   # -> taxones_completo.json
python pipeline/30_informe.py    # -> Informe_curacion_datos.pdf
python pipeline/60_excel.py      # -> los dos Excel corregidos (carpeta privada)
python pipeline/99_auditoria.py  # 91 comprobaciones; código 1 si algo falla
# El orden completo, con 07/45, esta en CLAUDE.md y en el README.
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

- **`BD FORAMS AMBTE FILTRACION - CORREGIDA.xlsx`** (229 KB) — Léeme · Base
  corregida (327 × 27) · Estudios (40 × 18) · Taxones de la base (197) ·
  Taxones leídos de los artículos (515, con los IDs de quién los reporta y de
  quién los declara dominantes) · **Asociaciones por estudio (1.527 pares
  estudio-taxón)** · **Resumen por estudio (36)** · Correcciones (85).
- **`Coleccion MSH-BC-21 - CORREGIDA.xlsx`** — Léeme · Clasificación corregida
  (52, con `Pi` y `Pi*Ln(Pi)` por especie, como el original) · Índices
  recalculados · Abundancias · Correcciones.

Las **asociaciones por estudio son el aporte que la tesis no tenía**: su base
recogía «las 5 principales especies» por filtro —una muestra de las
dominantes—, y esta hoja trae todo lo que cada artículo nombra.

Las tres señales no valen lo mismo y el Léeme lo declara: **presencia**
(sólida), **menciones** (proxy débil, no comparable entre artículos de
distinta extensión) y **dominante declarado** (la única que puede llamarse
dominancia).

Cada libro abre con una hoja «Léeme» que explica qué cambió, qué se añadió y
**qué no se pudo reconstruir**, para que el archivo se entienda sin el código
delante.

**Lo que sigue sin extraerse, y está declarado en el Léeme:** de los 36
artículos legibles, 33 mencionan abundancias relativas, 25 traen δ13C y 9
índices de diversidad — **ninguna cifra de eso se extrajo**. Vive en tablas
que pypdf no interpreta de forma fiable. E13 es un PDF escaneado sin capa de
texto. 7 de 40 estudios siguen sin morfología asignada.

`99_auditoria.py` verifica ahora estos libros si existen: que la hoja de
asociaciones conserve los 1.527 pares, que las 150 dominancias cuadren con el
pipeline y que `Pi*Ln(Pi)` reconstruya el Shannon publicado (3,4325).

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
- ~~Doble modo `Narrativa` ↔ `Exploración`~~: se implementó y se retiró el
  2026-08-18 — sólo cambiaba el `n=` de dos barras. Antiguamente:
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


---

## 12. Auditoría integral (2026-08-18)

Revisión completa del repositorio a petición del autor. **Resultado: 89/89 en
la auditoría, tipos limpios, cero fugas.** Lo que se encontró y se hizo:

### Un hueco real de extracción, corregido
`Li et al.` estaba en la base como **resumen de Goldschmidt 2020**
(`10.46427/gold2020.1503`), pero el PDF de la carpeta es el **artículo completo**
(*Ore Geology Reviews*, 2021, `10.1016/j.oregeorev.2021.104247`). Al no casar
los DOI, el emparejador lo dejaba fuera y **sus taxones no se extraían de
ninguna parte**. Se añadió una equivalencia de DOI documentada en `07_pdfs.py`.
Cobertura: de 37 a **38 artículos leídos**; E37 aporta 7 taxones.

Los dos estudios que siguen sin extracción **no tienen PDF** y es correcto:
E05 (McCorkle 1990, que además no es de filtración) y E26 (Chiang 2015, resumen
de congreso de la EGU).

### Código muerto retirado
- **npm:** `@observablehq/plot`, `d3-array`, `d3-scale` y sus `@types` — cero
  importaciones. Se planearon en la fase de diseño y todos los gráficos
  acabaron siendo SVG escrito a mano. `node_modules` baja de 395 a 388 MB.
- **i18n:** 11 de 15 claves del diccionario estaban muertas, restos del modo
  narrativa/exploración y de tablas que nunca se construyeron.
- **Exports:** `normalizaRespuesta` y `HORAS_SESION` se usaban sólo dentro de su
  módulo.
- **`package.json`:** el script `lint` (`next lint`) prometía una verificación
  inexistente —no hay ESLint— y se sustituyó por `npm run verificar`.

### Seguridad, verificada de nuevo
Cero secretos en los archivos versionados **y en todo el historial**; ningún
`.xlsx`, `.env` ni ruta privada ha existido jamás en un commit; los **18
despliegues vivos** revisados uno a uno contra la API: **0 archivos
confidenciales**; ninguna ruta del sistema ni texto literal de artículos en los
datos públicos.

### Reproducibilidad
Se regeneró el pipeline completo y se comparó archivo por archivo con lo
publicado: **los 11 datasets salen idénticos**. No hay deriva entre el código y
los datos.

### Datasets sin consumidor — RESUELTO
Los dos que quedaban pendientes ya tienen destino, y ninguno se retiró:

- `caribe_referencia.json` lo lee `Caribe.tsx`, la sección **07 · El Caribe
  contra sí mismo**. Era la historia que faltaba por construir.
- `cuantitativos.json` **no lo lee ningún componente, y así se queda**: su
  consumidor es `60_excel.py`, que con él escribe las columnas de δ13C,
  abundancias e índices de los Excel corregidos. Es público por ser agregados
  sin texto literal, pero su destino es la carpeta privada del autor. Borrarlo
  por «no lo importa nadie» rompe los Excel en silencio: ni `tsc` ni el build
  lo notarían.


---

## 13. Cierre: los datos huérfanos, resueltos (2026-08-18)

Los dos datasets que se generaban sin consumidor ya tienen destino, decidido
**midiendo el solape con la base curada (309 registros)**:

| Dato | Solape | Destino |
|---|---|---|
| δ13C | **73 %** (14/19) | Columnas en la **base principal** del Excel |
| Abundancias | **17 %** (34/200) | Hoja **«Asociaciones por estudio»** (vista ampliada) |
| Fauna caribeña | — | **Sección 07**, como contraste. NUNCA fusionada |

**Por qué la fauna caribeña no entra en la base principal.** Las cinco
localidades (manglar, estuario, arrecife) caen todas en la banda **0-15°** y son
someras: fusionarlas metería 4-5 entradas en la celda 0-15° / <150 m, que hoy
está en cero y es el argumento central del trabajo. Serían entradas de fauna
que **no es de filtración**, igual que McCorkle (1990). El titular «nadie ha
estudiado esto aquí» se volvería falso por un artefacto de la propia base.

**Lo que aporta puesta como contraste:** en las cinco localidades caribeñas una
sola especie se lleva del **29 al 61 %** de la asociación; en MSH-BC-21 la más
abundante no llega al **11 %**. Lo que distingue la muestra no es el elenco de
especies sino el reparto — que es justo lo que mide su J′ = 0,8687.

El dashboard pasó entonces a **nueve secciones**; Límites es 08 y Cuenta era
la 09. Al abrir el sitio (§16) desapareció Cuenta y quedaron **ocho**.

---

## 14. Errores de morfología y localidad (2026-08-18)

El autor detectó en el mapa que Dessandier (2019) figuraba como **«pingo de
hidratos»** y le sonó raro. Tenía razón, y al tirar del hilo aparecieron cuatro
asignaciones mal fundadas.

| ID | Decía | Dice ahora | Por qué |
|---|---|---|---|
| **E24** | Pingos de Storfjordrenna, 76,1 N, 380 m | **Vestnesa Ridge**, 79,0 N, 1200 m, pockmark | Su texto no dice «pingo» ni una vez y dice «pockmark» 30. Estaba **a 330 km** de su sitio |
| **E03** | Pockmark | **Tapete bacteriano** | «Pockmark» salía una vez, y era **en su propia bibliografía** |
| **E36** | Banco de bivalvos | **Montículo de hidratos** | Describía la fauna, no el fondo: «scarps and mounds», sitios Mounds 11 y 12 |
| **E10** | Montículo de hidratos | **sin determinar** | Multi-sitio por el margen de Cascadia; no hay morfología única |
| E25 | (se mantiene) | fuente corregida | El artículo dice «methane vent», nunca «hydrothermal» |

**La causa común: inferencias presentadas como evidencia.** E24 llevaba
`fuente="título y resumen"` y el título no menciona Storfjordrenna; E03 citaba
otro artículo del mismo grupo.

**Comprobación nueva en la auditoría (91 en total):** toda morfología asignada
debe aparecer en el CUERPO de su artículo, descartando la bibliografía. Las
excepciones legítimas —la localidad documentada en la literatura, como Hydrate
Ridge— van declaradas en `tipologia.JUSTIFICADA_POR_LOCALIDAD`, y la auditoría
vigila que no se multipliquen.

Morfologías asignadas: **32 de 40** (antes 33; E10 pasó a sin determinar).


---

## 15. El mapa, interactivo (2026-08-18)

El autor detectó dos cosas: que un estudio no aparecía y que había puntos
dibujados **fuera del mapa, al norte**. Ambas venían del apaño anterior — un
abanico con relajación que empujaba los puntos y llegó a sacar a E23 por encima
del borde (y = 6,5 con el marco en 8).

Sustituido por lo que pidió, que además es lo correcto:

- **Zoom y arrastre** propios (rueda, botones, ×1 a ×12), con la vista sujeta
  para que el mapa no se pueda sacar del marco.
- **Agrupación por distancia EN PANTALLA**: los solapados se muestran como un
  círculo con el número de estudios, y al acercar se separan solos porque la
  distancia en pantalla crece. **Ningún punto se desplaza de su posición real.**
- **Coordenadas idénticas**: no hay zoom que las separe, así que al pulsar el
  círculo se despliega la lista de sus estudios bajo el mapa.
- **`clipPath`**: nada puede dibujarse fuera del marco, pase lo que pase.

Verificado contra el despliegue: 8 puntos sueltos + 7 grupos que suman 31 = los
39 georreferenciados, 0 fuera del marco.


---

## 16. El sitio se abre al público (2026-08-18)

Decisión del autor: la tesis se entregó hace más de dos años y aún no ha salido
como artículo, pero el trabajo de grado está entregado y **el dashboard pasa a
ser parte de su portafolio**. Se retira la autenticación entera.

**Qué se quitó**

| Ruta | |
|---|---|
| `src/middleware.ts` | La puerta en el edge |
| `src/lib/sesion.ts` | Firma HMAC de la cookie |
| `src/lib/credenciales.ts` | Almacén Blob, PBKDF2, pregunta de seguridad |
| `src/app/api/` | Las tres rutas: entrar, salir, clave |
| `src/components/Cuenta.tsx` | La sección 09 |
| `.env.example` | Ya no hay variables de entorno que documentar |
| `@vercel/blob` | La única dependencia que existía por la contraseña |

**Qué cambió con ello**

- `next.config.ts` recupera `output: "export"`. Era lo único que lo impedía:
  un export estático no admite middleware. `npm run build` deja el sitio en
  `out/`, sin servidor ni consultas en runtime.
- `layout.tsx` pasa de `robots: { index: false }` a `index: true`. Antes se
  pedía no aparecer en buscadores; ahora es lo que se busca.
- El dashboard queda en **ocho secciones**, de «01 · El vacío» a
  «08 · Límites».

**Lo que NO cambió, y es lo importante**

Se abrió el dashboard, no los datos. `Data_nosubiralrepo/` y `data/private/`
siguen sin publicarse, y `.vercelignore` sigue siendo obligatorio — de hecho
pasa a importar más, porque ya no hay un 401 detrás por si algo se cuela.

Por lo mismo, dos comprobaciones de `99_auditoria.py` dejan de ser red de
seguridad y pasan a ser **la única defensa**: que ningún dataset público lleve
texto literal de los artículos y que ninguno exponga rutas del sistema de
archivos. Las dos siguen en verde.

**Verificado:** `tsc --noEmit` limpio, build con export estático correcto,
auditoría 91/91, y en el HTML servido cero apariciones de «contraseña» o
«password», ocho secciones y `<meta name="robots" content="index, follow">`.

---

## 17. Depuración e interventoría independiente (2026-08-18)

Barrido completo antes de publicar el repositorio. Lo que salió:

### Bugs encontrados y corregidos

| | Dónde | Qué pasaba |
|---|---|---|
| 1 | `MatrizLatProf` | La tinta de la cifra era un **hex fijo** sobre un fondo que sí cambia con el tema. En oscuro, el paso 100 quedaba a **contraste 1,00** (cifra invisible) y el 250 a 1,47 |
| 2 | `MatrizLatProf` | El subtítulo iba a `opacity-80`: peor caso 3,88, por debajo de AA |
| 3 | `08_organizar.py` | El manifiesto guardaba el **DOI leído del PDF**, truncado por un salto de línea en Fontanier 2014. Cualquier cruce por ese campo perdía el estudio |
| 4 | `08_organizar.py` | El emparejado por prefijo **no tenía longitud mínima**: un prefijo corto podía casar con el primer estudio que empezara igual |
| 5 | `package.json` | `geojson` se importaba como tipo sin estar declarado; llegaba de rebote por `@types/d3-geo` |

Las tintas viven ahora en `globals.css` como `--seq-*-tinta`, con su ratio
anotado. **Peor caso tras la corrección: 5,08** (AA texto normal exige 4,5), y
4,58 en el subtítulo con `opacity-90`.

### Código muerto retirado

- El bloque `@theme inline` entero: generaba utilidades (`bg-page`, `text-ink`,
  `font-serif`) que no usa **ni un** componente. El proyecto escribe siempre
  `bg-(--page)`, que lee la variable directamente. Verificado tras quitarlo que
  las dos fuentes siguen aplicándose.
- El `export` de `Idioma`: nadie lo importaba fuera de `i18n.tsx`.
- Tres imports muertos: `taxonomy as T` en `05_worms`, `math` en `10_clean`,
  `Counter` en `60_excel`.
- `--seq-700` estaba declarado en los tres bloques de tema y sin usar. **No se
  borró: se usa**, es la tinta de los pasos claros en modo claro.

### Comprobación nueva

`99_auditoria.py` pasa a **92 comprobaciones**. La nueva falla si vuelve a
aparecer un color en hex dentro de `src/components/` — la clase de error del
bug 1, que llevaba ahí desde el principio sin que nada lo detectara.

### Frescura de los datos

Se regeneró el pipeline entero desde los Excel originales y se comparó archivo
por archivo: **los 11 datasets salen byte a byte idénticos**. No hay deriva
entre el código y lo publicado.

### Verificación inversa de lo extraído

La auditoría comprueba coherencia interna; faltaba la pregunta contraria: *¿está
cada cifra publicada realmente en su artículo?* Se tomaron los **991 valores**
de tabla y los **9 índices** y se buscaron en la página que cada uno cita.

**991 de 991 y 9 de 9 aparecen donde dicen.** Las 166 fallidas en la primera
pasada eran el signo menos Unicode (U+2212) frente al guion ASCII: fallo de la
sonda, no del dato.

**Cómo NO se puede verificar esto, y conviene recordarlo.** Se probaron antes
dos sondas independientes —lectura por líneas y `extract_tables()` de
pdfplumber— y ambas daban cero incluso en los estudios donde el pipeline sí
extrae. El control positivo falló, así que el resultado intermedio («17
estudios con tablas sin extraer») **no valía y se descartó**. Estas tablas sólo
se dejan leer agrupando palabras por coordenada vertical.

### Confidencialidad antes de publicar

- Recorrido **todo el historial de git**, no sólo el árbol actual: ningún
  `.xlsx`, ningún PDF salvo `Informe_curacion_datos.pdf`, que es la excepción
  declarada. Nunca hubo un commit con datos primarios.
- Sin secretos en ningún commit: las plantillas `.env.example` siempre tuvieron
  los valores vacíos, y la respuesta de seguridad nunca se escribió a disco
  versionado.
- Las coincidencias de «cédula», `C:\Users` u `OneDrive` en el historial son
  **las propias reglas que los prohíben**, no datos.

### Cobertura de la extracción, sin maquillar

| | |
|---|---|
| Referencias verificadas | 40/40 |
| Taxones con AphiaID de WoRMS | **531/531** |
| Georreferenciados | 39/40 |
| Con morfología | 32/40 (los 8 restantes se muestran como pendientes) |
| Estudios con tabla legible por máquina | 8 de 37 con PDF |

Los 29 sin tabla legible están **nominados** en `tablas_pdf.json`. Tablas
rasterizadas o con columnas entrelazadas: no es una carencia oculta, es una
carencia declarada.
