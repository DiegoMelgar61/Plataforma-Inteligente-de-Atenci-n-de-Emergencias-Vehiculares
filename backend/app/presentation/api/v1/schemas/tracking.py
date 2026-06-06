from pydantic import BaseModel, Field


class LocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitud WGS-84")
    lng: float = Field(..., ge=-180, le=180, description="Longitud WGS-84")
