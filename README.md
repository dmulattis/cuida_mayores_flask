<div align="center">

# CUIDA A TUS MAYORES  
## Sistema web para la gestión de perfiles de cuidadores

**Asignatura:** Taller de Desarrollo Web y Móvil — APTC106  
**Evaluación:** Semana 6 — Sumativa 2  
**Integrantes:** Diego Mulatti Morales · Alejandro Ortega Aranda · Omar Sanhueza Becar  
**Repositorio:** https://github.com/dmulattis/cuida_mayores_flask

</div>

---

# CONSIDERACIONES PARA LA EJECUCIÓN

Este proyecto corresponde a un prototipo web desarrollado con **Flask**, cuyo propósito es administrar perfiles de cuidadores de personas mayores mediante operaciones CRUD.

La aplicación permite:

- Registrar nuevos cuidadores.
- Consultar el listado de perfiles.
- Buscar y filtrar registros.
- Visualizar el detalle de un cuidador.
- Editar información existente.
- Eliminar perfiles mediante confirmación.
- Validar datos ingresados en los formularios.
- Mantener la información en una base de datos local SQLite.
- Ejecutar pruebas automatizadas del ciclo CRUD.

> El prototipo se ejecuta en un entorno local y tiene fines académicos.  
> No incorpora todavía autenticación por roles, pagos, notificaciones ni aplicación móvil.

---

# 1. ENTORNO DE DESARROLLO

El proyecto fue desarrollado utilizando las siguientes tecnologías:

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11 o superior |
| Framework web | Flask |
| Acceso a datos | Flask-SQLAlchemy |
| Base de datos | SQLite |
| Interfaz | HTML5, CSS3 y Jinja |
| Pruebas | pytest |
| Control de versiones | Git y GitHub |
| Entorno recomendado | Visual Studio Code |

Para comprobar que Python y Git están instalados:

```powershell
py --version
git --version
```

---

# 2. ESTRUCTURA DEL PROYECTO

```text
cuida_mayores_flask/
│
├── app/
│   ├── cuidadores/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── static/
│   │   └── css/
│   │       └── estilos.css
│   │
│   ├── templates/
│   │   ├── cuidadores/
│   │   │   ├── confirmar_eliminar.html
│   │   │   ├── detalle.html
│   │   │   ├── formulario.html
│   │   │   └── lista.html
│   │   │
│   │   ├── 404.html
│   │   ├── base.html
│   │   └── inicio.html
│   │
│   ├── __init__.py
│   ├── extensions.py
│   └── models.py
│
├── instance/
│   └── cuida_mayores.db
│
├── tests/
│   ├── conftest.py
│   └── test_crud.py
│
├── .gitignore
├── README.md
├── requirements.txt
├── run.py
└── seed.py
```

## Archivos principales

| Archivo | Descripción |
|---|---|
| `app/__init__.py` | Crea y configura la aplicación mediante Application Factory. |
| `app/models.py` | Define la entidad `Cuidador`. |
| `app/extensions.py` | Inicializa SQLAlchemy. |
| `app/cuidadores/routes.py` | Contiene las rutas y operaciones CRUD. |
| `app/templates/` | Contiene las vistas HTML generadas con Jinja. |
| `app/static/css/estilos.css` | Define el diseño visual y responsivo. |
| `seed.py` | Crea la base local con perfiles de ejemplo. |
| `run.py` | Inicia el servidor Flask. |
| `tests/test_crud.py` | Verifica el ciclo completo del CRUD. |

---

# 3. ARQUITECTURA Y PATRONES UTILIZADOS

La aplicación utiliza una arquitectura web organizada por responsabilidades:

```text
Usuario
   ↓
HTML + CSS + Jinja
   ↓
Rutas Flask
   ↓
Modelo SQLAlchemy
   ↓
Base de datos SQLite
```

## Patrones implementados

### Application Factory

La función `create_app()` centraliza la creación y configuración de Flask.  
Esto permite utilizar configuraciones distintas para ejecución normal y pruebas.

### Blueprint

El módulo `cuidadores` agrupa todas las rutas relacionadas con el CRUD bajo el prefijo:

```text
/cuidadores
```

### MVC adaptado

| Componente | Ubicación |
|---|---|
| Modelo | `app/models.py` |
| Vista | `app/templates/` |
| Controlador | `app/cuidadores/routes.py` |

### Herencia de plantillas

La plantilla `base.html` contiene la estructura común del sitio.  
Las demás vistas reutilizan esta base mediante bloques de Jinja.

---

# 4. INSTALACIÓN EN WINDOWS

## 4.1 Abrir el proyecto

Desde Visual Studio Code:

```text
Archivo → Abrir carpeta
```

Seleccionar la carpeta que contiene:

```text
run.py
seed.py
requirements.txt
app/
```

## 4.2 Crear el entorno virtual

```powershell
py -m venv .venv
```

## 4.3 Instalar las dependencias

En equipos donde PowerShell bloquea la activación de scripts, se puede utilizar directamente el ejecutable de Python del entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

## 4.4 Crear la base de datos

```powershell
.\.venv\Scripts\python.exe .\seed.py
```

Este comando:

1. Elimina las tablas anteriores.
2. Crea nuevamente la estructura de la base.
3. Inserta cuidadores de ejemplo.

## 4.5 Ejecutar la aplicación

```powershell
.\.venv\Scripts\python.exe .\run.py
```

Abrir en el navegador:

```text
http://127.0.0.1:5000
```

Para detener el servidor:

```text
Ctrl + C
```

---

# 5. FUNCIONAMIENTO DEL SISTEMA

## 5.1 Página de inicio

La página principal muestra indicadores básicos:

- Total de cuidadores.
- Perfiles aprobados.
- Perfiles pendientes.
- Cuidadores disponibles.

## 5.2 Listado de cuidadores

La vista de listado permite:

- Buscar por nombre, correo o descripción.
- Filtrar por comuna.
- Filtrar por especialidad.
- Filtrar por estado de validación.
- Acceder al detalle de cada cuidador.
- Editar o eliminar registros.

## 5.3 Registro de cuidadores

El formulario solicita:

- Nombre.
- Correo.
- Teléfono.
- Comuna.
- Especialidad.
- Años de experiencia.
- Tarifa diaria.
- Disponibilidad.
- Estado de validación.
- Descripción profesional.

## 5.4 Validaciones

El sistema comprueba:

- Campos obligatorios.
- Estructura básica del correo electrónico.
- Especialidad válida.
- Estado de validación permitido.
- Años de experiencia entre 0 y 60.
- Tarifa diaria mayor que cero.
- Correo electrónico no duplicado.

---

# 6. OPERACIONES CRUD

| Operación | Ruta | Descripción |
|---|---|---|
| Crear | `/cuidadores/nuevo` | Registra un nuevo cuidador. |
| Leer | `/cuidadores/` | Lista, busca y filtra perfiles. |
| Leer detalle | `/cuidadores/<id>` | Muestra toda la información del cuidador. |
| Actualizar | `/cuidadores/<id>/editar` | Modifica un registro existente. |
| Eliminar | `/cuidadores/<id>/eliminar` | Elimina el perfil luego de una confirmación. |

Las rutas utilizan solicitudes `GET` para mostrar vistas y `POST` para registrar, actualizar o eliminar información.

---

# 7. PRUEBA MANUAL DEL CRUD

Para comprobar el funcionamiento:

1. Ejecutar `seed.py`.
2. Iniciar la aplicación con `run.py`.
3. Ingresar a **Cuidadores**.
4. Registrar un nuevo perfil.
5. Revisar el detalle del registro.
6. Editar la comuna, especialidad o tarifa.
7. Aplicar filtros en el listado.
8. Eliminar el perfil.
9. Confirmar que el registro ya no aparece.

---

# 8. PRUEBAS AUTOMATIZADAS

Instalar pytest:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
```

Ejecutar las pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado esperado:

```text
1 passed
```

La prueba automatizada utiliza una base SQLite temporal y verifica:

- Creación de un cuidador.
- Consulta del registro.
- Actualización de información.
- Eliminación del perfil.
- Ausencia de datos residuales al finalizar.

---

# 9. CONTROL DE VERSIONES

Para revisar los cambios:

```powershell
git status
```

Para guardar una nueva versión:

```powershell
git add .
git commit -m "Describe brevemente el cambio realizado"
git push
```

Archivos que no deben subirse al repositorio:

```gitignore
.venv/
__pycache__/
*.pyc
instance/*.db
.env
.vscode/
```

---

Con esto se garantiza un historial de cambios trazable y un repositorio limpio de archivos temporales o sensibles.

---

# 10. AUTORES

- **Diego Mulatti Morales**
- **Alejandro Ortega Aranda**
- **Omar Sanhueza Becar**

Proyecto desarrollado para la asignatura **Taller de Desarrollo Web y Móvil — APTC106**.
