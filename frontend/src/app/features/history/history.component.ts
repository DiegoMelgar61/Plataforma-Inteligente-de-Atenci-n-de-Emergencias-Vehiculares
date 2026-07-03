import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { IncidentsService } from '../requests/incidents.service';
import { ReportsService } from './reports.service';
import { Incident } from '../../models';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="space-y-5 fade-in">
      <div>
        <h1 class="page-title">Historial de incidentes</h1>
        <p class="page-subtitle">Registro completo de emergencias atendidas</p>
      </div>

      <!-- Search & Filters -->
      <div class="surface p-3 flex flex-wrap items-center gap-3">
        <div class="relative flex-1 min-w-48">
          <input [(ngModel)]="search" class="input pl-8 py-2 text-sm" placeholder="Buscar por ID o tipo..." />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style="color: var(--text-muted);">/</span>
        </div>
        <select [(ngModel)]="filterEstado" class="input text-sm w-40">
          <option value="">Todos los estados</option>
          <option value="ATENDIDO">Atendidos</option>
          <option value="CANCELADO">Cancelados</option>
          <option value="INCIERTO">Inciertos</option>
        </select>
        <select [(ngModel)]="filterClasif" class="input text-sm w-40">
          <option value="">Todos los tipos</option>
          @for (c of clasifs; track c) {
            <option [value]="c">{{ c }}</option>
          }
        </select>
        @if (search || filterEstado || filterClasif) {
          <button (click)="clearFilters()" class="btn-ghost text-xs">Limpiar</button>
        }
        <div class="flex gap-2">
          <button (click)="exportar('xlsx')" [disabled]="exportando()" class="btn-ghost text-xs">
            {{ exportando() ? '...' : 'Excel' }}
          </button>
          <button (click)="exportar('pdf')" [disabled]="exportando()" class="btn-ghost text-xs">
            {{ exportando() ? '...' : 'PDF' }}
          </button>
        </div>
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-4 gap-3">
        @for (s of stats(); track s.label) {
          <div class="surface p-4 flex items-center gap-3">
            <div>
              <p class="text-xl font-bold" [style.color]="s.color">{{ s.value }}</p>
              <p class="text-xs" style="color: var(--text-muted);">{{ s.label }}</p>
            </div>
          </div>
        }
      </div>

      <!-- Table -->
      @if (loading()) {
        <div class="space-y-2">
          @for (_ of [1,2,3,4,5]; track $index) {
            <div class="h-14 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (filtered().length === 0) {
        <div class="surface p-16 text-center">
          <p class="text-sm" style="color: var(--text-muted);">Sin resultados para esta búsqueda</p>
        </div>
      } @else {
        <div class="table-wrap">
          <table class="w-full">
            <thead>
              <tr>
                <th>ID</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Análisis IA</th>
                <th>Fecha</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              @for (inc of filtered(); track inc.id_incidente) {
                <tr>
                  <td class="font-mono text-xs" style="color: var(--text-muted);">
                    #{{ inc.id_incidente }}
                  </td>
                  <td>
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-sm" style="color: var(--text-primary);">{{ inc.clasificacion }}</span>
                    </div>
                  </td>
                  <td>
                    <span [class]="'badge ' + estadoBadge(inc.estado)">{{ inc.estado.split('_').join(' ') }}</span>
                  </td>
                  <td>
                    <span [class]="'badge ' + prioridadBadge(inc.prioridad)">{{ inc.prioridad }}</span>
                  </td>
                  <td class="max-w-xs">
                    @if (inc.resumen_ia) {
                      <p class="text-xs truncate" style="color: var(--text-muted);">IA: {{ inc.resumen_ia }}</p>
                    } @else {
                      <span style="color: var(--text-muted);">—</span>
                    }
                  </td>
                  <td class="text-xs" style="color: var(--text-muted);">{{ formatDate(inc.fecha_creacion) }}</td>
                  <td>
                    <a [routerLink]="['/requests', inc.id_incidente]" class="text-xs" style="color: var(--accent);">Ver →</a>
                  </td>
                </tr>
              }
            </tbody>
          </table>
          <div class="px-4 py-3" style="border-top: 1px solid var(--border);">
            <p class="text-xs" style="color: var(--text-muted);">{{ filtered().length }} de {{ incidents().length }} registros</p>
          </div>
        </div>
      }
    </div>
  `,
})
export class HistoryComponent implements OnInit {
  private incidentsService = inject(IncidentsService);
  private reportsService = inject(ReportsService);

  loading = signal(true);
  exportando = signal(false);
  incidents = signal<Incident[]>([]);
  search = '';
  filterEstado = '';
  filterClasif = '';
  clasifs = ['BATERIA', 'LLANTA', 'CHOQUE', 'MOTOR', 'OTROS', 'INCIERTO'];

  filtered = computed(() => this.incidents().filter(inc => {
    const s = this.search.toLowerCase();
    return (!s || String(inc.id_incidente).includes(s) || inc.clasificacion.toLowerCase().includes(s))
      && (!this.filterEstado || inc.estado === this.filterEstado)
      && (!this.filterClasif || inc.clasificacion === this.filterClasif);
  }));

  stats = computed(() => {
    const list = this.incidents();
    return [
      { label: 'Total', value: list.length, color: 'var(--text-primary)' },
      { label: 'Atendidos', value: list.filter(i => i.estado === 'ATENDIDO').length, color: 'var(--success)' },
      { label: 'Cancelados', value: list.filter(i => i.estado === 'CANCELADO').length, color: 'var(--danger)' },
      { label: 'Con análisis IA', value: list.filter(i => !!i.resumen_ia).length, color: 'var(--accent)' },
    ];
  });

  ngOnInit(): void {
    this.loading.set(true);
    this.incidentsService.getAll().subscribe({
      next: (list) => { this.incidents.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  clearFilters(): void { this.search = ''; this.filterEstado = ''; this.filterClasif = ''; }

  exportar(formato: 'xlsx' | 'pdf'): void {
    this.exportando.set(true);
    this.reportsService
      .descargarIncidentes(formato, {
        estado: this.filterEstado || undefined,
        clasificacion: this.filterClasif || undefined,
      })
      .subscribe({
        next: (blob) => {
          const stamp = new Date().toISOString().slice(0, 16).replace(/[:T]/g, '');
          this.reportsService.guardarArchivo(blob, `reporte_incidentes_${stamp}.${formato}`);
          this.exportando.set(false);
        },
        error: () => this.exportando.set(false),
      });
  }

  classIcon(c: string): string {
    return { BATERIA: 'BA', LLANTA: 'LL', CHOQUE: 'CH', MOTOR: 'MO', OTROS: 'OT', INCIERTO: '?' }[c] || 'OT';
  }

  estadoBadge(e: string): string {
    const m: Record<string,string> = { ATENDIDO: 'badge-green', CANCELADO: 'badge-red', INCIERTO: 'badge-gray', PENDIENTE: 'badge-orange', CLASIFICADO: 'badge-blue' };
    return m[e] || 'badge-gray';
  }

  prioridadBadge(p: string): string {
    return { ALTA: 'badge-red', MEDIA: 'badge-amber', BAJA: 'badge-green' }[p] || 'badge-gray';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', year: '2-digit', hour: '2-digit', minute: '2-digit' });
  }
}
