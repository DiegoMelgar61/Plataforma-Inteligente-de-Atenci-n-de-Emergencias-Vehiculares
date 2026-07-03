import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface PanelIa {
  titulo: string;
  metrica: string;
  tipo: 'bar' | 'line' | 'pie' | 'doughnut';
  periodo: string;
  labels: string[];
  series: { label: string; data: number[] }[];
}

export interface DashboardIa {
  titulo: string;
  orden: string;
  origen: string;
  paneles: PanelIa[];
}

@Injectable({ providedIn: 'root' })
export class DashboardsIaService {
  private http = inject(HttpClient);
  private api = `${environment.apiUrl}/dashboards-ia`;

  generar(form: FormData): Observable<DashboardIa> {
    return this.http.post<DashboardIa>(`${this.api}/generar`, form);
  }
}
