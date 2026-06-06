import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DashboardStats } from '../../models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class StatsService {
  private http = inject(HttpClient);
  private api = environment.apiUrl;

  getDashboard(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.api}/stats/dashboard`);
  }
}
