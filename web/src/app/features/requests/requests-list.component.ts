import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { IncidentsService } from './incidents.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { NotificationStore } from '../notifications/notification-store.service';
import { Incident } from '../../models';

@Component({
  selector: 'app-requests-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="space-y-5 fade-in">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">Solicitudes de emergencia</h1>
          <p class="page-subtitle">{{ filtered().length }} incidentes · Actualización en tiempo real</p>
        </div>
        <button (click)="reload()" class="btn-ghost text-xs">Actualizar</button>
      </div>

      <!-- Filters -->
      <div class="surface p-3 flex flex-wrap items-center gap-3">
        <div class="relative flex-1 min-w-48">
          <input [(ngModel)]="search" class="input pl-8 py-2 text-sm" placeholder="Buscar por ID o tipo..." />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style="color: var(--text-muted);">/</span>
        </div>
        <div class="flex flex-wrap gap-1.5">
          @for (f of filters; track f.value) {
            <button (click)="activeFilter.set(f.value)"
                    [class]="'filter-tab ' + (activeFilter() === f.value ? 'active' : '')">
              {{ f.label }}
            </button>
          }
        </div>
      </div>

      <!-- List -->
      @if (loading()) {
        <div class="space-y-2">
          @for (_ of [1,2,3,4,5]; track $index) {
            <div class="h-20 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (filtered().length === 0) {
        <div class="surface p-16 text-center">
          <p class="font-medium text-sm" style="color: var(--text-secondary);">Sin solicitudes</p>
          <p class="text-xs mt-1" style="color: var(--text-muted);">
            {{ activeFilter() !== 'ALL' ? 'Prueba con otro filtro' : 'No hay incidentes registrados' }}
          </p>
        </div>
      } @else {
        <div class="space-y-2">
          @for (inc of filtered(); track inc.id_incidente) {
            <a [routerLink]="['/requests', inc.id_incidente]"
               class="surface flex items-center gap-4 p-4 hover:border-blue-500/30 transition-all group cursor-pointer"
               style="display: flex; text-decoration: none;">
              <!-- Priority bar -->
              <div class="w-0.5 h-12 rounded-full flex-shrink-0" [class]="priorityBar(inc.prioridad)"></div>

              <!-- Icon -->
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
                   [style]="iconStyle(inc.clasificacion)">
                {{ classIcon(inc.clasificacion) }}
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-0.5">
                  <span class="text-sm font-semibold" style="color: var(--text-primary);">{{ inc.clasificacion }}</span>
                  <span [class]="'badge text-xs ' + prioridadBadge(inc.prioridad)">{{ inc.prioridad }}</span>
                </div>
                <p class="text-xs font-mono" style="color: var(--text-muted);">#{{ inc.id_incidente.substring(0,8).toUpperCase() }}</p>
                @if (inc.resumen_ia) {
                  <p class="text-xs mt-1 truncate max-w-md" style="color: var(--text-muted);">IA: {{ inc.resumen_ia }}</p>
                }
              </div>

              <!-- Right side -->
              <div class="flex items-center gap-3 flex-shrink-0">
                <div class="text-right hidden sm:block">
                  <span [class]="'badge ' + estadoBadge(inc.estado)">{{ inc.estado.split('_').join(' ') }}</span>
                  <p class="text-xs mt-1" style="color: var(--text-muted);">{{ formatDate(inc.fecha_creacion) }}</p>
                </div>
                <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--text-muted);">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </div>
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
  private notifStore = inject(NotificationStore);

  loading = signal(true);
  incidents = signal<Incident[]>([]);
  activeFilter = signal('ALL');
  search = '';

  filters = [
    { label: 'Todos', value: 'ALL' },
    { label: 'Clasificados', value: 'CLASIFICADO' },
    { label: 'Pendientes', value: 'PENDIENTE' },
    { label: 'Asignados', value: 'ASIGNADO' },
    { label: 'En camino', value: 'EN_CAMINO' },
    { label: 'En proceso', value: 'EN_PROCESO' },
    { label: 'Atendidos', value: 'ATENDIDO' },
  ];

  filtered = computed(() => {
    const f = this.activeFilter();
    const s = this.search.toLowerCase();
    return this.incidents()
      .filter(i => f === 'ALL' || i.estado === f)
      .filter(i => !s || i.clasificacion.toLowerCase().includes(s) || i.id_incidente.toLowerCase().includes(s));
  });

  ngOnInit(): void {
    this.reload();
    this.ws.messages$.subscribe((msg) => {
      this.notifStore.push(msg.data?.message || 'Nuevo incidente actualizado', 'info');
      this.reload();
    });
  }

  reload(): void {
    this.loading.set(true);
    this.incidentsService.getAll().subscribe({
      next: (list) => { this.incidents.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  priorityBar(p: string): string {
    return { ALTA: 'bg-red-500', MEDIA: 'bg-amber-400', BAJA: 'bg-green-500' }[p] || 'bg-gray-600';
  }

  prioridadBadge(p: string): string {
    return { ALTA: 'badge-red', MEDIA: 'badge-amber', BAJA: 'badge-green' }[p] || 'badge-gray';
  }

  estadoBadge(e: string): string {
    const m: Record<string,string> = {
      PENDIENTE: 'badge-orange', EN_PROCESO_IA: 'badge-purple', CLASIFICADO: 'badge-blue',
      ASIGNADO: 'badge-purple', EN_CAMINO: 'badge-amber', EN_PROCESO: 'badge-teal',
      ATENDIDO: 'badge-green', CANCELADO: 'badge-red',
    };
    return m[e] || 'badge-gray';
  }

  classIcon(c: string): string {
    return { BATERIA: 'BA', LLANTA: 'LL', CHOQUE: 'CH', MOTOR: 'MO', OTROS: 'OT', INCIERTO: '?' }[c] || 'OT';
  }

  iconStyle(c: string): string {
    const styles: Record<string,string> = {
      BATERIA: 'background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2)',
      LLANTA: 'background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2)',
      CHOQUE: 'background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2)',
      MOTOR: 'background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.2)',
      OTROS: 'background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2)',
      INCIERTO: 'background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.2)',
    };
    return styles[c] || 'background:rgba(100,116,139,0.1);';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  }
}
