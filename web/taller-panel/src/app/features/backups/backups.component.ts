import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BackupsService } from '../../core/services/backups.service';

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

        <!-- Programación (decorativa) -->
        <div class="surface p-6" style="opacity: 0.85;">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold" style="color: var(--text-primary);">Programación automática</h2>
            <span class="badge badge-gray" style="font-size:10px;">Próximamente</span>
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
            <input type="checkbox" disabled class="w-10" />
          </div>

          <div class="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label class="block text-xs mb-1" style="color: var(--text-muted);">Frecuencia</label>
              <select disabled class="input text-sm">
                <option>Diario</option>
              </select>
            </div>
            <div>
              <label class="block text-xs mb-1" style="color: var(--text-muted);">Hora de ejecución</label>
              <input type="time" value="02:00" disabled class="input text-sm" />
            </div>
          </div>
          <div class="mb-4">
            <label class="block text-xs mb-1" style="color: var(--text-muted);">Política de retención</label>
            <select disabled class="input text-sm">
              <option>Conservar últimos 7 días</option>
            </select>
          </div>

          <button disabled class="btn-ghost w-full" style="cursor: not-allowed;">Guardar configuración</button>
        </div>
      </div>
    </div>
  `,
})
export class BackupsComponent {
  private backupsService = inject(BackupsService);

  descargando = signal(false);
  error = signal<string | null>(null);

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
