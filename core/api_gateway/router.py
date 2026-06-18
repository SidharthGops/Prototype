"""
The ONLY place that knows every module exists.

Adding a new module = add one line to MODULE_REGISTRY.
Removing a module = remove one line. Nothing else in core/ should
ever need to change because a module was added or removed.
"""

from fastapi import FastAPI
import importlib

# module_name -> dotted path of its FastAPI router module
MODULE_REGISTRY = {
    "vton": "modules.vton.api.routes",
    "catalog": "modules.catalog.api.routes",
    # "saree": "modules.saree.api.routes",   # ← example of the only line
    #                                            you add for a new module.
}


def create_app() -> FastAPI:
    app = FastAPI(title="AI Visual Commerce Platform")

    for module_name, dotted_path in MODULE_REGISTRY.items():
        router_module = importlib.import_module(dotted_path)
        app.include_router(
            router_module.router,
            prefix=f"/{module_name}",
            tags=[module_name],
        )

    return app


app = create_app()
