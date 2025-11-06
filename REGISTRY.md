# REGISTRY.md — Natacha Core

Service: natacha-api-a  
Canonical URL: https://natacha-api-a-422255208682.us-central1.run.app  
Auth: Private (ID token, SA o user autorizado)  

Guías:
- Producción SOLO invoca la canónica.
- Nada de *.a.run.app no-canónicas (hook pre-commit lo bloquea).
- Entry point: `canal_a.main:app`
- Health: `/ops/health` (200 OK), `/ops/version` (meta & libs)

Última verificación: (completar con fecha/UTC y revisión)
