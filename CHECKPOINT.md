# CHECKPOINT — Dashboard Tesis Foraminíferos

**Última actualización:** 2026-08-17 · Fase 0 (datos) COMPLETA · Fase 1 (UI) NO INICIADA

Documento de continuidad: si la sesión se corta, esto es lo que hace falta
para retomar sin releer nada.

> **Todas las cifras del §5 fueron verificadas contra `data/derived/` el
> 2026-08-17.** En esa revisión se corrigieron tres errores de este mismo
> documento: la lectura de la matriz («3 de 12» → 6 de 12), la tasa de error
> (3,8% → 4,1%) y una dependencia inexistente (pandas). Si vuelves a citar
> una cifra de aquí, es fiable; si añades una nueva, verifícala igual.

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

## 2. REGLAS DE CONFIDENCIALIDAD (no negociables)

- `Data_nosubiralrepo/` NUNCA se sube. Contiene la tesis en PDF y dos Excel
  con datos primarios inéditos del proyecto MSH.
- `data/private/` NUNCA se sube (extracciones intermedias).
- Ya están en `.gitignore`, junto con `*.xlsx`, `*.pdf`, `.env*`.
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
python pipeline/20_build.py      # -> data/derived/*.json (público)
```

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

## 4. Los datos (data/derived/, 125 KB total)

| Archivo | Qué tiene |
|---|---|
| `estudios.json` | 38 estudios: cita, DOI, localidad, lat/lon, confianza |
| `taxones_global.json` | 160 taxones: registros, estudios, bandas, pared, AphiaID |
| `matriz_lat_prof.json` | Matriz 4×3 + posición de MSH-BC-21 |
| `pared_por_banda.json` | % calcáreo/aglutinado por banda, con n |
| `msh_bc21.json` | 52 especies, índices, pared, abundancias por cm/fracción |
| `solape.json` | Intersección MSH ↔ literatura global |
| `caribe_referencia.json` | 5 localidades caribeñas + MSH-BC-21 |
| `correcciones.json` | 67 correcciones documentadas + resumen de impacto |

**Volumen decisivo:** 125 KB. Todo va en el bundle estático. NO hace falta
base de datos, ni API, ni Supabase.

---

## 5. Cifras clave ya verificadas (úsalas, no las recalcules)

- Base bibliográfica: **287 registros** (tras excluir 5 planctónicos + 1
  placeholder), **160 taxones**, **38 estudios**.
- Matriz latitud × profundidad: **6 de 12 celdas con datos**. El sesgo real
  está en la profundidad: **el 82% de los registros (235 de 287) viene de
  >500 m**, y **3 de las 4 bandas latitudinales sólo tienen datos a >500 m**
  (todo lo somero procede de una única banda, 30-60°).
  La celda 0-15° / <150 m —donde cae el Caribe colombiano— está en **CERO**.
- MSH-BC-21: S=52, **H'=3,4325**, J'=0,8687, Simpson D=0,0454,
  top-5 = 38,5% de la abundancia.
- MSH-BC-21 pared: **87,0% calcáreo / 13,0% aglutinado**
  (hialino 70,53 · porcelanáceo 13,13 · monocristalino 3,35 · aglutinado 13,0).
- Solape: **15/52 especies** y **20/41 géneros** compartidos con la literatura
  global de seeps. **55,7% de la abundancia** de MSH-BC-21 está en géneros ya
  reportados en filtraciones.
- Top global corregido: *Uvigerina peregrina* (17 reg/15 est) ·
  ***Lobatula wuellerstorfi*** (11/10) · *Globobulimina pacifica* (10/9).

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
3. **Tasa de error real: 4,1%** — 11 entradas de corrección (6 erratas + 5
   reclasificaciones de pared) que afectan **12 de los 293 registros**
   originales. Las otras 56 entradas del log son normalización de
   nomenclatura abierta, actualizaciones de WoRMS posteriores a 2022,
   exclusiones y notas aritméticas: no son errores del autor.
4. **`Cassidulina` es homónimo**: WoRMS devuelve un equinoideo. Filtrado por
   phylum en `05_worms.py::pick_foram`. No quitar ese filtro.
5. **`McCorkle et al. 1990` no es un estudio de filtración** (microhábitats,
   multi-sitio Atlántico/Pacífico). Aporta 18 registros. Pendiente decidir si
   se marca aparte.

---

## 7. PENDIENTE — requiere respuesta del usuario

### 7.1 Cinco estudios sin localidad (tiene los PDFs)
- Bernhard, Martin & Rathburn (2010) — *Combined carbonate carbon isotopic…*
- Herguera et al. (2014) — *Limits to the sensitivity…*
- Burkett et al. (2016) — *Colonization of over a thousand…*
- Burkett et al. (2018) — *Influences of thermal and fluid characteristics…*
- McCorkle et al. (1990) — multi-sitio, ¿marcar como no-seep?

Al resolverlas: editar `pipeline/localidades.py` y re-ejecutar `20_build.py`.

### 7.2 Una referencia no localizable
*«Diversity and Characteristics of Benthic Foraminifera in Cold Seep Areas in
the Active Margin of the northeastern South China Sea»* (4 registros).
No está en CrossRef ni aparece en búsqueda web. CrossRef devolvió una
coincidencia falsa (parafinas cloradas) que ya está anulada en `20_build.py`.

### 7.3 Ampliar la base de estudios
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

**Historia 2 — el nudo narrativo:** 3 de 4 criterios de seep se cumplen y uno
los contradice (diversidad ALTA, H'=3,43, cuando la literatura predice baja).
Esa tensión es el mejor material de la pieza; no resolverla artificialmente.

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
