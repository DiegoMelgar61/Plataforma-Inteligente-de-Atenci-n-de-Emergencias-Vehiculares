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
  id_usuario: string;
  correo_electronico: string;
  nombre_completo: string;
  telefono?: string;
  rol: UserRole;
  activo: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

export interface Taller {
  id_taller: string;
  id_usuario: string;
  nombre_negocio: string;
  nit?: string;
  direccion?: string;
  tasa_comision: number;
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface TallerCreate {
  nombre_negocio: string;
  nit?: string;
  direccion?: string;
  tasa_comision?: number;
}

export interface Tecnico {
  id_tecnico: string;
  id_taller: string;
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

export type EstadoIncidente =
  | 'PENDIENTE' | 'EN_PROCESO_IA' | 'CLASIFICADO' | 'ASIGNADO'
  | 'EN_CAMINO' | 'EN_PROCESO' | 'ATENDIDO' | 'CANCELADO' | 'INCIERTO';

export type Prioridad = 'BAJA' | 'MEDIA' | 'ALTA';
export type Clasificacion = 'BATERIA' | 'LLANTA' | 'CHOQUE' | 'MOTOR' | 'OTROS' | 'INCIERTO';

export interface Evidencia {
  id_evidencia: string;
  id_incidente: string;
  tipo: 'IMAGEN' | 'AUDIO' | 'TEXTO';
  url_archivo?: string;
  texto_transcrito?: string;
  fecha_creacion: string;
}

export interface Incident {
  id_incidente: string;
  id_usuario_cliente: string;
  id_vehiculo?: string;
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
}

export interface Asignacion {
  id_asignacion: string;
  id_incidente: string;
  id_taller: string;
  id_tecnico?: string;
  fecha_asignacion: string;
  fecha_aceptacion?: string;
  fecha_rechazo?: string;
  motivo_rechazo?: string;
  incidente?: Incident;
  tecnico?: Tecnico;
}

export interface Notification {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  timestamp: Date;
}
