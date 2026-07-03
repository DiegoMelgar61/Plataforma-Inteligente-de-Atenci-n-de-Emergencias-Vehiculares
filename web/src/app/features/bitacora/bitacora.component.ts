import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BitacoraService, BitacoraEntry } from '../../core/services/bitacora.service';

@Component({
  selector: 'app-bitacora',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-5 fade-in">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">Bitácora de auditoría</h1>
          <p class="page-subtitle">Registro de acciones de los usuarios</p>
        </div>
        <button (click)="reload()" class="btn-ghost text-xs">Actualizar</button>
      </div>

      <!-- Filters -->
      <div class="surface p-3 flex flex-wrap items-center gap-3">
        <div class="relative flex-1 min-w-48">
          <input [(ngModel)]="search" class="input pl-8 py-2 text-sm"
                 placeholder="Buscar por usuario, descripción o entidad..." />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style="color: var(--text-muted);">/</span>
        </div>
        <select [(ngModel)]="filterAccion" class="input text-sm w-48">
          <option value="">Todas las acciones</option>
          @for (a of acciones(); track a) {
            <option [value]="a">{{ a }}</option>
          }
        </select>
        @if (search || filterAccion) {
          <button (click)="clearFilters()" class="btn-ghost text-xs">Limpiar</button>
        }
      </div>

      @if (loading()) {
        <div class="space-y-2">
          @for (_ of [1,2,3,4,5,6]; track $index) {
            <div class="h-12 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (filtered().length === 0) {
        <div class="surface p-16 text-center">
          <p class="text-sm" style="color: var(--text-muted);">Sin registros para esta búsqueda</p>
        </div>
      } @else {
        <div class="table-wrap">
          <table class="w-full">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Usuario</th>
                <th>Acción</th>
                <th>Entidad</th>
                <th>Descripción</th>
                <th>IP</th>
              </tr>
            </thead>
            <tbody>
              @for (e of filtered(); track e.id_bitacora) {
                <tr>
                  <td class="text-xs whitespace-nowrap" style="color: var(--text-muted);">{{ formatDate(e.fecha_creacion) }}</td>
                  <td class="text-sm">{{ e.usuario_nombre || '—' }}</td>
                  <td><span class="badge badge-blue" style="font-size:10px;">{{ e.accion }}</span></td>
                  <td class="text-xs" style="color: var(--text-muted);">{{ e.entidad || '—' }}</td>
                  <td class="text-xs max-w-md" style="color: var(--text-secondary);">{{ e.descripcion || '—' }}</td>
                  <td class="text-xs font-mono" style="color: var(--text-muted);">{{ e.ip || '—' }}</td>
                </tr>
              }
            </tbody>
          </table>
          <div class="px-4 py-3" style="border-top: 1px solid var(--border);">
            <p class="text-xs" style="color: var(--text-muted);">{{ filtered().length }} de {{ entries().length }} registros</p>
          </div>
        </div>
      }
    </div>
  `,
})
export class BitacoraComponent implements OnInit {
  private bitacoraService = inject(BitacoraService);

  loading = signal(true);
  entries = signal<BitacoraEntry[]>([]);
  search = '';
  filterAccion = '';

  acciones = computed(() =>
    Array.from(new Set(this.entries().map(e => e.accion))).sort()
  );

  filtered = computed(() => {
    const s = this.search.toLowerCase();
    return this.entries().filter(e => {
      const matchSearch = !s
        || (e.usuario_nombre || '').toLowerCase().includes(s)
        || (e.descripcion || '').toLowerCase().includes(s)
        || (e.entidad || '').toLowerCase().includes(s)
        || e.accion.toLowerCase().includes(s);
      const matchAccion = !this.filterAccion || e.accion === this.filterAccion;
      return matchSearch && matchAccion;
    });
  });

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.bitacoraService.list({ limit: 300 }).subscribe({
      next: (list) => { this.entries.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  clearFilters(): void { this.search = ''; this.filterAccion = ''; }

  formatDate(d?: string | null): string {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('es-BO', {
      day: 'numeric', month: 'short', year: '2-digit', hour: '2-digit', minute: '2-digit',
    });
  }
}
