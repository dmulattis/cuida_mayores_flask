<div align="center">

# CUIDA A TUS MAYORES  
## Sistema web para la gestión de perfiles de cuidadores y propuesta de integración móvil

**Asignatura:** Taller de Desarrollo Web y Móvil — APTC106  
**Evaluación:** Semana 09 — Sumativa 3  
**Integrantes:** Diego Mulatti Morales · Alejandro Ortega Aranda · Omar Sanhueza Becar  
**Repositorio:** https://github.com/dmulattis/cuida_mayores_flask  

**URL GitHub Pages:**  
https://dmulattis.github.io/cuida_mayores_flask/

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
- Registrar nuevas comunas cuando no existan en la base inicial.
- Registrar nuevas especialidades o profesiones cuando no existan en la base inicial.
- Mantener la información en una base de datos local SQLite.
- Ejecutar pruebas automatizadas del ciclo CRUD.

Para la **Semana 09 — Sumativa 3**, el proyecto incorpora además:

- Integración de la propuesta de mejora desarrollada en la semana anterior.
- Publicación de una versión estática del prototipo mediante GitHub Pages.
- Generación de la versión estática con Frozen-Flask.
- Diseño de mockups móviles para representar las primeras interacciones de navegación.
- Propuesta de integración entre el sistema web y una futura aplicación móvil.
- Mejora visual de contraste en la barra superior.
- Mejora funcional para registrar nuevas comunas y nuevas especialidades/profesiones desde el formulario.
- Propuesta de agendamiento por horas, jornada diaria, semana o mes.
- Propuesta de ruta del cuidador con validación GPS de inicio y término de jornada.

> El prototipo web tiene fines académicos.  
> Actualmente permite validar el funcionamiento mínimo viable mediante CRUD, pruebas automatizadas y diseño de una propuesta móvil inicial.  
> La versión publicada en GitHub Pages es estática, por lo que no ejecuta lógica dinámica de backend ni operaciones reales de base de datos.  
> Las operaciones reales del CRUD se validan en la aplicación Flask ejecutada en entorno local o Codespaces.

---

# 1. ENTORNO DE DESARROLLO

El proyecto fue desarrollado utilizando las siguientes tecnologías:

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11 o superior |
| Framework web | Flask |
| Acceso a datos | Flask-SQLAlchemy |
| Base de datos | SQLite |
| Interfaz | HTML5, CSS3, Bootstrap, CSS propio y Jinja |
| Pruebas | pytest |
| Publicación estática | Frozen-Flask |
| Despliegue visual | GitHub Pages |
| Servidor WSGI | Gunicorn |
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
├── docs/
│   └── Versión estática generada con Frozen-Flask para GitHub Pages
│
├── instance/
│   └── Archivos locales generados en ejecución, no versionados en Git
│
├── tests/
│   ├── conftest.py
│   └── test_crud.py
│
├── .gitignore
├── application.py
├── freeze.py
├── Procfile
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
| `app/static/css/estilos.css` | Define el diseño visual, responsivo y mejoras de contraste. |
| `seed.py` | Crea la base local con perfiles de ejemplo. |
| `run.py` | Inicia el servidor Flask. |
| `application.py` | Expone la aplicación para despliegues compatibles con WSGI. |
| `Procfile` | Define el comando de arranque para despliegues con Gunicorn. |
| `freeze.py` | Genera la versión estática del sitio en la carpeta `docs/`. |
| `docs/` | Contiene la versión estática publicada mediante GitHub Pages. |
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
- Especialidad o profesión.
- Años de experiencia.
- Tarifa diaria.
- Disponibilidad.
- Estado de validación.
- Descripción profesional.

Como mejora incorporada a partir de la retroalimentación docente, el formulario permite seleccionar **“Otra comuna”** u **“Otra especialidad / profesión”** cuando la opción requerida no existe en la base de datos inicial.

En ese caso, el usuario puede escribir una nueva comuna o una nueva especialidad/profesión, la cual queda registrada y asociada al perfil del cuidador.

Esta mejora resuelve la limitación inicial de depender únicamente de catálogos previamente cargados en la base de datos.

## 5.4 Validaciones

El sistema comprueba:

- Campos obligatorios.
- Longitud máxima de los campos de texto antes de persistirlos.
- Formato de correo electrónico mediante expresión regular.
- Formato de teléfono mediante expresión regular, entre 8 y 15 dígitos.
- Especialidad válida o nueva especialidad ingresada por el usuario.
- Comuna válida o nueva comuna ingresada por el usuario.
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
12. Se probó la opción **“Otra comuna”**.
13. Se probó la opción **“Otra especialidad / profesión”**.

Las evidencias obtenidas consideran:

- Dashboard local funcionando.
- Listado de cuidadores operativo.
- Formulario de registro.
- Registro exitoso de cuidador.
- Actualización exitosa de perfil.
- Confirmación previa antes de eliminar.
- Eliminación exitosa.
- Registro de nueva comuna desde el formulario.
- Registro de nueva especialidad/profesión desde el formulario.
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

# 9. DESPLIEGUE Y PUBLICACIÓN EN GITHUB PAGES

Para la Sumativa 3 se realizó una publicación del prototipo mediante GitHub Pages, utilizando una versión estática generada con Frozen-Flask desde la aplicación Flask original.

## 9.1 Repositorio GitHub

El código fuente del proyecto se encuentra disponible en GitHub:

```text
https://github.com/dmulattis/cuida_mayores_flask
```

## 9.2 URL pública del prototipo

La versión estática del prototipo se encuentra publicada en:

```text
https://dmulattis.github.io/cuida_mayores_flask/
```

## 9.3 Consideraciones del despliegue

GitHub Pages permite publicar contenido estático desde un repositorio. Por este motivo, se utilizó Frozen-Flask para generar una versión navegable del prototipo desde la carpeta `docs/`.

Esta publicación permite visualizar las principales vistas del sistema desde una URL pública. Sin embargo, al tratarse de una versión estática, no ejecuta lógica dinámica de backend ni operaciones reales de base de datos.

Las operaciones dinámicas del CRUD fueron validadas en la aplicación Flask ejecutada en entorno local/Codespaces y mediante pruebas automatizadas con pytest.

## 9.4 Generar nuevamente la versión estática

Si se realizan cambios en vistas, estilos o rutas que deban verse en GitHub Pages, se debe regenerar la carpeta `docs/` con:

```powershell
.\venv\Scripts\python.exe .\freeze.py
```

Luego se deben subir los cambios:

```powershell
git add docs freeze.py requirements.txt
git commit -m "Actualiza versión estática para GitHub Pages"
git push origin main
```

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
- Configuración de agenda del servicio.
- Selección de modalidad de contratación.
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

# 11. MODELO DE AGENDAMIENTO PROPUESTO

A partir de la retroalimentación docente, se identificó como punto de incertidumbre la forma en que se agenda el servicio del cuidador.

Para resolverlo, se propone incorporar en el mockup móvil una pantalla intermedia de configuración de agenda antes de confirmar la solicitud.

Esta pantalla permitiría definir:

- Servicio por horas.
- Servicio por jornada diaria.
- Servicio semanal recurrente.
- Servicio mensual.
- Fecha de inicio.
- Fecha de término, cuando corresponda.
- Días requeridos.
- Hora de inicio.
- Hora de término.
- Total estimado del servicio.

De esta forma, la solicitud no queda limitada a una única modalidad de contratación y permite representar distintos escenarios reales de cuidado domiciliario.

---

# 12. RUTA DEL CUIDADOR Y VALIDACIÓN GPS PROPUESTA

Además del flujo de la familia, se propone complementar el mockup con la ruta del cuidador.

La ruta del cuidador considera:

1. Inicio de sesión como cuidador.
2. Visualización del panel de solicitudes recibidas.
3. Revisión del detalle de la solicitud.
4. Aceptación o rechazo del servicio.
5. Visualización del próximo servicio confirmado.
6. Inicio de jornada.
7. Validación de ubicación mediante GPS.
8. Registro de hora de inicio.
9. Jornada en curso.
10. Finalización de jornada.
11. Validación GPS de término.
12. Resumen de horas trabajadas.

La restricción espacial mediante GPS busca verificar que el cuidador se encuentre en la dirección correspondiente antes de iniciar o finalizar la jornada.

Si el cuidador se encuentra dentro del rango permitido, el sistema permite iniciar el servicio.  
Si el cuidador se encuentra fuera del rango, el sistema muestra una alerta indicando que debe acercarse al domicilio registrado para poder marcar el inicio o término de la jornada.

---

# 13. INTEGRACIÓN MÓVIL / WEB PROPUESTA

La integración propuesta considera que el sistema web Flask funcione como módulo administrativo para la gestión de cuidadores, mientras que la aplicación móvil actúe como interfaz principal para familias y cuidadores.

Desde la versión web se administran los perfiles de cuidadores, incluyendo:

- Información personal.
- Correo y teléfono.
- Comuna.
- Especialidad o profesión.
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
- Configurar modalidad de agenda.
- Solicitar un servicio de cuidado.
- Confirmar una solicitud.
- Revisar el estado del servicio.

Por su parte, el cuidador podría:

- Acceder a su panel móvil.
- Revisar solicitudes recibidas.
- Aceptar o rechazar solicitudes.
- Visualizar información básica de la familia solicitante.
- Consultar horario, ubicación y especialidad requerida.
- Marcar inicio y término de jornada mediante validación GPS.

De esta forma, el sistema web y la aplicación móvil se complementan.  
La web funciona como base de administración y gestión de datos, mientras que la app móvil entrega una experiencia directa al usuario final.

---

# 14. PROPUESTA DE MEJORA INTEGRADA

La propuesta de mejora incorporada para esta etapa busca ampliar el alcance del prototipo web hacia una solución más completa y orientada al usuario final.

Las mejoras consideradas son:

- Diseño de una experiencia móvil para familias y cuidadores.
- Visualización de cuidadores validados.
- Búsqueda por ubicación, especialidad, horario y tarifa.
- Flujo de solicitud de servicio en pasos.
- Pantalla intermedia para definir modalidad de agendamiento.
- Confirmación previa antes de enviar una solicitud.
- Visualización del estado de la solicitud.
- Panel del cuidador para aceptar o rechazar solicitudes.
- Ruta del cuidador posterior a la aceptación del servicio.
- Marcaje de inicio y término de jornada mediante restricción espacial GPS.
- Manejo de estados alternativos, como ausencia de resultados, solicitud no aceptada o falta de conexión.
- Mejora visual de contraste en la barra de navegación.
- Registro de nuevas comunas desde el formulario.
- Registro de nuevas especialidades o profesiones desde el formulario.
- Publicación estática del prototipo mediante GitHub Pages y Frozen-Flask.

Estas mejoras permiten proyectar el sistema más allá de un CRUD administrativo, acercándolo a una solución digital de intermediación entre familias y cuidadores.

---

# 15. ANÁLISIS CRÍTICO DE DECISIONES

El uso de Flask permitió construir un prototipo funcional, liviano y comprensible para fines académicos. Esta decisión facilitó la implementación de rutas, vistas, modelos y pruebas automatizadas sin aumentar innecesariamente la complejidad técnica del proyecto.

El uso de SQLite fue adecuado para esta etapa, ya que permite validar la persistencia de información en un entorno local sin requerir la configuración de un servidor de base de datos externo. Para una etapa futura, especialmente en un despliegue productivo, se recomienda migrar hacia una base de datos más robusta, como PostgreSQL o MySQL.

La separación por Blueprints, modelos y plantillas permite mantener una estructura ordenada y escalable. Esta organización favorece la mantenibilidad del código y permite que nuevas funcionalidades, como autenticación, solicitudes de servicio o paneles diferenciados por rol, puedan incorporarse de manera progresiva.

La mejora de comunas y especialidades/profesiones responde a una limitación del prototipo inicial. En la primera versión, el registro de cuidadores dependía de catálogos previamente cargados. Con la mejora implementada, el usuario puede registrar una nueva comuna o profesión si no existe en la base de datos inicial, aumentando la flexibilidad del sistema.

El ajuste de contraste visual fue incorporado para mejorar la legibilidad de la interfaz, especialmente en la barra superior, donde los enlaces de navegación debían mantener suficiente contraste sobre el fondo verde.

El diseño de mockups móviles fue necesario para visualizar la evolución natural del sistema hacia una solución multiplataforma. La app móvil propuesta responde mejor a las necesidades de las familias y cuidadores, quienes probablemente interactuarían con el servicio desde un teléfono. En cambio, la versión web resulta útil como módulo de administración y validación de perfiles.

La incorporación de una pantalla intermedia de agendamiento permite resolver la incertidumbre sobre la modalidad de contratación del cuidador. El servicio puede requerirse por horas, jornada diaria, semana o mes, por lo que se propone una etapa específica para configurar fecha, horario y recurrencia antes de confirmar la solicitud.

La ruta del cuidador y la validación GPS permiten abordar la trazabilidad del servicio. Esta propuesta busca verificar que el cuidador se encuentre en la dirección correspondiente al iniciar y finalizar la jornada, reduciendo incertidumbre operacional y entregando mayor seguridad a las familias.

GitHub Pages fue utilizado para cumplir con la publicación del prototipo en una URL pública. Sin embargo, al tratarse de un servicio orientado a contenido estático, se utilizó Frozen-Flask para generar una versión navegable del sitio. Las funciones dinámicas del CRUD se mantienen validadas en la aplicación Flask ejecutada localmente o en Codespaces.

---

# 16. CONTROL DE VERSIONES

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

# 17. ESTADO ACTUAL DEL PROYECTO

El estado actual del proyecto para la Sumativa 3 considera:

- Repositorio GitHub disponible.
- Aplicación Flask ejecutable en entorno local.
- CRUD de cuidadores funcional.
- Validaciones de formularios implementadas.
- Registro de nuevas comunas desde el formulario.
- Registro de nuevas especialidades/profesiones desde el formulario.
- Manejo de errores y transacciones.
- Pruebas automatizadas ejecutadas correctamente.
- Mockups móviles diseñados.
- Propuesta de integración móvil/web documentada.
- Propuesta de agendamiento incorporada.
- Ruta del cuidador propuesta.
- Validación GPS propuesta para inicio y término de jornada.
- Contraste visual mejorado.
- Versión estática publicada en GitHub Pages mediante Frozen-Flask.

URL pública:

```text
https://dmulattis.github.io/cuida_mayores_flask/
```

Esta versión permite visualizar el prototipo desde una URL pública.  
Las operaciones dinámicas del CRUD se validan en Flask local/Codespaces y mediante pruebas automatizadas con pytest.

---

# 18. AUTORES

- **Diego Mulatti Morales**
- **Alejandro Ortega Aranda**
- **Omar Sanhueza Becar**

Proyecto desarrollado para la asignatura **Taller de Desarrollo Web y Móvil — APTC106**.