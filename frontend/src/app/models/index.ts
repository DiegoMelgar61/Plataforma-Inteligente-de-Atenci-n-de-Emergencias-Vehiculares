export interface LoginRequest {
  correo_electronico: string;
  contrasena: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export type UserRole = 'CLIENTE' | 'TALLER' | 'ADMIN';

export interface User {
  id_usuario: number;
  correo_electronico: string;
  nombre_completo: string;
  telefono?: string;
  rol: UserRole;
  activo: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

export interface Taller {
  id_taller: number;
  id_usuario: number;
  nombre_negocio: string;
  nit?: string;
  direccion?: string;
  tasa_comision: number;
  latitud?: number | null;
  longitud?: number | null;
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface TallerCreate {
  nombre_negocio: string;
  nit?: string;
  direccion?: string;
  tasa_comision?: number;
  latitud?: number | null;
  longitud?: number | null;
}

export interface Tecnico {
  id_tecnico: number;
  id_taller: number;
  id_usuario?: number | null;
  nombre_completo: string;
  telefono?: string;
  disponible: boolean;
  ubicacion_lat?: number;
  ubicacion_lng?: number;
  fecha_creacion: string;
}

export interface TecnicoCreate {
  nombre_completo: string;
  telefono?: string;
  disponible?: boolean;
}

export interface TecnicoWithUserCreate {
  nombre_completo: string;
  telefono?: string;
  correo_electronico: string;
  contrasena: string;
  id_taller?: number;
}

export type EstadoIncidente =
  | 'PENDIENTE' | 'EN_PROCESO_IA' | 'CLASIFICADO' | 'ASIGNADO'
  | 'EN_CAMINO' | 'EN_PROCESO' | 'ATENDIDO' | 'CANCELADO' | 'INCIERTO';

export type Prioridad = 'BAJA' | 'MEDIA' | 'ALTA';
export type Clasificacion = 'BATERIA' | 'LLANTA' | 'CHOQUE' | 'MOTOR' | 'OTROS' | 'INCIERTO';

export interface Evidencia {
  id_evidencia: number;
  id_incidente: number;
  tipo: 'IMAGEN' | 'AUDIO' | 'TEXTO';
  url_archivo?: string;
  texto_transcrito?: string;
  fecha_creacion: string;
}

export interface Incident {
  id_incidente: number;
  id_usuario_cliente: number;
  id_vehiculo?: number;
  latitud?: number;
  longitud?: number;
  estado: EstadoIncidente;
  prioridad: Prioridad;
  clasificacion: Clasificacion;
  resumen_ia?: string;
  tiempo_estimado_llegada_minutos?: number;
  fecha_creacion: string;
  fecha_actualizacion?: string;
  evidencias?: Evidencia[];
  taller_asignado?: string | null;
  tecnico_asignado?: string | null;
  tecnico_telefono?: string | null;
  monto_estimado?: number | null;
}

export interface Asignacion {
  id_asignacion: number;
  id_incidente: number;
  id_taller: number;
  id_tecnico?: number;
  fecha_asignacion: string;
  fecha_aceptacion?: string;
  fecha_rechazo?: string;
  motivo_rechazo?: string;
  monto_cotizado?: number | string | null;
  tiempo_estimado_minutos?: number | null;
  tiempo_estimado_reparacion?: number | null;
  notas_cotizacion?: string | null;
  estado_cotizacion?: 'PENDIENTE' | 'ACEPTADA' | 'RECHAZADA' | string | null;
  cotizacion_aceptada?: boolean | null;
  fecha_cotizacion?: string | null;
  fecha_aceptacion_cotizacion?: string | null;
  fecha_rechazo_cotizacion?: string | null;
  incidente?: Incident;
  tecnico?: Tecnico;
}

export interface QuotationRequest {
  monto_cotizado: number;
  tiempo_estimado_reparacion?: number | null;
  notas_cotizacion?: string | null;
}

export interface CotizacionDetalle {
  id_asignacion: number;
  id_incidente: number;
  monto_cotizado: number | null;
  tiempo_estimado_reparacion: number | null;
  notas_cotizacion: string | null;
  cotizacion_aceptada: boolean | null;
  estado_incidente: string;
  timestamp?: string | null;
}

export interface DashboardStats {
  total_incidentes: number;
  incidentes_atendidos?: number;
  incidentes_por_estado?: Array<{ estado: string; total: number }>;
  total_recaudado: number;
  tiempo_promedio_atencion_minutos: number | null;
  incidentes_por_clasificacion: Record<string, number> | Array<{ clasificacion: string; total: number }>;
  incidentes_ultimos_7_dias: Array<{ fecha?: string; dia?: string; total: number }>;
  taller_top?: {
    id_taller?: number;
    nombre_negocio: string;
    total_atendidos: number;
  } | null;
  taller_mas_eficiente?: {
    id_taller?: number;
    nombre_negocio: string;
    incidentes_atendidos?: number;
    tiempo_promedio_atencion_minutos?: number | null;
  } | null;
}

export interface Notification {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  timestamp: Date;
}
