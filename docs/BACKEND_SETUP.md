# Guía de configuración — Django + PostgreSQL

> **Proyecto:** Sazed ERP (TFG)
> **Fecha:** 2026-04-08
> **Requisitos previos:** Windows 10/11, Python 3.11+, acceso a terminal (PowerShell o CMD)

---

## 1. Instalar Python

### Verificar si ya lo tienes

```bash
python --version
```

Si sale `Python 3.11.x` o superior, estás listo. Si no:

### Instalar Python

1. Descargar desde https://www.python.org/downloads/
2. **IMPORTANTE:** En el instalador, marcar la casilla **"Add Python to PATH"**
3. Instalar con las opciones por defecto
4. Verificar: `python --version`

---

## 2. Instalar PostgreSQL

### Opción A: Instalador nativo (recomendado para TFG)

1. Descargar desde https://www.postgresql.org/downloads/windows/
2. Ejecutar el instalador (EDB installer)
3. Durante la instalación:
   - **Puerto:** dejarlo en `5432` (por defecto)
   - **Contraseña del superusuario (postgres):** elige una y **anótala** (la necesitarás luego)
   - **Locale:** dejar por defecto
   - **Stack Builder:** puedes saltártelo (desmarcar al final)
4. Una vez instalado, verificar que el servicio está corriendo:
   ```powershell
   Get-Service postgresql*
   ```
   Debería mostrar `Running`.

### Opción B: Docker (alternativa)

Si prefieres Docker:
```bash
docker run --name erp-postgres -e POSTGRES_PASSWORD=tu_contraseña -e POSTGRES_DB=erp_db -p 5432:5432 -d postgres:16
```

### Crear la base de datos

Abre **pgAdmin 4** (se instala con PostgreSQL) o usa la terminal:

```bash
# Abrir psql (PostgreSQL command line)
psql -U postgres

# Dentro de psql:
CREATE DATABASE erp_db;
CREATE USER erp_user WITH PASSWORD 'erp_password_2026';
GRANT ALL PRIVILEGES ON DATABASE erp_db TO erp_user;

# Necesario en PostgreSQL 15+:
\c erp_db
GRANT ALL ON SCHEMA public TO erp_user;

\q
```

> **Nota:** Puedes cambiar `erp_user` y `erp_password_2026` por lo que prefieras. Solo asegúrate de usar los mismos valores en el archivo `.env` del backend.

### Alternativa con pgAdmin 4 (interfaz gráfica)

1. Abrir pgAdmin 4
2. Conectarse al servidor local (contraseña del paso de instalación)
3. Click derecho en "Databases" → "Create" → "Database"
4. Nombre: `erp_db`
5. Owner: `postgres` (o crear un usuario nuevo desde "Login/Group Roles")

---

## 3. Configurar el entorno virtual de Python

Desde la raíz del proyecto (donde está `package.json`):

```powershell
# Crear el directorio del backend
mkdir backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1
```

> **Si da error de permisos en PowerShell:** ejecutar primero:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Verás `(venv)` al inicio del prompt, indicando que el entorno virtual está activo.

**IMPORTANTE:** Cada vez que abras una terminal nueva para trabajar con el backend, necesitas activar el entorno virtual:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

---

## 4. Instalar dependencias Python

Con el entorno virtual activo:

```bash
pip install django djangorestframework django-cors-headers django-filter psycopg[binary] python-decouple Pillow whitenoise dj-database-url
```

---

## 5. Archivo de variables de entorno

Crear el archivo `backend/.env` con esta configuración:

```env
# Django
SECRET_KEY=tu-clave-secreta-larga-y-aleatoria-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos PostgreSQL
DATABASE_URL=postgres://erp_user:erp_password_2026@localhost:5432/erp_db
```

> **Para generar una SECRET_KEY aleatoria:**
> ```python
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```
> (Ejecutar esto después de instalar Django)

> **IMPORTANTE:** El archivo `.env` contiene contraseñas. Añádelo a `.gitignore`:
> ```
> # En el .gitignore del proyecto raíz
> backend/.env
> backend/venv/
> ```

---

## 6. Cómo funciona la conexión Frontend ↔ Backend

```
┌──────────────┐         HTTP/JSON          ┌──────────────┐         SQL          ┌──────────────┐
│  Vue 3 SPA   │  ────────────────────────► │ Django REST  │ ─────────────────── │  PostgreSQL  │
│  (Vite)      │  ◄──────────────────────── │ Framework    │ ◄────────────────── │  (erp_db)    │
│  localhost:   │    fetch / axios           │  localhost:  │    psycopg          │  localhost:  │
│  5173        │                             │  8000        │                     │  5432        │
└──────────────┘                             └──────────────┘                     └──────────────┘
```

- El **frontend** (Vue 3) corre en `http://localhost:5173` (Vite dev server)
- El **backend** (Django) corre en `http://localhost:8000`
- La **base de datos** (PostgreSQL) escucha en `localhost:5432`
- El frontend hace peticiones HTTP (GET, POST, PUT, DELETE) al backend
- El backend consulta/escribe en PostgreSQL y devuelve JSON
- **CORS** (Cross-Origin Resource Sharing) permite que el frontend hable con el backend desde un puerto diferente

---

## 7. Comandos que usarás habitualmente

### Arrancar todo el proyecto (3 terminales)

**Terminal 1 — Frontend:**
```powershell
cd c:\Users\xelavi\Documents\TFG
npm run dev
```

**Terminal 2 — Backend:**
```powershell
cd c:\Users\xelavi\Documents\TFG\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

**Terminal 3 — PostgreSQL** (solo si necesitas consultas manuales):
```bash
psql -U erp_user -d erp_db
```

### Comandos Django comunes

| Comando | Descripción |
|---------|-------------|
| `python manage.py runserver` | Arrancar el servidor de desarrollo (puerto 8000) |
| `python manage.py makemigrations` | Detectar cambios en los modelos y crear archivos de migración |
| `python manage.py migrate` | Aplicar migraciones a la base de datos |
| `python manage.py createsuperuser` | Crear usuario admin para el panel de Django |
| `python manage.py shell` | Consola interactiva de Python con Django cargado |
| `python manage.py seed` | Cargar datos de ejemplo (lo crearemos nosotros) |
| `python manage.py test` | Ejecutar tests |

### Flujo cuando se cambian los modelos

Cada vez que modifiques un modelo (añadir un campo, cambiar un tipo, etc.):

```bash
python manage.py makemigrations     # 1. Genera el archivo de migración
python manage.py migrate            # 2. Aplica los cambios a PostgreSQL
```

---

## 8. Panel de administración de Django

Django incluye un panel de admin automático en `http://localhost:8000/admin/`.

Para acceder:
1. Crear superusuario: `python manage.py createsuperuser`
2. Introducir email, nombre de usuario y contraseña
3. Navegar a `http://localhost:8000/admin/` y hacer login

El panel te permite:
- Ver, crear, editar y eliminar registros de todas las tablas
- Es útil para verificar que los datos se están guardando correctamente
- Puedes añadir/editar datos directamente sin pasar por el frontend

---

## 9. Verificar que PostgreSQL funciona

### Test rápido de conexión desde Python

```python
# Con el venv activo, ejecutar:
python -c "
import psycopg
conn = psycopg.connect('dbname=erp_db user=erp_user password=erp_password_2026 host=localhost')
print('Conexión exitosa!')
conn.close()
"
```

### Ver tablas creadas

```sql
-- Desde psql:
\dt

-- O desde pgAdmin, navegar a: Servers > PostgreSQL > erp_db > Schemas > public > Tables
```

---

## 10. Herramientas recomendadas

| Herramienta | Para qué | URL |
|-------------|----------|-----|
| **pgAdmin 4** | Gestionar PostgreSQL visualmente | Se instala con PostgreSQL |
| **DBeaver** | Alternativa a pgAdmin (más moderna) | https://dbeaver.io/ |
| **Postman** o **Thunder Client** | Probar la API REST manualmente | Extensión de VS Code |
| **Django Debug Toolbar** | Ver queries SQL, tiempos, etc. | `pip install django-debug-toolbar` |

---

## 11. Estructura de archivos tras el setup

```
TFG/
├── frontend (Vue 3 - ya existente)
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── ...
│
├── backend/ (Django - nuevo)
│   ├── venv/              ← Entorno virtual (NO commitear)
│   ├── .env               ← Variables secretas (NO commitear)
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/            ← Configuración Django
│   ├── core/              ← App: TaxRate, Tag, Warehouse, etc.
│   ├── customers/         ← App: Customer, Note, Activity
│   ├── products/          ← App: Product, Variant, Stock
│   ├── invoices/          ← App: Invoice, Line, Payment
│   └── tasks/             ← App: Task (dashboard)
│
├── docs/                  ← Documentación
│   ├── BACKEND_DESIGN.md
│   ├── BACKEND_SETUP.md   ← Este archivo
│   └── ...
│
└── .gitignore             ← Añadir backend/venv/ y backend/.env
```

---

## 12. Actualizar .gitignore

Añadir al `.gitignore` del proyecto raíz:

```gitignore
# Backend
backend/venv/
backend/.env
backend/__pycache__/
backend/*/__pycache__/
backend/*/migrations/__pycache__/
backend/db.sqlite3
backend/media/
*.pyc
```

---

## 13. Solución de problemas comunes

### "python" no se reconoce como comando
- Reinstalar Python marcando "Add to PATH"
- O añadir manualmente: `C:\Users\TU_USUARIO\AppData\Local\Programs\Python\Python311\` al PATH del sistema

### Error al activar venv en PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### psycopg: Error de conexión a PostgreSQL
- Verificar que el servicio PostgreSQL está corriendo: `Get-Service postgresql*`
- Verificar puerto: `netstat -an | findstr 5432`
- Verificar usuario/contraseña en `.env`

### "FATAL: password authentication failed"
- Verificar que el usuario `erp_user` fue creado correctamente en PostgreSQL
- Verificar que la contraseña en `.env` coincide con la que usaste al crear el usuario

### Migrations: "relation already exists"
```bash
python manage.py migrate --fake    # Marca las migraciones como aplicadas sin ejecutarlas
```

### Puerto 8000 ya en uso
```bash
python manage.py runserver 8001    # Usar otro puerto
```

---

## 14. Resumen de pasos (checklist)

- [ ] Instalar Python 3.11+ (con Add to PATH)
- [ ] Instalar PostgreSQL 16 (anotar contraseña de postgres)
- [ ] Crear base de datos `erp_db` y usuario `erp_user`
- [ ] Crear directorio `backend/` y entorno virtual (`python -m venv venv`)
- [ ] Activar venv y instalar dependencias (`pip install ...`)
- [ ] Crear archivo `backend/.env` con SECRET_KEY y DATABASE_URL
- [ ] Actualizar `.gitignore`
- [ ] Cuando yo genere el código Django: ejecutar `makemigrations` + `migrate`
- [ ] Crear superusuario: `python manage.py createsuperuser`
- [ ] Ejecutar seed de datos: `python manage.py seed`
- [ ] Arrancar backend: `python manage.py runserver`
- [ ] Arrancar frontend: `npm run dev`
- [ ] Verificar que `http://localhost:8000/admin/` funciona
- [ ] Verificar que `http://localhost:8000/api/` devuelve JSON
