# ops/cognitive/project_profiles.py

from dataclasses import dataclass
from typing import List


@dataclass
class ProjectCognitiveProfile:
    name: str
    description: str
    primary_focus: List[str]
    memory_bias: str
    tone: str


PROJECT_PROFILES = {
    "LLVC": ProjectCognitiveProfile(
        name="LLVC",
        description="Operación de importación, ventas y logística",
        primary_focus=[
            "importaciones",
            "clientes",
            "proveedores",
            "costos",
            "logística",
            "seguimiento operativo",
        ],
        memory_bias="executive",
        tone="operativo, claro, orientado a resultados",
    ),

    "MADE_IN_LATAM": ProjectCognitiveProfile(
        name="Made in Latam",
        description="Startup de marketplace B2B para LATAM",
        primary_focus=[
            "producto",
            "estrategia",
            "roadmap",
            "modelo de negocio",
            "alianzas",
            "escalabilidad",
        ],
        memory_bias="structural",
        tone="estratégico, exploratorio, de largo plazo",
    ),

    "PERSONAL": ProjectCognitiveProfile(
        name="Personal",
        description="Gestión personal y holding de proyectos",
        primary_focus=[
            "prioridades",
            "agenda",
            "decisiones",
            "equilibrio",
            "visión general",
        ],
        memory_bias="executive",
        tone="claro, sintético, orientado a decisión",
    ),
}
