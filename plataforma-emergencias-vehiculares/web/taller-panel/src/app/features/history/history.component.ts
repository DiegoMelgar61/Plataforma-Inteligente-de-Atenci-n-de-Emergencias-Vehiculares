import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { IncidentsService } from '../../core/services/incidents.service';
import { Incident } from '../../models';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div>
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Historial de incidentes</h1>
        <p class="text-gray-500 text-sm">Todos los incidentes atendidos por tu taller</p>
      </div>

      <!-- Search & Filter -->
      <div class="flex gap-3 mb-6">
        <div class="flex-1 relative">
          <input
            type="search"
            [(ngModel)]="search"
            class="input-field pl-9"
            placeholder="Buscar por ID o clasificación..."
          />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
        </div>
        <select [(ngModel)]="filterEstado" class="input-field w-44">
          <option value="">Todos los estados</option>
          <option value="ATENDIDO">Atendidos</option>
          <option value="CANCELADO">Cancelados</option>
          <option value="INCIERTO">Inciertos</option>
        </select>
        <select [(ngModel)]="filterClasificacion" class="input-field w-40">
          <option value="">Todas las clases</option>
          <option value="BATERIA">Batería</option>
          <option value="LLANTA">Llanta</option>
          <option value="CHOQUE">Choque</option>
          <option value="MOTOR">Motor</option>
          <option value="OTROS">Otros</option>
        </select>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="card text-center">
          <p class="text-2xl font-bold text-gray-700">{{ total() }}</p>
          <p class="text-xs text-gray-500 mt-1">Total</p>
        </div>
        <div class="card text-center">
          <p class="text-2xl font-bold text-green-600">{{ atendidos() }}</p>
          <p class="text-xs text-gray-500 mt-1">Atendidos</p>
        </div>
        <div class="card text-center">
          <p class="text-2xl font-bold text-red-500">{{ cancelados() }}</p>
          <p class="text-xs text-gray-500 mt-1">Cancelados</p>
        </div>
        <div class="card text-center">
          <p class="text-2xl font-bold text-blue-600">{{ conIA() }}</p>
          <p class="text-xs text-gray-500 mt-1">Con análisis IA</p>
        </div>
      </div>

      <!-- Table -->
      @if (loading()) {
        <div class="space-y-3">
          @for (_ of [1,2,3,4,5]; track $index) {
            <div class="h-16 bg-gray-100 rounded-xl animate-pulse"></div>
          }
        </div>
      } @else if (filtered().length === 0) {
        <div class="card text-center py-16">
          <div class="text-5xl mb-4">📜</div>
          <p class="text-gray-500">No se encontraron incidentes</p>
          @if (search || filterEstado || filterClasificacion) {
            <button (click)="clearFilters()" class="btn-secondary mt-4">Limpiar filtros</button>
          }
        </div>
      } @else {
        <div class="card p-0 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Tipo</th>
                  <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Estado</th>
                  <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Prioridad</th>
                  <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Análisis IA</th>
                  <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Fecha</th>
                  <th class="text-right py-3 px-4"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                @for (inc of filtered(); track inc.id_incidente) {
                  <tr class="hover:bg-gray-50 transition-colors">
                    <td class="py-3 px-4 font-mono text-xs text-gray-400">
                      #{{ inc.id_incidente.substring(0,8).toUpperCase() }}
                    </td>
                    <td class="py-3 px-4">
                      <span class="flex items-center gap-1.5">
                        {{ classIcon(inc.clasificacion) }}
                        <span class="font-medium text-gray-700">{{ inc.clasificacion }}</span>
                      </span>
                    </td>
                    <td class="py-3 px-4">
                      <span [class]="'badge ' + estadoBadge(inc.estado)">{{ inc.estado.split('_').join(' ') }}</span>
                    </td>
                    <td class="py-3 px-4">
                      <span [class]="priorityColor(inc.prioridad)">{{ inc.prioridad }}</span>
                    </td>
                    <td class="py-3 px-4 max-w-xs">
                      @if (inc.resumen_ia) {
                        <p class="text-gray-500 truncate text-xs">🤖 {{ inc.resumen_ia }}</p>
                      } @else {
                        <span class="text-gray-300 text-xs">—</span>
                      }
                    </td>
                    <td class="py-3 px-4 text-gray-400 text-xs">{{ formatDate(inc.fecha_creacion) }}</td>
                    <td class="py-3 px-4 text-right">
                      <a [routerLink]="['/requests', inc.id_incidente]"
                         class="text-blue-600 hover:underline text-xs">Ver →</a>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
          <div class="px-4 py-3 bg-gray-50 border-t border-gray-100 text-xs text-gray-400">
            Mostrando {{ filtered().length }} de {{ incidents().length }} registros
          </div>
        </div>
      }
    </div>
  `,
})
export class HistoryComponent implements OnInit {
  private incidentsService = inject(IncidentsService);

  loading = signal(true);
  incidents = signal<Incident[]>([]);
  search = '';
  filterEstado = '';
  filterClasificacion = '';

  total = computed(() => this.incidents().length);
  atendidos = computed(() => this.incidents().filter(i => i.estado === 'ATENDIDO').length);
  cancelados = computed(() => this.incidents().filter(i => i.estado === 'CANCELADO').length);
  conIA = computed(() => this.incidents().filter(i => !!i.resumen_ia).length);

  filtered = computed(() => {
    return this.incidents().filter(inc => {
      const matchSearch = !this.search ||
        inc.id_incidente.toLowerCase().includes(this.search.toLowerCase()) ||
        inc.clasificacion.toLowerCase().includes(this.search.toLowerCase());
      const matchEstado = !this.filterEstado || inc.estado === this.filterEstado;
      const matchClasif = !this.filterClasificacion || inc.clasificacion === this.filterClasificacion;
      return matchSearch && matchEstado && matchClasif;
    });
  });

  ngOnInit(): void {
    this.loading.set(true);
    this.incidentsService.getAll().subscribe({
      next: (list) => {
        // History = completed/cancelled
        const history = list.filter(i => ['ATENDIDO', 'CANCELADO', 'INCIERTO'].includes(i.estado));
        this.incidents.set(history.length > 0 ? history : list);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  clearFilters(): void {
    this.search = '';
    this.filterEstado = '';
    this.filterClasificacion = '';
  }

  classIcon(c: string): string {
    return { BATERIA: '🔋', LLANTA: '🔄', CHOQUE: '💥', MOTOR: '⚙️', OTROS: '🚗', INCIERTO: '❓' }[c] || '🚗';
  }

  estadoBadge(e: string): string {
    const map: Record<string, string> = {
      ATENDIDO: 'bg-green-100 text-green-700',
      CANCELADO: 'bg-red-100 text-red-700',
      INCIERTO: 'bg-gray-100 text-gray-600',
      PENDIENTE: 'bg-orange-100 text-orange-700',
      CLASIFICADO: 'bg-blue-100 text-blue-700',
    };
    return map[e] || 'bg-gray-100 text-gray-600';
  }

  priorityColor(p: string): string {
    return { ALTA: 'text-red-600 font-medium', MEDIA: 'text-amber-600', BAJA: 'text-green-600' }[p] || 'text-gray-500';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }
}
