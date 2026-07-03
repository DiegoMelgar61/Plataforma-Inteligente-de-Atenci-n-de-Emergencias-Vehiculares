import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BackupsService } from './backups.service';

@Component({
  selector: 'app-backups',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-5 fade-in">
      <div>
        <h1 class="page-title">Gestión de copias de seguridad</h1>
        <p class="page-subtitle">Protege la base de datos mediante respaldos manuales o programados</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- Extracción manual (funcional) -->
        <div class="surface p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold" style="color: var(--text-primary);">Extracción manual</h2>
            <span class="badge badge-blue" style="font-size:10px;">Inmediato</span>
          </div>
          <p class="text-sm mb-6" style="color: var(--text-muted); line-height: 1.7;">
            Descarga un archivo <strong>.sql</strong> con el estado de los datos en este momento.
            Recomendado antes de actualizaciones de versión o mantenimientos.
          </p>
          @if (error()) {
            <div class="text-xs rounded-lg px-3 py-2 mb-3"
                 style="background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.2);">
              {{ error() }}
            </div>
          }
          <button (click)="descargar()" [disabled]="descargando()" class="btn-primary w-full">
            {{ descargando() ? 'Generando respaldo...' : 'Descargar ahora' }}
          </button>
        </div>

        <!-- Programación automática (solo visual) -->
        <div class="surface p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold" style="color: var(--text-primary);">Programación automática</h2>
            <span class="badge badge-amber" style="font-size:10px;">Cron Job</span>
          </div>
          <p class="text-sm mb-5" style="color: var(--text-muted); line-height: 1.7;">
            Configura una tarea para generar respaldos automáticos sin intervención manual.
          </p>

          <div class="rounded-lg p-3 mb-4 flex items-center justify-between"
               style="background: var(--bg-elevated); border: 1px solid var(--border);">
            <div>
              <p class="text-sm font-medium" style="color: var(--text-secondary);">Estado del servicio</p>
              <p class="text-xs" style="color: var(--text-muted);">Activa o pausa las copias programadas.</p>
            </div>
            <button type="button" (click)="servicioActivo.set(!servicioActivo())"
                    class="relative inline-flex items-center rounded-full transition-colors"
                    [style.background]="servicioActivo() ? 'var(--success)' : 'var(--border-strong)'"
                    style="width: 44px; height: 24px;">
              <span class="inline-block rounded-full bg-white transition-transform"
                    [style.transform]="servicioActivo() ? 'translateX(22px)' : 'translateX(2px)'"
                    style="width: 20px; height: 20px;"></span>
            </button>
          </div>

          <div class="grid grid-cols-2 gap-3 mb-3"
               [style.opacity]="servicioActivo() ? '1' : '0.5'"
               [style.pointer-events]="servicioActivo() ? 'auto' : 'none'">
            <div>
              <label class="block text-xs mb-1" style="color: var(--text-muted);">Frecuencia</label>
              <select [(ngModel)]="frecuencia" class="input text-sm">
                <option value="Diario">Diario</option>
                <option value="Semanal">Semanal</option>
                <option value="Mensual">Mensual</option>
              </select>
            </div>
            <div>
              <label class="block text-xs mb-1" style="color: var(--text-muted);">Hora de ejecución</label>
              <input type="time" [(ngModel)]="hora" class="input text-sm" />
            </div>
          </div>
          <div class="mb-4"
               [style.opacity]="servicioActivo() ? '1' : '0.5'"
               [style.pointer-events]="servicioActivo() ? 'auto' : 'none'">
            <label class="block text-xs mb-1" style="color: var(--text-muted);">Política de retención</label>
            <select [(ngModel)]="retencion" class="input text-sm">
              <option value="7">Conservar últimos 7 días</option>
              <option value="15">Conservar últimos 15 días</option>
              <option value="30">Conservar últimos 30 días</option>
            </select>
          </div>

          @if (configGuardada()) {
            <div class="text-xs rounded-lg px-3 py-2 mb-3"
                 style="background: rgba(16,185,129,0.1); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.2);">
              Configuración guardada.
            </div>
          }
          <button (click)="guardarConfig()" class="btn-primary w-full">Guardar configuración</button>
        </div>
      </div>
    </div>
  `,
})
export class BackupsComponent {
  private backupsService = inject(BackupsService);

  descargando = signal(false);
  error = signal<string | null>(null);

  // Programación automática — solo visual (no funcional).
  servicioActivo = signal(false);
  configGuardada = signal(false);
  frecuencia = 'Diario';
  hora = '02:00';
  retencion = '7';

  constructor() {
    const raw = localStorage.getItem('backup_config');
    if (raw) {
      try {
        const c = JSON.parse(raw);
        this.servicioActivo.set(!!c.activo);
        this.frecuencia = c.frecuencia ?? 'Diario';
        this.hora = c.hora ?? '02:00';
        this.retencion = c.retencion ?? '7';
      } catch { /* ignore */ }
    }
  }

  guardarConfig(): void {
    localStorage.setItem('backup_config', JSON.stringify({
      activo: this.servicioActivo(),
      frecuencia: this.frecuencia,
      hora: this.hora,
      retencion: this.retencion,
    }));
    this.configGuardada.set(true);
    setTimeout(() => this.configGuardada.set(false), 3000);
  }

  descargar(): void {
    this.descargando.set(true);
    this.error.set(null);
    this.backupsService.descargarManual().subscribe({
      next: (blob) => {
        const stamp = new Date().toISOString().slice(0, 16).replace(/[:T]/g, '');
        this.backupsService.guardarArchivo(blob, `backup_${stamp}.sql`);
        this.descargando.set(false);
      },
      error: () => {
        this.error.set('No se pudo generar el respaldo. Reintentá en unos segundos.');
        this.descargando.set(false);
      },
    });
  }
}
