import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface BitacoraEntry {
  id_bitacora: string;
  id_usuario?: string | null;
  usuario_nombre?: string | null;
  id_tenant?: string | null;
  accion: string;
  entidad?: string | null;
  id_entidad?: string | null;
  descripcion?: string | null;
  ip?: string | null;
  fecha_creacion?: string | null;
}

export interface BitacoraFilters {
  accion?: string;
  entidad?: string;
  desde?: string;
  hasta?: string;
  limit?: number;
}

@Injectable({ providedIn: 'root' })
export class BitacoraService {
  private http = inject(HttpClient);
  private api = `${environment.apiUrl}/bitacora`;

  list(filters: BitacoraFilters = {}): Observable<BitacoraEntry[]> {
    let params = new HttpParams();
    if (filters.accion) params = params.set('accion', filters.accion);
    if (filters.entidad) params = params.set('entidad', filters.entidad);
    if (filters.desde) params = params.set('desde', filters.desde);
    if (filters.hasta) params = params.set('hasta', filters.hasta);
    params = params.set('limit', String(filters.limit ?? 300));
    return this.http.get<BitacoraEntry[]>(this.api, { params });
  }
}
