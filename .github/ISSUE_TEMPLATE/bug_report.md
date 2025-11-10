name: Bug report
description: Reportar bug en Natacha API
labels: [bug]
body:
  - type: textarea
    id: desc
    attributes: { label: Descripción, description: ¿Qué pasó? }
  - type: input
    id: version
    attributes: { label: Versión/Tag, placeholder: stable-YYYYMMDD-HHMMSS }
  - type: textarea
    id: steps
    attributes: { label: Pasos para reproducir }
  - type: textarea
    id: expected
    attributes: { label: Esperado }
  - type: textarea
    id: extra
    attributes: { label: Logs/PoC }
