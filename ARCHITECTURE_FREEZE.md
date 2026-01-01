# Natacha — Architecture Freeze v1

## Modo operativo
- Mode: pre-ML-unified
- Semantic engine: heuristic-only (lazy)
- Vector engine: disabled (stub)
- Learning: OFF
- Self-modification: BLOCKED

## Garantías
- No side effects en /agent/interact
- Memoria NDJSON canónica
- Cold start deterministic
- Gateway único (natacha-api)

## Regla de oro
Nada se activa sin:
1) flag explícito
2) test local
3) snapshot previo
