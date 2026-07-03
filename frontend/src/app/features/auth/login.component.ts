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
    <div class="min-h-screen flex items-center justify-center p-6" style="background: var(--bg-base);">
      <div class="w-full max-w-[420px] fade-in rounded-[24px] p-10"
           style="background: var(--bg-surface); border: 1px solid var(--border); box-shadow: var(--shadow-card);">
        <div class="flex flex-col items-center text-center mb-8">
          <div class="w-16 h-16 rounded-[20px] flex items-center justify-center mb-5 text-white"
               style="background: var(--accent-gradient); box-shadow: var(--neon-glow);">
            <svg class="w-9 h-9" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M12 2L2 19h20L12 2zm0 4l7 13H5l7-13zm-1 5v4h2v-4h-2zm0 5v2h2v-2h-2z"/>
            </svg>
          </div>
          <p class="text-[13px] font-bold uppercase tracking-[0.22em]" style="color: var(--accent);">EmergVehicular</p>
          <h1 class="mt-3 text-[22px] font-bold leading-tight" style="color: var(--text-primary);">Iniciar sesión</h1>
          <p class="mt-1 text-[13px]" style="color: var(--text-muted);">Panel de operaciones</p>
        </div>

          @if (error()) {
            <div class="flex items-start gap-3 rounded-lg px-4 py-3 mb-5 text-sm fade-in"
                 style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); color: #fca5a5;">
              <svg class="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
                <path stroke-linecap="round" stroke-width="2" d="M12 8v4m0 4h.01"/>
              </svg>
              {{ error() }}
            </div>
          }

          <form (ngSubmit)="submit()" class="space-y-4">
            <div>
              <label class="block text-xs font-medium mb-2" style="color: var(--text-secondary);">
                Correo electrónico
              </label>
              <input
                type="email"
                [(ngModel)]="email"
                name="email"
                required
                class="input"
                placeholder="nombre@taller.com"
                [disabled]="loading()"
                autocomplete="email"
              />
            </div>
            <div>
              <label class="block text-xs font-medium mb-2" style="color: var(--text-secondary);">
                Contraseña
              </label>
              <div class="relative">
                <input
                  [type]="showPass() ? 'text' : 'password'"
                  [(ngModel)]="password"
                  name="password"
                  required
                  class="input pr-10"
                  placeholder="••••••••"
                  [disabled]="loading()"
                  autocomplete="current-password"
                />
                <button type="button" (click)="showPass.set(!showPass())"
                        class="absolute right-3 top-1/2 -translate-y-1/2 transition-colors"
                        style="color: var(--text-muted);">
                  @if (showPass()) {
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                    </svg>
                  } @else {
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>  
                  }
                </button>
              </div>
            </div>

            <button
              type="submit"
              class="btn-primary w-full py-3 text-sm font-semibold mt-2"
              [disabled]="loading() || !email || !password"
            >
              @if (loading()) {
                <svg class="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Verificando...
              } @else {
                Iniciar sesión
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
                </svg>
              }
            </button>
          </form>

          <p class="text-center text-xs mt-8" style="color: var(--text-muted);">
            Acceso exclusivo para cuentas con rol
            <span class="badge-blue ml-1">TALLER</span> o
            <span class="badge-purple ml-1">ADMIN</span>
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
  showPass = signal(false);

  features = [
    { icon: 'RT', title: 'Respuesta en tiempo real', desc: 'WebSocket para notificaciones instantáneas' },
    { icon: 'IA', title: 'Clasificación por IA', desc: 'Análisis automático de incidentes vehiculares' },
    { icon: 'MAP', title: 'Mapa de operaciones', desc: 'Seguimiento geográfico de técnicos' },
  ];

  submit(): void {
    if (!this.email || !this.password) return;
    this.loading.set(true);
    this.error.set(null);

    this.auth.login({ correo_electronico: this.email, contrasena: this.password }).subscribe({
      next: () => {
        if (!this.auth.hasAccess()) {
          this.auth.logout();
          this.error.set('Acceso denegado. Solo cuentas TALLER o ADMIN pueden ingresar.');
        } else {
          this.router.navigate(['/dashboard']);
        }
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Credenciales incorrectas. Verifica tu correo y contraseña.');
        this.loading.set(false);
      },
    });
  }
}
