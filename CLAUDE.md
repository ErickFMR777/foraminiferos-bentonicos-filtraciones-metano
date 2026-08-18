# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Todo el proyecto está en español: identificadores, comentarios, documentación
y mensajes de commit. Mantener esa convención.

---

## Qué es esto

Dashboard editorial bilingüe (ES/EN) sobre la tesis de grado de **Erick
Francisco Mendoza Rivero, Ingeniero Geólogo** (Universidad Nacional de
Colombia, sede Medellín, Facultad de Minas, Departamento de Geociencias y
Medio Ambiente, 2023; directora Ph.D. Gladys Rocío Bernal Franco). No es un
panel de KPI: cada sección es una historia de datos con su método declarado.

**El alcance es mundial, y el titular debe reflejarlo.** La tesis compara
localidades de todo el planeta *y* la plataforma continental del Caribe
colombiano; el Caribe es la localidad propia del autor, no el objeto único.
Un título que sólo nombre el Caribe representa mal el trabajo.

Datos del proyecto, verificados contra el informe técnico final de la
beca-pasantía (no inventar ni aproximar estos identificadores):

| | |
|---|---|
| Proyecto | Methane seep hunting: A multi-scale and multi method approach |
| Programa CTeI | Programa Nacional de Ciencia, Tecnología e Innovación en Geociencias |
| Convocatoria | 877-2020 — financiación de proy. de inv. en geociencias para el sector de hidrocarburos |
| Contrato / convenio | 80740-143-2021 (Minciencias — Entidad) |
| **Financiación** | **Convenio 785/668 de 2019**, suscrito entre la **Agencia Nacional de Hidrocarburos (ANH)**, el **Ministerio de Ciencia, Tecnología e Innovación** y el **Fondo Francisco José de Caldas** |
| Grupo | OCEÁNICOS |
| Entidades ejecutoras y beneficiarias | UNAL · UPB · GMAS · GEOMARES · ACGGP (la UNAL va primero) |
| Vinculación | Beca-pasantía Jóvenes Investigadores, 21-08-2021 a 31-03-2024 |

**La tesis está entregada a la Universidad Nacional.** No decir que «no está
publicada»: lo que sigue siendo inédito son los datos primarios del proyecto
MSH. Las cédulas que aparecen en el informe técnico son datos personales y no
se publican en ningún artefacto.

**La tesis es de 2023.** La portada del PDF dice 2022, pero es un error del
propio documento que el autor rectificó: el trabajo de grado (3007442) se
entregó en el primer período académico de 2023 (2023-1S). El dashboard y el
informe lo aclaran en una nota, en vez de callarlo. Cuidado al corregir años: **no todo
`2022` del repo es la tesis.** Se quedan como están la fecha de consulta de
WoRMS (nov-2022, declarada en el manuscrito y de la que depende la distinción
`errata` / `actualizacion`), el año de Puerres 2022 y las campañas de campo de
mayo-junio de 2022. Cambiar la fecha de WoRMS corrompería el registro de
correcciones.

Dos mitades independientes:

1. **Pipeline en Python** (`pipeline/`) — cura los Excel originales de la
   tesis y produce agregados públicos.
2. **Frontend Next.js** (`src/`) — consume esos agregados como JSON estático.

No hay base de datos, ni API, ni consultas en runtime. Los datasets viajan
dentro del bundle: 555 KB en `data/derived/`, de los que ~440 KB llegan al
cliente —`taxones_global.json` y `cuantitativos.json` no los importa ningún
componente—. El grueso es `taxones_completo.json` (325 KB), que creció al leer
los artículos enteros.

---

## Regla no negociable: confidencialidad

Los datos primarios son inéditos (proyecto MSH, *Methane seep hunting*).

| Ruta | Estado |
|---|---|
| `Data_nosubiralrepo/` | **NUNCA** se sube. Tesis en PDF, artículos y los dos Excel |
| `data/private/` | **NUNCA** se sube. Extracciones intermedias, cita texto literal |
| `data/derived/` | Público. Sólo agregados, índices y tablas derivadas |
| `Informe_curacion_datos.pdf` | Público. Único PDF versionado (excepción explícita en `.gitignore`) |

Las **referencias bibliográficas sí se publican** — el usuario lo autorizó
rectificando una instrucción previa. La regla es no subir los archivos, no
callar las fuentes. Lo que no se publica es cualquier enlace de descarga.

Antes de cualquier push, comprobar los ignorados:
`git status --porcelain --ignored`.

**Hacen falta DOS archivos de exclusión, y no son intercambiables.** El CLI de
Vercel **no lee `.gitignore`**: construye su lista sólo desde `.vercelignore`
(o `.nowignore`) más unos pocos valores por defecto. Mientras `.vercelignore`
no existió, `vercel deploy` subió el directorio entero —los dos Excel
inéditos, los 47 PDF y todo `data/private/`— a los servidores de Vercel. No
llegaron a servirse en ninguna URL (nada de eso está en `public/` y por
entonces el middleware devolvía 401), pero habían salido del equipo. Borrar
`.vercelignore` reabre la fuga en el siguiente despliegue.

**Al abrir el sitio, este archivo pasó a importar más, no menos.** Ya no hay
un 401 detrás por si algo se cuela: `.vercelignore` es lo único que separa los
originales del equipo de los servidores de Vercel.

La auditoría verifica además que ningún dataset público ni el informe
contengan rutas del sistema de archivos (`Data_nosubiralrepo/`, `C:\Users`,
`OneDrive`, `file://`).

---

## Comandos

### Frontend

```bash
npm run dev              # servidor de desarrollo
npm run build            # build de producción (prerenderiza todo)
npm run verificar        # tsc --noEmit — ESTE es el gate
```

No hay ESLint en el repo. El script `lint` prometía una verificación que no
existía y se retiró: **la comprobación real es `npm run verificar`**
(`tsc --noEmit`), y ha atrapado errores que la auditoría no vio — por ejemplo
una colisión de claves en un spread de objeto que silenciaba una banda
latitudinal.

### Pipeline

```bash
npm run datos            # 00 -> 10 -> 20 -> 99 (el subconjunto sin red ni PDF)
npm run auditoria        # sólo la auditoría
python pipeline/05_worms.py      # un script suelto, siempre desde la raíz
```

Orden completo, cuando se regenera todo desde cero:

```bash
python pipeline/00_extract.py         # Excel        -> data/private/*_raw.json
python pipeline/05_worms.py           # WoRMS (red, cacheado)
python pipeline/06_estudios.py        # CrossRef (red)
python pipeline/10_clean.py           # aplica correcciones -> *_clean.json
python pipeline/07_pdfs.py            # empareja PDF y extrae evidencia
python pipeline/08_organizar.py       # renombra PDF, separa los excluidos
python pipeline/09_verificar_pdfs.py  # nombre vs contenido + duplicados
python pipeline/20_build.py           # -> data/derived/*.json (PÚBLICO)
python pipeline/40_taxones_pdf.py     # lee los artículos completos
python pipeline/45_tablas_pdf.py      # TABLAS: δ13C, abundancias, índices
python pipeline/50_estadisticas.py    # -> taxones_completo.json
python pipeline/30_informe.py         # -> Informe_curacion_datos.pdf
python pipeline/60_excel.py           # -> los Excel corregidos (carpeta privada)
python pipeline/99_auditoria.py       # sale con código 1 si algo falla
```

**Ejecutar `99_auditoria.py` después de cualquier cambio en el pipeline.** No
confía en las salidas intermedias: vuelve a leer los Excel originales y
verifica de forma independiente la conservación de registros, la aritmética
recalculada desde cero, la coherencia entre datasets y la ausencia de fugas.

Dependencias: `openpyxl`, `pypdf`, `fpdf2`, `pdfplumber`. **Ningún script
usa pandas.** `pdfplumber` es sólo para `45_tablas_pdf.py`: `pypdf` devuelve
el texto en orden de lectura y una tabla se vuelve una ristra de números sin
columnas; `pdfplumber` da la POSICIÓN de cada palabra, y agrupando por
coordenada vertical se recupera la fila, que es lo que asocia un taxón con
sus cifras.
Los scripts leen los originales desde `THESIS_DATA_DIR` (por defecto
`./Data_nosubiralrepo`). El caché de WoRMS vive en
`data/private/worms_cache.json`; borrarlo fuerza la reconsulta.

### Despliegue

Vercel, proyecto `foraminiferos-bentonicos-filtraciones-metano`, **desplegado
desde GitHub**: cada push a `master` publica solo, sin `vercel deploy` a mano.
El repositorio, el proyecto de Vercel y el dominio llevan el mismo nombre a
propósito.

Lo que mantiene el sitio abierto **no es el código, es un ajuste de Vercel**:
`ssoProtection` desactivado. Estuvo en `all_except_custom_domains` de la etapa
con contraseña, y ahí cualquier dominio nuevo devuelve 302 a `vercel.com/sso-api`
—el sitio parece roto estando bien—. Se mira con
`vercel project protection <proyecto>`. **El sitio es público y
estático**: `output: "export"` en `next.config.ts`, sin servidor, sin variables
de entorno y sin nada que decidir en runtime. `npm run build` deja el sitio
entero en `out/`.

Hasta 2026-08-18 iba cerrado con sesión de cookie firmada. Se abrió a petición
del autor: la tesis se entregó en 2023 y el dashboard pasa a ser parte de su
portafolio. **Lo que se abrió es el dashboard, no los datos primarios** — la
regla de confidencialidad de arriba no se toca, porque lo único que el sitio
publica son los agregados de `data/derived/`, que ya estaban pensados para
verse. Por lo mismo `layout.tsx` pasó a `robots: { index: true, follow: true }`:
antes se pedía no indexar, ahora se busca lo contrario.

**Si algún día vuelve a cerrarse**, son dos cambios y hacen falta los dos:
quitar `output: "export"` **y** devolver `src/middleware.ts`. Sólo uno de ellos
deja el sitio abierto creyéndolo cerrado. El código de la sesión —firma HMAC en
Web Crypto, almacén Blob con PBKDF2 y pregunta de seguridad— está en el commit
anterior a su retirada, no hay que reescribirlo.

---

## Arquitectura

### Flujo de datos

```
Data_nosubiralrepo/*.xlsx  ──00──▶  data/private/*_raw.json
                                          │
        WoRMS ─05─┐                       │
      CrossRef ─06─┼──▶ data/private/  ──10──▶  *_clean.json
          PDF ─07─┘    (nunca se sube)          │
                                                ▼
                                    20/45/50 ──▶ data/derived/*.json
                                                    │  (público, 555 KB)
                                                    ▼
                               import x from "@datos/nombre.json"
                                                    │
                                        build estático de Next.js
```

`@datos/*` está mapeado en `tsconfig.json` a `data/derived/*`; `@/*` a `src/*`.
Un componente que necesite un dato nuevo exige que `20_build.py` lo emita
primero: no hay fetch en runtime.

Los once datasets públicos y quién los consume:

| Dataset | Lo consume |
|---|---|
| `estudios.json` | `MapaMundial`, `Referencias`, `Pagina` |
| `matriz_lat_prof.json` | `MatrizLatProf`, `MapaMundial`, `Pagina` |
| `pared_por_banda.json` | `ParedPorBanda` |
| `msh_bc21.json` | `Composicion`, `Testigo`, `Veredicto`, `ParedPorBanda`, `Caribe`, `Pagina` |
| `sinu_2024.json` | `Sinu`, `Veredicto` |
| `solape.json` | `Composicion`, `Veredicto` |
| `taxones_completo.json` | `Explorador`, `Pagina` |
| `taxones_global.json` | *(insumo de `50_estadisticas.py`)* |
| `caribe_referencia.json` | `Caribe` |
| `correcciones.json` | `Pagina` |
| `cuantitativos.json` | **nadie en el frontend — y está bien** |

**`cuantitativos.json` no es salida muerta.** Es público porque son agregados
sin texto literal, pero su consumidor es `60_excel.py`: de ahí salen las
columnas de δ13C, abundancias e índices de los Excel corregidos, que van a la
carpeta privada. Borrarlo por «no lo importa ningún componente» rompe los Excel
del autor sin que el `tsc` ni el build se enteren.

### El pipeline

Numeración por etapas. Los archivos **sin número son módulos de referencia
curados a mano, y son la fuente de verdad** — no se generan, se editan:

| Módulo | Contenido |
|---|---|
| `taxonomy.py` | Tablas género→pared, planctónicos, normalización de texto de PDF |
| `corrections.py` | Registro auditable de TODAS las desviaciones respecto del original |
| `localidades.py` | Georreferenciación por DOI, tipo de fluido, nivel de confianza |
| `tipologia.py` | Los dos ejes de clasificación de filtraciones |
| `caribe_referencia.py` | Fauna caribeña estructurada desde la prosa del cap. 4.2 de la tesis |
| `estudios_nuevos.py` | Estudios incorporados después de la tesis |
| `candidatos.py` | Lista de trabajo: estudios por integrar. No alimenta el dashboard |

**`corrections.py` es la pieza central del proyecto.** Toda diferencia entre
los Excel del autor y los datos publicados pasa por ahí, con su motivo y su
fuente, y el registro se publica en `correcciones.json`. Los tipos distinguen
cosas que no son equivalentes: `errata` (error del manuscrito) frente a
`actualizacion` (WoRMS reclasificó después de nov-2022 — **no** es un error
del autor), más `exclusion`, `reclasificacion_pared`, `aritmetica`,
`duplicado`, `recuperacion` y `sin_verificar`. Nunca corregir un dato saltando
este registro.

`tipologia.py` clasifica cada filtración en **dos ejes ortogonales**: la
naturaleza del fluido (frío / termogénico / biogénico / hidrotermal) y la
expresión geomorfológica (pockmark, volcán de lodo, montículo de hidratos…).
Mezclarlos en un solo campo confunde dos cosas distintas. Donde habría que
adivinar se deja en `None` y el dashboard lo muestra como pendiente.

### El frontend

`src/app/page.tsx` renderiza un único componente, `src/components/Pagina.tsx`,
que es la narrativa completa: **ocho** secciones en scroll. Cada una envuelve
un componente de visualización en `<Seccion>`.

| # | Componente | Historia |
|---|---|---|
| 01 | `MatrizLatProf` + `MapaMundial` | El punto ciego: la celda 0-15° / <150 m está vacía |
| 02 | `ParedPorBanda` | La firma de la pared (calcáreo/aglutinado por banda) |
| 03 | `Composicion` + `Testigo` | Fauna de seep o de plataforma tropical |
| 04 | `Veredicto` | ¿Qué tan *seep* se ve MSH-BC-21? |
| 05 | `Sinu` | Barragán y Bernal (2024): mismo campo, con isótopos |
| 06 | `Explorador` | Buscar, filtrar y ordenar los taxones |
| 07 | `Caribe` | El contraste con la fauna de fondo regional |
| 08 | *(inline)* + `Referencias` | Los límites declarados, y las referencias dentro de ellos |

`Referencias` **no es una sección**: vive dentro de «08 · Límites», bajo
«Trazabilidad». Poner las fuentes dentro de los límites es deliberado — es
donde se sostiene lo que el trabajo puede y no puede afirmar.

`src/lib/i18n.tsx` — contexto con `idioma`, persistido en `localStorage`. `useT()` devuelve `t(clave)` para las cadenas
de interfaz repetidas y `tx({es, en})` para el contenido largo, que vive
inline en cada componente. **Todo texto visible pasa por uno de los dos.**

`src/lib/ui.tsx` — primitivas compartidas: `<Taxon>`, `<Cifra>`, `<Seccion>`,
`<ComoSeLee>` (bloque plegable con el método) y `<Nota>`.

---

## Invariantes que se rompen con facilidad

Cada una viene de un fallo real ya ocurrido. El comentario en el código
explica el caso concreto; esto es el índice.

- **Lo que protege los datos es `.vercelignore` y la curación, NO una
  contraseña.** La hubo, y se retiró al abrir el sitio; quien lea código
  antiguo puede creer que sigue habiendo una barrera. No la hay: **todo lo que
  entre en `data/derived/` es público desde el momento en que se despliega.**
  Si un dataset nuevo llevara texto literal de un artículo o una ruta del
  sistema de archivos, ya no hay un 401 detrás que lo tape — por eso esas dos
  comprobaciones de `99_auditoria.py` pasaron de red de seguridad a única
  defensa, y ninguna se puede relajar.
- **`05_worms.py::pick_foram` filtra por `phylum == "Foraminifera"`.** Varios
  géneros son homónimos entre grupos: `Cassidulina` devuelve un equinoideo. No
  quitar el filtro.
- **La firma que identifica un PDF se busca SÓLO en la primera página.**
  Buscarla en tres capturó una cita de la bibliografía y archivó un resumen de
  Panieri (2000) con el nombre de Sen Gupta y Aharon (1994). Ejecutar siempre
  `09_verificar_pdfs.py` después de `08_organizar.py`.
- **`taxonomy.normalizar_pdf()` antes de buscar nombres en texto de PDF.** Las
  ligaduras salen con espacios espurios (`wuellerstor ﬁ`); sin esto,
  *Cibicidoides wuellerstorfi* se pierde entero.
- **Los colores de serie de `globals.css` pasaron un validador de contraste**
  sobre las superficies reales del proyecto, en ambos modos y con visión
  cromática deficiente. La paleta desaturada que se probó primero falló. No
  sustituir esos valores a ojo. El color codifica variables; si no codifica
  nada, es gris.
- **Ningún componente fija un color en hex.** Un hex no cambia con el tema;
  el fondo sobre el que se pinta, sí. `MatrizLatProf` llevaba la tinta de la
  cifra en hex fijo sobre un fondo `var(--seq-*)`, y en modo oscuro el paso
  100 quedaba a **contraste 1,00** —tinta y fondo idénticos, la cifra
  invisible— y el 250 a 1,47. Las tintas viven ahora en `globals.css` como
  `--seq-*-tinta`, con su ratio anotado y los tres bloques de tema. Hay una
  comprobación en `99_auditoria.py` que falla si vuelve a aparecer un hex en
  `src/components/`. Cuidado también con `opacity-*` sobre esas tintas: el
  subtítulo iba a `opacity-80` y eso solo bajaba el peor caso a 3,88.
- **El DOI del manifiesto de PDF es el canónico del estudio, no el leído del
  PDF.** El del PDF llega truncado cuando parte un salto de línea (Fontanier
  2014 se leía sin el último dígito), y entonces cualquier cruce por ese campo
  pierde el estudio en silencio — pasó. El leído se conserva aparte, en
  `doi_leido_del_pdf`. El emparejado por prefijo sigue siendo deliberado, pero
  exige `MIN_PREFIJO = 12`: por debajo, un prefijo corto emparejaba con el
  primer estudio que empezara igual.
- **«Sin datos» debe leerse VACÍO, nunca como cero** — de ahí
  `--sin-datos-trama` y la clase `.trama-sin-datos`, que sobrevive a
  `forced-colors` y a la impresión, donde el relleno de color se pierde.
- **Los rankings van por número de ESTUDIOS, no de registros.** El recuento de
  registros premia a los artículos que desglosan más bandas.
- **Dos vistas de la base, y no son intercambiables:** `curada` (la que
  sustenta la tesis) y `ampliada` (con los estudios reincorporados). Los
  datasets traen ambas (`celdas` / `celdas_ampliada`, `n_curada` /
  `n_ampliada`). El dashboard ofrece la curada por defecto.
- **Presencia, menciones y dominancia no valen lo mismo** en la extracción de
  los artículos: la presencia es señal sólida, el número de menciones es un
  proxy débil (un artículo repite un nombre al citar a otros) y sólo hay
  dominancia cuando el texto la afirma. El dashboard debe distinguirlas.
- **Los nombres científicos van siempre en cursiva**, vía `<Taxon>`, que
  respeta la nomenclatura abierta: el calificador `sp.` / `spp.` va en redonda.
- **En el mapa, ningún punto se desplaza de su coordenada real.** Separarlos
  en abanico para que no se solapen dibujó E23 fuera del marco, al norte de
  Noruega: un dato falso en un mapa que existe para decir dónde se ha
  estudiado. La solución es zoom (`K_MIN`–`K_MAX`) más agrupación **en espacio
  de pantalla** (`JUNTOS = 24` px): al acercar, la distancia en pantalla crece
  y los grupos se abren solos sin mover nada. Tres estudios en coordenadas
  idénticas no se separan con ningún zoom —Hydrate Ridge y Vestnesa tienen
  tres cada uno—, y por eso al pulsar un grupo se despliega su lista bajo el
  mapa. El `<clipPath id="marco-mapa">` es el cinturón de seguridad; los
  puntos se dibujan **fuera** del `<g>` escalado para que su radio no crezca.
- **Una morfología o una localidad exigen evidencia EN EL CUERPO del
  artículo.** E24 figuraba como «pingos de hidratos» con
  `fuente="título y resumen"`, que era una inferencia disfrazada de prueba: el
  artículo dice «pingo» cero veces y «pockmark» treinta, y el punto estaba a
  330 km de su sitio. Al revisar aparecieron tres casos más. `99_auditoria.py`
  comprueba ahora que cada morfología asignada se lea en el texto del artículo
  **recortando la bibliografía** —ahí los títulos citados nombran morfologías
  de otros trabajos— y que las justificadas sólo por la localidad
  (`JUSTIFICADA_POR_LOCALIDAD`) sigan siendo pocas y explícitas.

---

## Convenciones

- Comentarios en español, y explican **por qué**, no qué. Varios documentan un
  fallo concreto para que nadie lo repita: no borrarlos al refactorizar.
- Mensajes de commit en español, en imperativo y sin tildes en el asunto.
- En la interfaz, las cifras van con coma decimal (`3,4325`) y
  `font-variant-numeric: tabular-nums` cuando se comparan en columna.
- Toda visualización lleva su `<ComoSeLee>` y su `<Nota>` con la fuente: el
  público es académico y el método tiene que estar a la vista.

---

## README.md

La cara pública del repositorio: qué es, qué contiene cada sección, las cifras,
el método y los límites declarados. Es el documento que verá quien llegue por
GitHub, así que **una cifra que cambie en `data/derived/` lo desactualiza**.
Reparte el trabajo con este archivo sin repetirlo: el README explica el
proyecto a quien no lo conoce, CLAUDE.md dice qué se rompe con facilidad.

El repositorio está limpio para publicarse, pero **no tiene remoto**: el primer
`git remote add origin` y el primer push los hace el autor.

---

## CHECKPOINT.md

Documento de continuidad entre sesiones: estado del pipeline, cifras
verificadas, hallazgos que corrigen el manuscrito y decisiones del usuario.
**Leerlo antes de retomar el trabajo.**

Sus §4 y §5 (los datos y las cifras clave) han quedado obsoletos tres veces:
si cambia el pipeline, **regenerarlos desde `data/derived/`**, no editarlos a
mano, y con `99_auditoria.py` en verde. La §10 conserva la dirección visual
acordada, pero sus valores de color son la propuesta inicial, anterior al
validador: los vigentes son los de `globals.css`.

---

## Dónde va cada dato extraído

Decidido **midiendo el solape**, no por comodidad:

- **δ13C → la base principal** (`Base corregida` del Excel). Mismo grano y el
  **73 %** cae sobre registros que ya existen: son columnas, no filas.
- **Abundancias → la vista ampliada** (`Asociaciones por estudio`). Sólo
  solapan un **17 %**: la base recoge «las 5 principales especies» por filtro
  y las tablas listan la asociación entera.
- **`caribe_referencia` → sección de contraste, NUNCA fusionado con la base.**
  Las cinco localidades caen en la banda 0-15° y son someras: fusionarlas
  llenaría de fauna de manglar y arrecife **justamente la celda vacía que
  sostiene el argumento central**, y lo volvería falso. Es el mismo error que
  ya se corrigió con McCorkle (1990). Si alguien propone «unificar las bases»,
  esto es lo que hay que responderle.

---

## Dos cosas que se probaron y se quitaron

**Ordenación multivariante (PCoA + PERMANOVA), retirada el 2026-08-18.** El
autor la juzgó sin aporte para el dashboard. El código está en el commit
`2efd964` por si algún día se retoma, y el motivo de fondo conviene recordarlo
antes de reintentarlo: **con los 37 estudios el primer eje reproducía la
riqueza a rho = −0,95**, es decir, medía cuántos taxones nombra cada artículo y
no su ecología. La rarefacción no lo arregla (submuestrear 12 taxones de un
artículo que nombra 318 lo vuelve un sorteo que se aleja de todos). Sólo en la
franja 18-70 taxones —doce estudios— la riqueza dejaba de gobernar el eje. Con
ese n, latitud daba p=0,009 y todo lo demás no separaba nada. **δ13C,
abundancias e índices no pueden entrar en un análisis conjunto**: cubren el
12-15 % de los estudios y el resto habría que imputarlo, que es inventar la
estructura.

**Modo narrativa ↔ exploración, retirado el 2026-08-18.** Prometía dos lecturas
del dashboard y en once componentes sólo cambiaba una cosa: que apareciera el
`n=` en dos barras de `ParedPorBanda`. Ahora ese `n` se muestra siempre, que es
lo coherente con un público académico.
