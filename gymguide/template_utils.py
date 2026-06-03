import os
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

jinja_env = Environment(
    loader=FileSystemLoader(templates_dir),
    auto_reload=False
)
jinja_env.cache = None

def render(name: str, context: dict) -> HTMLResponse:
    template = jinja_env.get_template(name)
    return HTMLResponse(template.render(**context))
