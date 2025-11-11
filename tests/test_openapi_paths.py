import importlib
def test_ops_self_register_present():
    app = importlib.import_module("service_main").app
    spec = app.openapi()
    assert "/ops/self_register" in spec.get("paths", {}), "Missing /ops/self_register in OpenAPI"
