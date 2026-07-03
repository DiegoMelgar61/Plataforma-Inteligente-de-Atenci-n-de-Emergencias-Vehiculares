from pydantic import BaseModel, Field


class ProcesamientoIAResponse(BaseModel):
    """Resultado expuesto tras ejecutar el pipeline de IA sobre un incidente."""

    id_incidente: int
    estado: str = Field(description="Estado del incidente tras el pipeline (ej. CLASIFICADO)")
    clasificacion: str
    prioridad: str
    resumen_ia: str | None = None
