import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Incident, Asignacion, AssignRequest } from '../../models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class IncidentsService {
  private http = inject(HttpClient);
  private api = environment.apiUrl;

  getAll(estado?: string): Observable<Incident[]> {
    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);
    return this.http.get<Incident[]>(`${this.api}/incidents`, { params });
  }

  getById(id: string): Observable<Incident> {
    return this.http.get<Incident>(`${this.api}/incidents/${id}`);
  }

  getPending(): Observable<Incident[]> {
    return this.http.get<Incident[]>(`${this.api}/incidents?estado=CLASIFICADO`);
  }

  getAssignedToTaller(): Observable<Asignacion[]> {
    return this.http.get<Asignacion[]>(`${this.api}/assignments/my`);
  }

  assign(incidentId: string, body: AssignRequest): Observable<Asignacion> {
    return this.http.post<Asignacion>(
      `${this.api}/assignments/incidents/${incidentId}/assign`,
      body
    );
  }

  updateStatus(id: string, estado: string, notas?: string): Observable<Incident> {
    return this.http.patch<Incident>(`${this.api}/incidents/${id}/estado`, {
      estado,
      notas,
    });
  }

  rejectAssignment(incidentId: string, motivo: string): Observable<any> {
    return this.http.post(`${this.api}/assignments/incidents/${incidentId}/reject`, {
      motivo_rechazo: motivo,
    });
  }
}
