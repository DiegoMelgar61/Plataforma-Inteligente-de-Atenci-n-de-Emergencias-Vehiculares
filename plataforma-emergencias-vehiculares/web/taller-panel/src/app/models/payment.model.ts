export type EstadoPago = 'NO_PAGO' | 'PENDIENTE' | 'PAGADO' | 'RECHAZADO';

export interface Payment {
  id_pago: string;
  id_incidente: string;
  id_usuario_cliente?: string;
  id_taller?: string;
  id_asignacion?: string;
  monto: number;
  comision_plataforma?: number;
  estado: EstadoPago;
  metodo_pago?: string;
  id_transaccion?: string;
  comprobante_url?: string;
  notas_cliente?: string;
  fecha_creacion?: string;
  fecha_marcado_pago?: string;
  fecha_confirmacion?: string;
  fecha_rechazo?: string;
  motivo_rechazo?: string;
  id_usuario_confirmo?: string;
  fecha_actualizacion?: string;
}

export interface PaymentStats {
  total_cobrado: number;
  total_pendiente: number;
  total_no_pago: number;
  count_por_estado: Record<string, number>;
}
