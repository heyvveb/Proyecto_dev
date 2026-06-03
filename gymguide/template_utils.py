import os
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse
#Ruta templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

#Configuración de Jinja
jinja_env = Environment(
    loader=FileSystemLoader(templates_dir),
    auto_reload=False
)
#Evita templeates desactualizados
jinja_env.cache = None
#Renderiza el templeate con los datos que obtivo
def render(name: str, context: dict) -> HTMLResponse:
    #Busca templeate
    template = jinja_env.get_template(name)
    #Renderiza el templeate 
    return HTMLResponse(template.render(**context))
