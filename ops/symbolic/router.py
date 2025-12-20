from fastapi import APIRouter
from ops.symbolic.evaluator import evaluate

router = APIRouter(prefix="/ops/symbolic", tags=["Symbolic"])

@router.get("/evaluate")
def symbolic_evaluate():
    return evaluate()
