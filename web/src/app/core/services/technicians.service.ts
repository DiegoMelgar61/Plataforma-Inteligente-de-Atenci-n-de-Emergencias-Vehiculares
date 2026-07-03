import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Tecnico, TecnicoCreate, TecnicoWithUserCreate } from '../../models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class TechniciansService {
  private http = inject(HttpClient);
  private api = environment.apiUrl;

  getAll(): Observable<Tecnico[]> {
    return this.http.get<Tecnico[]>(`${this.api}/tecnicos`);
  }

  create(tecnico: TecnicoCreate): Observable<Tecnico> {
    return this.http.post<Tecnico>(`${this.api}/tecnicos`, tecnico);
  }

  createWithUser(tecnico: TecnicoWithUserCreate): Observable<Tecnico> {
    return this.http.post<Tecnico>(`${this.api}/tecnicos/crear-con-usuario`, tecnico);
  }

  update(id: string, tecnico: Partial<TecnicoCreate>): Observable<Tecnico> {
    return this.http.put<Tecnico>(`${this.api}/tecnicos/${id}`, tecnico);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.api}/tecnicos/${id}`);
  }

  toggleDisponible(id: string, disponible: boolean): Observable<Tecnico> {
    return this.http.put<Tecnico>(`${this.api}/tecnicos/${id}`, { disponible });
  }
}
