# Quotes Scraper API

API REST que extrae citas de [quotes.toscrape.com](https://quotes.toscrape.com) usando Selenium, las almacena en una base de datos PostgreSQL y las expone a través de endpoints con filtros combinables.

---

## Tabla de contenido

1. [Requisitos previos](#requisitos-previos)
2. [Instalacion](#instalacion)
3. [Configuracion](#configuracion)
4. [Base de datos](#base-de-datos)
5. [Correr el proyecto](#correr-el-proyecto)
6. [Probar la API](#probar-la-api)
7. [Verificar la base de datos](#verificar-la-base-de-datos)
8. [Estructura del proyecto](#estructura-del-proyecto)

---

## Requisitos previos

Para correr este proyecto solo necesitas:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows / Mac)
- O Docker + Docker Compose (Linux)

No es necesario instalar Python, Chrome ni PostgreSQL en tu maquina. Todo corre dentro de contenedores Docker.

---

## Instalacion

```bash
# Clonar el repositorio
git clone <https://github.com/MAZP73/prueba_Quotes.git>
cd PRUEBA_TECNICA
```

O descarga y descomprime el archivo ZIP, luego abre una terminal dentro de la carpeta extraida.

---

## Configuracion

El proyecto usa un archivo `.env` para las variables de entorno. Se incluye un `.env` por defecto que funciona directamente con Docker sin modificaciones.

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
POSTGRES_DB=quotes_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

> Nota: `POSTGRES_HOST=db` hace referencia al nombre del contenedor PostgreSQL dentro de la red Docker. Si corres el proyecto localmente sin Docker, cambia este valor a `localhost`.

---

## Base de datos

### Con Docker (automatico)

La base de datos y todas las tablas se crean automaticamente al iniciar los contenedores. No se requiere ningun paso manual.


### Modelo de datos

```
authors (1) ---- quotes (N) ---- quote_tags ---- tags (N)
```

- Un autor tiene muchas citas.
- Una cita puede tener muchas etiquetas (relacion N:N).
- Los duplicados se evitan mediante una restriccion de unicidad sobre el texto de la cita.

---

## Correr el proyecto

### Iniciar todos los servicios

```bash
docker compose up --build -d
```

Este unico comando construye la imagen de la API, inicia el contenedor de PostgreSQL, inicia el contenedor de FastAPI y crea todas las tablas de la base de datos automaticamente.

Espera entre 15 y 30 segundos a que todo este listo, luego ejecuta el scraper para poblar la base de datos.

### Ejecutar el scraper (obligatorio en el primer inicio)

La base de datos inicia vacia. Debes correr el scraper una vez para poblarla. Elige una de las tres opciones a continuacion.

---

### Opcion 1 — Swagger UI

Abre tu navegador y ve a:

```
http://localhost:8000/docs
```

1. Haz clic en `POST /quotes/scrape`
2. Haz clic en `Try it out`
3. Haz clic en `Execute`

Espera 1-2 minutos mientras Selenium navega las 10 paginas del sitio.

---

### Opcion 2 — API desde la terminal

Windows (PowerShell):
```powershell
curl -UseBasicParsing -Method POST http://localhost:8000/quotes/scrape
```

Linux / Mac:
```bash
curl -X POST http://localhost:8000/quotes/scrape
```

Respuesta esperada:
```json
{
  "message": "Scraping completado exitosamente.",
  "total_scraped": 100,
  "total_saved": 100
}
```

---

### Opcion 3 — Script dentro del contenedor

```bash
docker exec -it quotes_api python scripts/run_scraper.py
```

Ejecuta el scraper directamente sin pasar por la API. Util para depuracion o para correr sin el servidor web activo.

---

## Probar la API

### Documentacion interactiva

Con la API corriendo, abre en el navegador:

```
http://localhost:8000/docs       Swagger UI — ejecutar peticiones desde el navegador
```

---

### Endpoints desde la terminal

**1. Health check**

Windows:
```powershell
curl -UseBasicParsing http://localhost:8000/
```
Linux/Mac:
```bash
curl http://localhost:8000/
```

**2. Todas las citas**

Windows:
```powershell
curl -UseBasicParsing http://localhost:8000/quotes/
```
Linux/Mac:
```bash
curl http://localhost:8000/quotes/
```

**3. Filtrar por autor**

Windows:
```powershell
curl -UseBasicParsing "http://localhost:8000/quotes/?author=Einstein"
```
Linux/Mac:
```bash
curl "http://localhost:8000/quotes/?author=Einstein"
```

**4. Filtrar por etiqueta**

Windows:
```powershell
curl -UseBasicParsing "http://localhost:8000/quotes/?tag=life"
```
Linux/Mac:
```bash
curl "http://localhost:8000/quotes/?tag=life"
```

**5. Busqueda libre**

Windows:
```powershell
curl -UseBasicParsing "http://localhost:8000/quotes/?search=love"
```
Linux/Mac:
```bash
curl "http://localhost:8000/quotes/?search=love"
```

**6. Filtros combinados**

Windows:
```powershell
curl -UseBasicParsing "http://localhost:8000/quotes/?author=Einstein&tag=life"
```
Linux/Mac:
```bash
curl "http://localhost:8000/quotes/?author=Einstein&tag=life"
```

**7. Ejecutar scraper nuevamente — prueba de duplicados**

Windows:
```powershell
curl -UseBasicParsing -Method POST http://localhost:8000/quotes/scrape
```
Linux/Mac:
```bash
curl -X POST http://localhost:8000/quotes/scrape
```

Respuesta esperada cuando los datos ya existen:
```json
{
  "message": "Scraping completado exitosamente.",
  "total_scraped": 100,
  "total_saved": 0
}
```

`total_saved: 0` confirma que la prevencion de duplicados funciona correctamente.

---

## Verificar la base de datos

### Contar registros por tabla

```bash
docker exec -it quotes_postgres psql -U admin -d quotes_db -c "SELECT COUNT(*) FROM quotes;"

docker exec -it quotes_postgres psql -U admin -d quotes_db -c "SELECT COUNT(*) FROM authors;"

docker exec -it quotes_postgres psql -U admin -d quotes_db -c "SELECT COUNT(*) FROM tags;"

docker exec -it quotes_postgres psql -U admin -d quotes_db -c "SELECT COUNT(*) FROM quote_tags;"
```

### Ingresar a la consola interactiva de PostgreSQL

```bash
docker exec -it quotes_postgres psql -U admin -d quotes_db
```

Una vez dentro puedes ejecutar consultas SQL directamente:

```sql
-- Listar todas las tablas
\dt

-- Ver las primeras 5 citas con su autor
SELECT q.id, q.text, a.name
FROM quotes q
JOIN authors a ON q.author_id = a.id
LIMIT 5;

-- Contar citas por autor
SELECT a.name, COUNT(q.id) AS total
FROM authors a
JOIN quotes q ON a.id = q.author_id
GROUP BY a.name
ORDER BY total DESC;

-- Contar citas por etiqueta
SELECT t.name, COUNT(qt.quote_id) AS total
FROM tags t
JOIN quote_tags qt ON t.id = qt.tag_id
GROUP BY t.name
ORDER BY total DESC;

-- Ver citas con sus etiquetas
SELECT q.text, t.name AS etiqueta
FROM quotes q
JOIN quote_tags qt ON q.id = qt.quote_id
JOIN tags t ON t.id = qt.tag_id
LIMIT 10;

-- Salir de la consola
\q
```

---

## Comandos Docker utiles

```bash
# Iniciar todos los servicios
docker compose up --build -d

# Ver logs de la API en tiempo real
docker logs -f quotes_api

# Ver contenedores en ejecucion
docker ps

# Detener servicios (los datos se conservan)
docker compose down

# Detener servicios y eliminar todos los datos
docker compose down -v

# Reinicio completo desde cero
docker compose down -v && docker compose up --build -d
```

---

## Estructura del proyecto

```
quotes_scraper_api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── config.py                # Configuracion global
│   ├── logger.py                # Logger centralizado
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes_quotes.py     # Endpoints
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py          # Conexion a la base de datos
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   └── schemas.py           # Schemas Pydantic
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraper_service.py   # Logica de scraping con Selenium
│   │   └── quote_service.py     # Logica de negocio
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── quote_repository.py  # Capa de acceso a datos
│   │
│   └── utils/
│       ├── __init__.py
│       └── driver.py            # Configuracion del WebDriver Selenium
│
├── scripts/
│   └── run_scraper.py           # Script standalone del scraper
│
├── database.sql                 # Schema inicial de la base de datos
├── docker-compose.yml           # Orquestacion de servicios
├── Dockerfile                   # Imagen de la API
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno
├── .gitignore
└── README.md
```