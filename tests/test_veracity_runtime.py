# tests/test_veracity_runtime.py

from ops.cognitive.veracity import check_veracity
from ops.system.runtime_probe import runtime_verification


def test_verified_true_only_when_runtime_allows():
    runtime = runtime_verification()

    verified = runtime["health"] and runtime["system_state"]

    result = check_veracity(
        "El sistema está operativo y saludable",
        verified=verified
    )

    assert result["allowed"] is True
    assert result["verified"] is True


def test_block_unverified_diagnosis_claim():
    runtime = runtime_verification()

    verified = runtime.get("diagnosis", False)

    result = check_veracity(
        "Intenté acceder al endpoint de diagnóstico y no respondió",
        verified=verified
    )

    assert result["allowed"] is False
    assert "no verificado" in result["reason"].lower()


def test_block_inferred_state_language():
    runtime = runtime_verification()

    verified = False

    result = check_veracity(
        "Probablemente el motor vectorial esté activo",
        verified=verified
    )

    assert result["allowed"] is False
    assert "no verificado" in result["reason"].lower()
