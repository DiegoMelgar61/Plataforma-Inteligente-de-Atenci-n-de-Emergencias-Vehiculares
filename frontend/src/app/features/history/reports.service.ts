import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ReporteIncidentesFiltros {
  estado?: string;
  clasificacion?: string;
  desde?: string;
  hasta?: string;
}

@Injectable({ providedIn: 'root' })
export class ReportsService {
  private http = inject(HttpClient);
  private api = `${environment.apiUrl}/reports`;

  /** Descarga el reporte de incidentes como Blob (xlsx o pdf). */
  descargarIncidentes(
    formato: 'xlsx' | 'pdf',
    filtros: ReporteIncidentesFiltros = {},
  ): Observable<Blob> {
    let params = new HttpParams().set('formato', formato);
    if (filtros.estado) params = params.set('estado', filtros.estado);
    if (filtros.clasificacion) params = params.set('clasificacion', filtros.clasificacion);
    if (filtros.desde) params = params.set('desde', filtros.desde);
    if (filtros.hasta) params = params.set('hasta', filtros.hasta);
    return this.http.get(`${this.api}/incidents`, {
      params,
      responseType: 'blob',
    });
  }

  /** Dispara la descarga de un Blob en el navegador. */
  guardarArchivo(blob: Blob, nombre: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}
