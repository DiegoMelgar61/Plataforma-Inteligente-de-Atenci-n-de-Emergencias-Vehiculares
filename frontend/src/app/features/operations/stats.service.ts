import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DashboardStats } from '../../models';
import { environment } from '../../../environments/environment';

export interface ZonaIncidente {
  lat: number;
  lon: number;
  total: number;
  porcentaje: number;
}

@Injectable({ providedIn: 'root' })
export class StatsService {
  private http = inject(HttpClient);
  private api = environment.apiUrl;

  getDashboard(idTenant?: number): Observable<DashboardStats> {
    let params = new HttpParams();
    if (idTenant) params = params.set('id_tenant', String(idTenant));
    return this.http.get<DashboardStats>(`${this.api}/stats/dashboard`, { params });
  }

  getZonas(idTenant?: number): Observable<ZonaIncidente[]> {
    let params = new HttpParams();
    if (idTenant) params = params.set('id_tenant', String(idTenant));
    return this.http.get<ZonaIncidente[]>(`${this.api}/stats/zonas`, { params });
  }
}
