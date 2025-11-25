# routes/notion_blueprint_routes.py

from fastapi import APIRouter, HTTPException
from integrations.notion_client import create_page, append_blocks

router = APIRouter(prefix="/notion", tags=["Notion Blueprint"])


BLUEPRINT = [
    {"type": "heading_1", "content": "Descripción general"},
    {"type": "paragraph", "content": "Objetivo del cliente, contexto y requerimiento."},

    {"type": "heading_1", "content": "Modelos cotizados"},
    {"type": "bulleted_list", "items": []},

    {"type": "heading_1", "content": "Precios y Costos"},
    {"type": "table", "columns": ["Concepto", "Valor"], "rows": []},

    {"type": "heading_1", "content": "Logística y Tiempos"},
    {"type": "paragraph", "content": "Puertos, tiempos, producción, embarque."},

    {"type": "heading_1", "content": "Estado actual"},
    {"type": "to_do", "content": "Proforma pendiente"},

    {"type": "heading_1", "content": "Documentos adjuntos"},
]


@router.post("/project_blueprint")
async def create_project_blueprint(
    cliente: str,
    proyecto: str,
    proveedor: str = "",
    modelo: str = "",
    paso: str = "",
):
    """
    Crea automáticamente un proyecto LLVC con estructura estándar.
    """

    try:
        page = create_page(
            parent_db_id="225d6b3ca30780378e10fb409b0fb668",
            title=cliente,
            properties={
                "PROYECTO": proyecto,
                "MODELOS": modelo,
                "PROVEEDOR": proveedor,
                "PROXIMO PASO": paso,
                "FASE": "F1 – Lead",
                "Status": "En curso",
            }
        )

        page_id = page["id"]

        # Add body blocks
        append_blocks(page_id, BLUEPRINT)

        return {
            "status": "ok",
            "page_id": page_id,
            "url": page.get("url", None),
            "message": "Proyecto creado exitosamente con blueprint LLVC."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
