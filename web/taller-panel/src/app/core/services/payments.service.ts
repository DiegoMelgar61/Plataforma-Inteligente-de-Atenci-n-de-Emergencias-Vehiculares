import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Payment, PaymentStats } from '../../models/payment.model';

interface FiltrosPago {
  estado?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
}

@Injectable({ providedIn: 'root' })
export class PaymentsService {
  private http = inject(HttpClient);
  private api = `${environment.apiUrl}/payments`;

  listar(filtros?: FiltrosPago): Observable<Payment[]> {
    let params = new HttpParams();
    if (filtros?.estado) params = params.set('estado', filtros.estado);
    if (filtros?.fecha_desde) params = params.set('fecha_desde', filtros.fecha_desde);
    if (filtros?.fecha_hasta) params = params.set('fecha_hasta', filtros.fecha_hasta);
    return this.http.get<Payment[]>(this.api, { params });
  }

  obtener(idPago: string): Observable<Payment> {
    return this.http.get<Payment>(`${this.api}/${idPago}`);
  }

  confirmar(idPago: string): Observable<Payment> {
    return this.http.post<Payment>(`${this.api}/${idPago}/confirm`, {});
  }

  rechazar(idPago: string, motivo: string): Observable<Payment> {
    return this.http.post<Payment>(`${this.api}/${idPago}/reject`, { motivo_rechazo: motivo });
  }

  obtenerStats(): Observable<PaymentStats> {
    return this.http.get<PaymentStats>(`${this.api}/stats`);
  }
}
