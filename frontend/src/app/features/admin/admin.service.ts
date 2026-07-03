import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User, Taller, TallerCreate } from '../../models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AdminService {
  private http = inject(HttpClient);
  private api = environment.apiUrl;

  getUsers(rol?: string, activo?: boolean): Observable<User[]> {
    let params = new HttpParams();
    if (rol) params = params.set('rol', rol);
    if (activo !== undefined) params = params.set('activo', String(activo));
    return this.http.get<User[]>(`${this.api}/usuarios`, { params });
  }

  changeRole(id: number, rol: string): Observable<User> {
    return this.http.patch<User>(`${this.api}/usuarios/${id}/rol`, { rol });
  }

  toggleActive(id: number, activo: boolean): Observable<User> {
    return this.http.patch<User>(`${this.api}/usuarios/${id}/activo`, { activo });
  }

  getWorkshops(soloActivos = false): Observable<Taller[]> {
    const params = new HttpParams().set('solo_activos', String(soloActivos));
    return this.http.get<Taller[]>(`${this.api}/talleres`, { params });
  }

  createWorkshop(data: TallerCreate): Observable<Taller> {
    return this.http.post<Taller>(`${this.api}/talleres`, data);
  }

  updateWorkshop(id: number, data: Partial<TallerCreate & { activo: boolean }>): Observable<Taller> {
    return this.http.put<Taller>(`${this.api}/talleres/${id}`, data);
  }

  toggleWorkshop(id: number, activo: boolean): Observable<Taller> {
    return this.http.put<Taller>(`${this.api}/talleres/${id}`, { activo });
  }

  deleteWorkshop(id: number): Observable<void> {
    return this.http.delete<void>(`${this.api}/talleres/${id}`);
  }
}
