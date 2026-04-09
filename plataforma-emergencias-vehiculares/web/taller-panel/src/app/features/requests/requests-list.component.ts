import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { IncidentsService } from '../../core/services/incidents.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { Incident } from '../../models';

@Component({
  selector: 'app-requests-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div>
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Solicitudes de emergencia</h1>
          <p class="text-gray-500 text-sm">Incidentes vehiculares que requieren atención</p>
        </div>
        <button (click)="reload()" class="btn-secondary flex items-center gap-2">
          <span class="text-lg">🔄</span> Actualizar
        </button>
      </div>

      <!-- Filters -->
      <div class="flex gap-2 mb-6 flex-wrap">
        @for (f of filters; track f.value) {
          <button
            (click)="setFilter(f.value)"
            [class]="activeFilter() === f.value
              ? 'px-4 py-2 rounded-full text-sm font-medium bg-blue-600 text-white'
              : 'px-4 py-2 rounded-full text-sm font-medium bg-white border border-gray-200 text-gray-600 hover:border-blue-300'">
            {{ f.label }}
          </button>
        }
      </div>

      <!-- List -->
      @if (loading()) {
        <div class="space-y-3">
          @for (_ of [1,2,3,4,5]; track $index) {
            <div class="h-20 bg-gray-100 rounded-xl animate-pulse"></div>
          }
        </div>
      } @else if (filtered().length === 0) {
        <div class="card text-center py-16">
          <div class="text-5xl mb-4">📭</div>
          <p class="text-gray-500">No hay solicitudes {{ activeFilter() !== 'ALL' ? 'con este estado' : '' }}</p>
        </div>
      } @else {
        <div class="space-y-3">
          @for (inc of filtered(); track inc.id_incidente) {
            <a [routerLink]="['/requests', inc.id_incidente]"
               class="card flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer p-4">
              <!-- Priority indicator -->
              <div [class]="'w-1 h-16 rounded-full flex-shrink-0 ' + priorityBar(inc.prioridad)"></div>

              <!-- Icon -->
              <div [class]="'w-12 h-12 rounded-xl flex items-center justify-center text-xl flex-shrink-0 ' + iconBg(inc.clasificacion)">
                {{ classIcon(inc.clasificacion) }}
              </div>

              <!-- Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <h3 class="font-semibold text-gray-900">{{ inc.clasificacion }}</h3>
                  <span [class]="'badge ' + prioridadBadge(inc.prioridad)">{{ inc.prioridad }}</span>
                </div>
                <p class="text-xs text-gray-400"># {{ inc.id_incidente.substring(0,8).toUpperCase() }}</p>
                @if (inc.resumen_ia) {
                  <p class="text-sm text-gray-500 truncate mt-1">🤖 {{ inc.resumen_ia }}</p>
                }
              </div>

              <!-- Estado + fecha -->
              <div class="text-right flex-shrink-0">
                <span [class]="'badge block mb-1 ' + estadoBadge(inc.estado)">
                  {{ inc.estado.split('_').join(' ') }}
                </span>
                <p class="text-xs text-gray-400">{{ formatDate(inc.fecha_creacion) }}</p>
              </div>

              <svg class="w-5 h-5 text-gray-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </a>
          }
        </div>
      }
    </div>
  `,
})
export class RequestsListComponent implements OnInit {
  private incidentsService = inject(IncidentsService);
  private ws = inject(WebSocketService);

  loading = signal(true);
  incidents = signal<Incident[]>([]);
  activeFilter = signal('ALL');

  filters = [
    { label: 'Todos', value: 'ALL' },
    { label: 'Clasificados', value: 'CLASIFICADO' },
    { label: 'Pendientes', value: 'PENDIENTE' },
    { label: 'Asignados', value: 'ASIGNADO' },
    { label: 'En camino', value: 'EN_CAMINO' },
    { label: 'En proceso', value: 'EN_PROCESO' },
    { label: 'Atendidos', value: 'ATENDIDO' },
  ];

  filtered = () => {
    const f = this.activeFilter();
    const list = this.incidents();
    return f === 'ALL' ? list : list.filter(i => i.estado === f);
  };

  ngOnInit(): void {
    this.reload();
    this.ws.messages$.subscribe(() => this.reload());
  }

  reload(): void {
    this.loading.set(true);
    this.incidentsService.getAll().subscribe({
      next: (list) => { this.incidents.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  setFilter(v: string): void { this.activeFilter.set(v); }

  priorityBar(p: string): string {
    return { ALTA: 'bg-red-500', MEDIA: 'bg-amber-400', BAJA: 'bg-green-400' }[p] || 'bg-gray-300';
  }

  prioridadBadge(p: string): string {
    return { ALTA: 'bg-red-100 text-red-700', MEDIA: 'bg-amber-100 text-amber-700', BAJA: 'bg-green-100 text-green-700' }[p] || 'bg-gray-100 text-gray-500';
  }

  estadoBadge(e: string): string {
    const map: Record<string, string> = {
      PENDIENTE: 'bg-orange-100 text-orange-700',
      EN_PROCESO_IA: 'bg-indigo-100 text-indigo-700',
      CLASIFICADO: 'bg-blue-100 text-blue-700',
      ASIGNADO: 'bg-purple-100 text-purple-700',
      EN_CAMINO: 'bg-amber-100 text-amber-700',
      EN_PROCESO: 'bg-teal-100 text-teal-700',
      ATENDIDO: 'bg-green-100 text-green-700',
      CANCELADO: 'bg-red-100 text-red-700',
    };
    return map[e] || 'bg-gray-100 text-gray-600';
  }

  classIcon(c: string): string {
    return { BATERIA: '🔋', LLANTA: '🔄', CHOQUE: '💥', MOTOR: '⚙️', OTROS: '🚗', INCIERTO: '❓' }[c] || '🚗';
  }

  iconBg(c: string): string {
    return { BATERIA: 'bg-yellow-100', LLANTA: 'bg-blue-100', CHOQUE: 'bg-red-100', MOTOR: 'bg-gray-100', OTROS: 'bg-purple-100', INCIERTO: 'bg-gray-100' }[c] || 'bg-gray-100';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  }
}
