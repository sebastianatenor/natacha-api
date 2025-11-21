"""
inspect_routes.py

Script para listar todas las rutas registradas en service_main.app,
mostrando:
- PATH
- MÉTODOS
- NOMBRE
- MÓDULO PYTHON
- FUNCIÓN

Se puede usar para auditar qué endpoints están vivos, en qué archivo
están definidos y qué función los maneja.
"""

from service_main import app

try:
    from fastapi.routing import APIRoute
except ImportError:
    # Fallback básico si cambia el import en versiones futuras
    from fastapi import routing as fastapi_routing
    APIRoute = fastapi_routing.APIRoute  # type: ignore[misc]


def main() -> None:
    print("== RUTAS FASTAPI ==\n")

    # Filtramos solo rutas "normales" (no websockets, etc.)
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append(route)

    # Ordenamos por path para que sea más legible
    routes.sort(key=lambda r: r.path)

    for route in routes:
        path = route.path
        methods = sorted(route.methods) if route.methods else []
        name = route.name

        endpoint = route.endpoint
        module = getattr(endpoint, "__module__", "<?>")
        func_name = getattr(endpoint, "__name__", repr(endpoint))

        print(f"PATH:      {path}")
        print(f"METHODS:   {methods}")
        print(f"NAME:      {name}")
        print(f"MODULE:    {module}")
        print(f"FUNC:      {func_name}")
        print("-" * 70)


if __name__ == "__main__":
    main()
