from fastapi.testclient import TestClient
from service_main import app

client = TestClient(app)

def test_affective_train_run_endpoint():
    """
    Test de integración para el endpoint /ops/affective-train/run.
    Verifica que el módulo afectivo responda correctamente con los campos esperados.
    """
    response = client.post("/ops/affective-train/run")
    assert response.status_code == 200, "El endpoint no respondió 200 OK"

    data = response.json()
    for field in ["timestamp", "predicted_mood", "predicted_energy", "confidence", "model_version"]:
        assert field in data, f"Falta el campo '{field}' en la respuesta"

    assert isinstance(data["predicted_mood"], str)
    assert isinstance(data["predicted_energy"], float)
    assert isinstance(data["confidence"], float)
    assert data["model_version"].startswith("v1.0")

    print("✅ /ops/affective-train/run responde correctamente")

