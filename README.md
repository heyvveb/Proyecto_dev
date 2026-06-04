# GymGuide — Fitness Management System

Plataforma web para gestionar influencers fitness, rutinas de entrenamiento, suplementos y ejercicios. Interfaz visual con operaciones CRUD completas, soft-delete, restauración de registros y filtros combinados.

**Link:** https://proyecto-dev-o39q.onrender.com/

## Modelos

- **Influencers** — perfiles con categoría, logros, rutina recomendada y suplementos asociados
- **Rutinas** — programas de entrenamiento con nivel, objetivo, duración y ejercicios asignados
- **Suplementos** — catálogo con tipo, marca, precio y beneficios
- **Ejercicios** — banco de ejercicios con grupo muscular, series, repeticiones y descanso


## Tecnologías

| Capa | Stack |
|------|-------|
| Backend | FastAPI, SQLModel, Pydantic v2 |
| Base de datos | PostgreSQL (Neon)|
| Frontend | Jinja2, HTML, CSS, JS|
| Despliegue | Render (uvicorn) |

### Endpoints

Todos los endpoints:

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/{entidad}/{id}` | Obtener por ID |
| `POST` | `/{entidad}` | Crear nuevo registro |
| `PATCH` | `/{entidad}/{id}` | Actualizar campos parcialmente |
| `DELETE` | `/{entidad}/{id}` | status → inactive |
| `POST` | `/{entidad}/{id}/restore` | Restaurar registro inactivo |

Mismos patrones para rutinas, suplementos y ejercicios.

Endpoints de relaciones:

| Método | Ruta | Descripción |
|---|---|---|
| `PUT` | `/influencers/{id}/suplementos` | Asignar suplementos a un influencer |
| `PUT` | `/rutinas/{id}/ejercicios` | Asignar ejercicios a una rutina |


### Páginas

| Ruta | Descripción |
|---|---|
| `/` | Página principal con estadísticas y accesos directos |
| `/dashboard` | Estadísticas con gráficas de barras por categoría, nivel, tipo y grupo muscular |
| `/search?q=...` | Búsqueda global simultánea en las cuatro entidades |
| `/influencers` | Listado con filtros por categoría, rutina y suplemento |
| `/influencers/{id}` | Detalle con suplementos asociados y enlace a rutina |
| `/rutinas` | Listado con filtros por nivel, objetivo, duración y ejercicio |
| `/rutinas/{id}` | Detalle con ejercicios e influencers que la recomiendan |
| `/suplementos` | Listado con filtros por tipo, marca y precio |
| `/suplementos/{id}` | Detalle con influencers que lo usan |
| `/ejercicios` | Listado con filtros por grupo muscular |
| `/ejercicios/{id}` | Detalle con rutinas que lo incluyen |


## Funcionalidades

- CRUD completo con restauración, los registros eliminados se marcan como inactive y son recuperables
- Relaciones M:N 
- Filtros combinados 
- Consulta por nombre en todas las entidades desde la barra de navegación
- Páginas de detalle con enlaces cruzados entre entidades
- Vistas de elementos activos/eliminados
- Conteos activos/inactivos y gráficas de barras en HTML/CSS

## Uso

```bash
uvicorn main:app --reload
```
