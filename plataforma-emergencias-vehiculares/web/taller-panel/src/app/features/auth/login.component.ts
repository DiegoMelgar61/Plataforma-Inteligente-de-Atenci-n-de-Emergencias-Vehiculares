import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="min-h-screen bg-gradient-to-br from-gray-900 to-blue-900 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-900">Panel de Taller</h1>
          <p class="text-gray-500 text-sm mt-1">Gestión de emergencias vehiculares</p>
        </div>

        <!-- Error -->
        @if (error()) {
          <div class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 mb-4 text-sm">
            {{ error() }}
          </div>
        }

        <!-- Form -->
        <form (ngSubmit)="submit()" #f="ngForm">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Correo electrónico</label>
            <input
              type="email"
              name="email"
              [(ngModel)]="email"
              required
              class="input-field"
              placeholder="taller@ejemplo.com"
              [disabled]="loading()"
            />
          </div>
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input
              type="password"
              name="password"
              [(ngModel)]="password"
              required
              class="input-field"
              placeholder="••••••••"
              [disabled]="loading()"
            />
          </div>
          <button
            type="submit"
            class="btn-primary w-full py-3 text-base"
            [disabled]="loading() || !email || !password"
          >
            @if (loading()) {
              <span class="flex items-center justify-center gap-2">
                <svg class="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Iniciando sesión...
              </span>
            } @else {
              Iniciar sesión
            }
          </button>
        </form>

        <p class="text-center text-xs text-gray-400 mt-6">
          Solo para cuentas con rol <strong>TALLER</strong>
        </p>
      </div>
    </div>
  `,
})
export class LoginComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  email = '';
  password = '';
  loading = signal(false);
  error = signal<string | null>(null);

  submit(): void {
    if (!this.email || !this.password) return;
    this.loading.set(true);
    this.error.set(null);

    this.auth.login({ correo_electronico: this.email, contrasena: this.password }).subscribe({
      next: () => {
        if (!this.auth.isTaller()) {
          this.auth.logout();
          this.error.set('Acceso denegado. Esta plataforma es exclusiva para talleres.');
        } else {
          this.router.navigate(['/dashboard']);
        }
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Credenciales incorrectas');
        this.loading.set(false);
      },
    });
  }
}
