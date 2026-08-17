<div align="center">

# CUIDA A TUS MAYORES  
## Sistema web para la gestión de perfiles de cuidadores y propuesta de integración móvil

**Asignatura:** Taller de Desarrollo Web y Móvil — APTC106  
**Evaluación:** Semana 09 — Sumativa 3  
**Integrantes:** Diego Mulatti Morales · Alejandro Ortega Aranda · Omar Sanhueza Becar  
**Repositorio:** https://github.com/dmulattis/cuida_mayores_flask  

**URL despliegue Cloud:**  
[PEGAR AQUÍ LA URL PÚBLICA DEL DESPLIEGUE]

</div>

---

# CONSIDERACIONES GENERALES

Este proyecto corresponde a un prototipo web desarrollado con **Flask**, cuyo propósito es administrar perfiles de cuidadores de personas mayores mediante operaciones CRUD.

La propuesta nace a partir de la necesidad de conectar familias con cuidadores de confianza, facilitando la gestión de perfiles, la validación de información relevante y la proyección hacia una futura aplicación móvil orientada a familias y cuidadores.

La aplicación web permite:

- Registrar nuevos cuidadores.
- Consultar el listado de perfiles.
- Buscar y filtrar registros.
- Visualizar el detalle de un cuidador.
- Editar información existente.
- Desactivar perfiles mediante confirmación y borrado lógico.
- Validar datos ingresados en los formularios.
- Mantener la información en una base de datos local SQLite.
- Ejecutar pruebas automatizadas del ciclo CRUD.

Para la **Semana 09 — Sumativa 3**, el proyecto incorpora además:

- Integración de la propuesta de mejora desarrollada en la semana anterior.
- Preparación para el despliegue del aplicativo en Cloud.
- Diseño de mockups móviles para representar las primeras interacciones de navegación.
- Propuesta de integración entre el sistema web y una futura aplicación móvil.

> El prototipo web tiene fines académicos.  
> Actualmente permite validar el funcionamiento mínimo viable mediante CRUD, pruebas automatizadas y diseño de una propuesta móvil inicial.  
> Aún no incorpora autenticación real por roles, pagos funcionales, notificaciones reales ni conexión completa entre app móvil y backend.

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
| Despliegue Cloud | AWS / servicio Cloud equivalente |
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
│   │   │   ├── crear.html
│   │   │   ├── detalle.html
│   │   │   └── lista.html
│   │   │
│   │   ├── 404.html
│   │   ├── 500.html
│   │   ├── base.html
│   │   └── inicio.html
│   │
│   ├── __init__.py
│   ├── extensions.py
│   └── models.py
│
├── instance/
│   └── Archivos locales generados en ejecución, no versionados en Git
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
| `app/models.py` | Define cuidadores, comunas, especialidades y auditorías. |
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
py -m venv venv
```

## 4.3 Instalar las dependencias

En equipos donde PowerShell bloquea la activación de scripts, se puede utilizar directamente el ejecutable de Python del entorno virtual:

```powershell
.\venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

## 4.4 Crear la base de datos

```powershell
.\venv\Scripts\python.exe .\seed.py
```

Este comando:

1. Elimina las tablas anteriores.
2. Crea nuevamente la estructura de la base.
3. Inserta cuidadores de ejemplo.

## 4.5 Ejecutar la aplicación

```powershell
.\venv\Scripts\python.exe .\run.py
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

# 5. FUNCIONAMIENTO DEL SISTEMA WEB

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
- Longitud máxima de los campos de texto antes de persistirlos.
- Formato de correo electrónico mediante expresión regular.
- Formato de teléfono mediante expresión regular, entre 8 y 15 dígitos.
- Especialidad válida.
- Comuna válida.
- Estado de validación permitido.
- Años de experiencia entre 0 y 60.
- Tarifa diaria mayor que cero.
- Correo electrónico no duplicado.

Las validaciones se ejecutan en el backend, incluso si se omiten o alteran las restricciones HTML del formulario.

## 5.5 Manejo de errores

Las operaciones de creación, edición y eliminación usan transacciones controladas.  
Ante un fallo inesperado se revierte la transacción con `rollback`, se muestra un mensaje seguro al usuario y la traza técnica se registra en `instance/app.log`.

Un manejador global conserva las respuestas HTTP normales, como 404 y 405, y transforma solamente las excepciones inesperadas en una respuesta 500 sin exponer información técnica.

---

# 6. OPERACIONES CRUD

| Operación | Ruta | Descripción |
|---|---|---|
| Crear | `/cuidadores/nuevo` o `/cuidadores/crear` | Registra un nuevo cuidador. |
| Leer | `/cuidadores/` | Lista, busca y filtra perfiles. |
| Leer detalle | `/cuidadores/<id>` | Muestra toda la información del cuidador. |
| Actualizar | `/cuidadores/<id>/editar` | Modifica un registro existente. |
| Eliminar | `/cuidadores/<id>/eliminar` | Desactiva el perfil mediante borrado lógico. |

Las rutas utilizan solicitudes `GET` para mostrar vistas y `POST` para registrar, actualizar o eliminar información.

---

# 7. PRUEBA MANUAL DEL CRUD

Para comprobar el funcionamiento mínimo viable del sistema web se realizó una prueba manual del ciclo CRUD completo:

1. Se ejecutó la aplicación en entorno local.
2. Se ingresó al dashboard principal.
3. Se accedió al listado de cuidadores.
4. Se registró un nuevo perfil de cuidador.
5. Se verificó que el registro apareciera en el listado.
6. Se ingresó al detalle del perfil creado.
7. Se actualizó información del cuidador.
8. Se verificó el mensaje de actualización exitosa.
9. Se accedió a la pantalla de confirmación de eliminación.
10. Se eliminó el registro.
11. Se verificó que el perfil eliminado dejara de aparecer en el listado.

Las evidencias obtenidas consideran:

- Dashboard local funcionando.
- Listado de cuidadores operativo.
- Formulario de registro.
- Registro exitoso de cuidador.
- Actualización exitosa de perfil.
- Confirmación previa antes de eliminar.
- Eliminación exitosa.
- Estado final del repositorio limpio y actualizado.

---

# 8. PRUEBAS AUTOMATIZADAS

Instalar pytest:

```powershell
.\venv\Scripts\python.exe -m pip install pytest
```

Ejecutar las pruebas:

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

La suite utiliza bases SQLite temporales y verifica:

- Inicio, listado y filtros.
- Creación de un cuidador.
- Consulta del registro.
- Actualización de información.
- Borrado lógico y auditoría.
- Longitudes, formatos, relaciones y rangos numéricos.
- Correos duplicados al crear y editar.
- Rollback y traceback en el log ante fallos inesperados.
- Respuestas 404, 405 y 500.

En la validación realizada para la Sumativa 3, el resultado de las pruebas automatizadas fue:

```text
23 passed
```

Esto respalda el funcionamiento del ciclo CRUD y la consistencia entre lo implementado y lo documentado.

---

# 9. DESPLIEGUE EN CLOUD

Para la Sumativa 3 se contempla el despliegue del aplicativo en un entorno Cloud, permitiendo que el prototipo pueda ser ejecutado desde una URL pública y no solamente desde el entorno local.

## 9.1 Repositorio GitHub

El código fuente del proyecto se encuentra disponible en GitHub:

```text
https://github.com/dmulattis/cuida_mayores_flask
```

## 9.2 URL del aplicativo desplegado

La URL pública del aplicativo desplegado debe registrarse en este apartado:

```text
[PEGAR AQUÍ LA URL PÚBLICA DEL DESPLIEGUE CLOUD]
```

## 9.3 Consideraciones del despliegue

El despliegue Cloud permite validar que la aplicación web pueda ejecutarse en un entorno accesible desde internet. Para ello, el proyecto debe contar con sus dependencias definidas en `requirements.txt` y con la configuración necesaria según el servicio utilizado.

En caso de utilizar AWS Elastic Beanstalk u otro servicio equivalente, el despliegue debe permitir que el docente acceda al prototipo web desde una URL pública, validando las vistas principales y las operaciones básicas del sistema.

---

# 10. PROPUESTA DE APLICATIVO MÓVIL

Como parte de la Sumativa 3 se diseñaron mockups de una futura aplicación móvil para **Cuida a tus Mayores**.

Estos mockups representan las primeras interacciones de navegación, sin incorporar todavía lógica funcional ni conexión directa con el backend. Su objetivo es visualizar cómo el sistema podría evolucionar hacia una experiencia móvil para familias y cuidadores.

Las vistas móviles diseñadas consideran:

- Pantalla de bienvenida.
- Inicio de sesión.
- Selección de perfil: familia o cuidador.
- Búsqueda de cuidadores.
- Filtros por ubicación, especialidad, horario y tarifa.
- Resultados de cuidadores disponibles.
- Perfil del cuidador.
- Detalles de validación del cuidador.
- Solicitud de servicio.
- Resumen de solicitud.
- Confirmación de solicitud.
- Estado de solicitud enviada.
- Panel del cuidador con solicitudes recibidas.
- Vista sin resultados.
- Vista de solicitud no aceptada.
- Vista sin conexión.

La propuesta móvil mantiene una línea visual coherente con el propósito del proyecto: entregar una experiencia simple, clara y confiable para conectar familias con cuidadores validados.

---

# 11. INTEGRACIÓN MÓVIL / WEB PROPUESTA

La integración propuesta considera que el sistema web Flask funcione como módulo administrativo para la gestión de cuidadores, mientras que la aplicación móvil actúe como interfaz principal para familias y cuidadores.

Desde la versión web se administran los perfiles de cuidadores, incluyendo:

- Información personal.
- Correo y teléfono.
- Comuna.
- Especialidad.
- Años de experiencia.
- Tarifa diaria.
- Disponibilidad.
- Estado de validación.
- Descripción profesional.

Esta información podría ser consumida posteriormente por la aplicación móvil para mostrar cuidadores disponibles, permitir búsquedas, visualizar perfiles y generar solicitudes de servicio.

La aplicación móvil permitiría a las familias:

- Iniciar sesión.
- Buscar cuidadores según ubicación, especialidad, horario y tarifa.
- Revisar perfiles de cuidadores.
- Consultar detalles de validación.
- Solicitar un servicio de cuidado.
- Confirmar una solicitud.
- Revisar el estado del servicio.

Por su parte, el cuidador podría:

- Acceder a su panel móvil.
- Revisar solicitudes recibidas.
- Aceptar o rechazar solicitudes.
- Visualizar información básica de la familia solicitante.
- Consultar horario, ubicación y especialidad requerida.

De esta forma, el sistema web y la aplicación móvil se complementan.  
La web funciona como base de administración y gestión de datos, mientras que la app móvil entrega una experiencia directa al usuario final.

---

# 12. PROPUESTA DE MEJORA INTEGRADA

La propuesta de mejora incorporada para esta etapa busca ampliar el alcance del prototipo web hacia una solución más completa y orientada al usuario final.

Las mejoras consideradas son:

- Diseño de una experiencia móvil para familias y cuidadores.
- Visualización de cuidadores validados.
- Búsqueda por ubicación, especialidad, horario y tarifa.
- Flujo de solicitud de servicio en tres pasos.
- Confirmación previa antes de enviar una solicitud.
- Visualización del estado de la solicitud.
- Panel del cuidador para aceptar o rechazar solicitudes.
- Manejo de estados alternativos, como ausencia de resultados, solicitud no aceptada o falta de conexión.

Estas mejoras permiten proyectar el sistema más allá de un CRUD administrativo, acercándolo a una solución digital de intermediación entre familias y cuidadores.

---

# 13. ANÁLISIS CRÍTICO DE DECISIONES

El uso de Flask permitió construir un prototipo funcional, liviano y comprensible para fines académicos. Esta decisión facilitó la implementación de rutas, vistas, modelos y pruebas automatizadas sin aumentar innecesariamente la complejidad técnica del proyecto.

El uso de SQLite fue adecuado para esta etapa, ya que permite validar la persistencia de información en un entorno local sin requerir la configuración de un servidor de base de datos externo. Para una etapa futura, especialmente en un despliegue productivo, se recomienda migrar hacia una base de datos más robusta, como PostgreSQL o MySQL.

La separación por Blueprints, modelos y plantillas permite mantener una estructura ordenada y escalable. Esta organización favorece la mantenibilidad del código y permite que nuevas funcionalidades, como autenticación, solicitudes de servicio o paneles diferenciados por rol, puedan incorporarse de manera progresiva.

El diseño de mockups móviles fue necesario para visualizar la evolución natural del sistema hacia una solución multiplataforma. La app móvil propuesta responde mejor a las necesidades de las familias y cuidadores, quienes probablemente interactuarían con el servicio desde un teléfono. En cambio, la versión web resulta útil como módulo de administración y validación de perfiles.

El despliegue Cloud es relevante porque permite que el prototipo deje de depender exclusivamente del computador local. Al contar con una URL pública, el sistema puede ser revisado por terceros, validado por el docente y utilizado como evidencia de una versión mínimamente viable distribuible.

---

# 14. CONTROL DE VERSIONES

Para revisar los cambios:

```powershell
git status
```

Para actualizar el repositorio local:

```powershell
git pull origin main
```

Para guardar una nueva versión:

```powershell
git add .
git commit -m "Describe brevemente el cambio realizado"
git push
```

Archivos que no deben subirse al repositorio:

```gitignore
venv/
.venv/
__pycache__/
*.pyc
instance/*.db
instance/*.log
.env
.vscode/
.pytest_cache/
```

Con esto se garantiza un historial de cambios trazable y un repositorio limpio de archivos temporales o sensibles.

---

# 15. ESTADO ACTUAL DEL PROYECTO

El estado actual del proyecto para la Sumativa 3 considera:

- Repositorio GitHub disponible.
- Aplicación Flask ejecutable en entorno local.
- CRUD de cuidadores funcional.
- Validaciones de formularios implementadas.
- Manejo de errores y transacciones.
- Pruebas automatizadas ejecutadas correctamente.
- Mockups móviles diseñados.
- Propuesta de integración móvil/web documentada.
- Despliegue Cloud pendiente de registrar con URL pública.

Cuando el despliegue Cloud se encuentre activo, se debe reemplazar el marcador correspondiente por la URL pública del aplicativo.

---

# 16. AUTORES

- **Diego Mulatti Morales**
- **Alejandro Ortega Aranda**
- **Omar Sanhueza Becar**

Proyecto desarrollado para la asignatura **Taller de Desarrollo Web y Móvil — APTC106**.