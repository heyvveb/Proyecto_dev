# GymGuide

Plataforma web de gestión de entrenamiento: influencers, rutinas, suplementos y ejercicios
Link: https://proyecto-dev-o39q.onrender.com/
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
| Frontend | Jinja2|
| Despliegue | Render (uvicorn) |


## Uso

```bash
uvicorn main:app --reload
```

### Endpoints

Todos los endpoints:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/influencers` | Listar influencers |
| `POST` | `/influencers` | Crear influencer |
| `PATCH` | `/influencers/{id}` | Actualizar |
| `DELETE` | `/influencers/{id}` | Eliminar |
| `PUT` | `/influencers/{id}/suplementos` | Asociar suplementos |
| `POST` | `/influencers/{id}/restore` | Restaurar |

Mismos patrones para rutinas, suplementos y ejercicios.

### Páginas

| Ruta | Descripción |
|------|-------------|
| `/` | Dashboard con estadísticas |
| `/influencers` | Listado de influencers |
| `/influencers/{id}` | Detalle con suplementos y rutina |
| `/rutinas` | Listado de rutinas |
| `/rutinas/{id}` | Detalle con ejercicios e influencers |
| `/suplementos` | Listado de suplementos |
| `/suplementos/{id}` | Detalle con influencers asociados |
| `/ejercicios` | Listado de ejercicios |
| `/ejercicios/{id}` | Detalle con rutinas asociadas |


## Funcionalidades

- CRUD completo con soft-delete y restauración
- Relaciones M:N 
- Filtros combinados 
- Páginas de detalle con enlaces cruzados entre entidades
- Vistas de elementos activos/eliminados
