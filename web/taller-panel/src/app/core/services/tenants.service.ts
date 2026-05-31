import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Tenant, TenantCreate, TenantUpdate } from '../../models/tenant.model';

@Injectable({ providedIn: 'root' })
export class TenantsService {
  private http = inject(HttpClient);
  private api = `${environment.apiUrl}/api/v1/tenants`;

  listar(soloActivos = false): Observable<Tenant[]> {
    const params = new HttpParams().set('solo_activos', String(soloActivos));
    return this.http.get<Tenant[]>(this.api, { params });
  }

  crear(datos: TenantCreate): Observable<Tenant> {
    return this.http.post<Tenant>(this.api, datos);
  }

  actualizar(id: string, datos: TenantUpdate): Observable<Tenant> {
    return this.http.patch<Tenant>(`${this.api}/${id}`, datos);
  }

  toggleActivo(id: string): Observable<Tenant> {
    return this.http.patch<Tenant>(`${this.api}/${id}/toggle-activo`, {});
  }
}
