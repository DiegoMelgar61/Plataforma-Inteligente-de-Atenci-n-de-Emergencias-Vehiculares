import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Asignacion, CotizacionDetalle, Incident, QuotationRequest } from '../../models';
import { environment } from '../../../environments/environment';

interface AssignRequest { id_tecnico?: number; }

@Injectable({ providedIn: 'root' })
export class IncidentsService {
  private http = inject(HttpClient);
  private api = environment.apiUrl;

  getAll(estado?: string): Observable<Incident[]> {
    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);
    return this.http.get<Incident[]>(`${this.api}/incidents`, { params });
  }

  getById(id: number): Observable<Incident> {
    return this.http.get<Incident>(`${this.api}/incidents/${id}`);
  }

  getPending(): Observable<Incident[]> {
    return this.http.get<Incident[]>(`${this.api}/incidents?estado=CLASIFICADO`);
  }

  getAssignedToTaller(): Observable<Asignacion[]> {
    return this.http.get<Asignacion[]>(`${this.api}/assignments/my`);
  }

  assign(incidentId: number, body: AssignRequest): Observable<Asignacion> {
    return this.http.post<Asignacion>(
      `${this.api}/assignments/incidents/${incidentId}/assign`,
      body
    );
  }

  updateStatus(id: number, estado: string, notas?: string): Observable<Incident> {
    return this.http.patch<Incident>(`${this.api}/incidents/${id}/estado`, {
      estado,
      notas,
    });
  }

  rejectAssignment(incidentId: number, motivo: string): Observable<any> {
    return this.http.post(`${this.api}/assignments/incidents/${incidentId}/reject`, {
      motivo_rechazo: motivo,
    });
  }

  getQuotation(incidentId: number): Observable<CotizacionDetalle> {
    return this.http.get<CotizacionDetalle>(`${this.api}/assignments/incidents/${incidentId}/cotizacion`);
  }

  proposeQuotation(incidentId: number, body: QuotationRequest): Observable<CotizacionDetalle> {
    return this.http.post<CotizacionDetalle>(`${this.api}/assignments/incidents/${incidentId}/cotizacion`, body);
  }
}
