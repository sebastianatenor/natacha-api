# Security Policy

## Supported Versions
- `main` protegido por CI “Sanity”.
- Tags `stable-*` son snapshots inmutables.

## Reporting a Vulnerability
- Email: security@llvc-global.com (o tu correo operativo)
- Asunto: `[SECURITY] Natacha API`
- Incluí: versión/tag, endpoint afectado, PoC, impacto y severidad.

## Severity
- **Critical**: RCE, auth bypass, credenciales expuestas → 24h
- **High**: privilege escalation, data exfiltration → 72h
- **Medium**: info leak, DoS limitado → 7 días
- **Low**: mejores prácticas, hardening → próxima release

## Handling
1. Reproducir y aislar.
2. Hotfix en branch `fix/security/<slug>` con pruebas.
3. Revisión obligatoria (CODEOWNERS).
4. Tag `stable-YYYYMMDD-HHMMSS` y changelog corto.
