export interface Tenant {
  id_tenant: string;
  nombre: string;
  descripcion: string | null;
  activo: boolean;
  fecha_creacion: string;
}

export interface TenantCreate {
  nombre: string;
  descripcion?: string;
}

export interface TenantUpdate {
  nombre?: string;
  descripcion?: string;
  activo?: boolean;
}
