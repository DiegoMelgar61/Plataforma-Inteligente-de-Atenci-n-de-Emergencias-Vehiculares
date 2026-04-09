import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { LoginRequest, LoginResponse, User } from '../../models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  private _token = signal<string | null>(localStorage.getItem('token'));
  private _user = signal<User | null>(this.parseUser());

  readonly token = this._token.asReadonly();
  readonly user = this._user.asReadonly();
  readonly isAuthenticated = computed(() => !!this._token());

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiUrl}/auth/login`, credentials).pipe(
      tap((res) => {
        localStorage.setItem('token', res.access_token);
        this._token.set(res.access_token);
        const user = this.decodeToken(res.access_token);
        if (user) {
          localStorage.setItem('user', JSON.stringify(user));
          this._user.set(user);
        }
      })
    );
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this._token.set(null);
    this._user.set(null);
    this.router.navigate(['/login']);
  }

  isTaller(): boolean {
    return this._user()?.rol === 'TALLER';
  }

  private parseUser(): User | null {
    try {
      const u = localStorage.getItem('user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  }

  private decodeToken(token: string): User | null {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        id_usuario: payload.sub || '',
        correo_electronico: payload.email || '',
        nombre_completo: payload.nombre || payload.nombre_completo || '',
        rol: (payload.rol as User['rol']) || 'TALLER',
        activo: true,
      };
    } catch {
      return null;
    }
  }
}
