from uuid import UUID

from pydantic import BaseModel


class IncidentesPorEstado(BaseModel):
    estado: str
    total: int


class IncidentesPorClasificacion(BaseModel):
    clasificacion: str
    total: int


class IncidentesPorDia(BaseModel):
    dia: str
    total: int


class TallerTop(BaseModel):
    id_taller: UUID
    nombre_negocio: str
    total_atendidos: int


class DashboardStatsResponse(BaseModel):
    total_incidentes: int
    incidentes_por_estado: list[IncidentesPorEstado]
    tiempo_promedio_atencion_minutos: float | None
    incidentes_por_clasificacion: list[IncidentesPorClasificacion]
    total_recaudado: float
    taller_top: TallerTop | None
    incidentes_ultimos_7_dias: list[IncidentesPorDia]
    porcentaje_atendidos: float
    filtrado_por_tenant: str | None
