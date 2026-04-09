import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { IncidentsService } from '../../core/services/incidents.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { Asignacion } from '../../models';

@Component({
  selector: 'app-assignments',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div>
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Mis asignaciones</h1>
          <p class="text-gray-500 text-sm">Incidentes asignados a tu taller</p>
        </div>
        <button (click)="reload()" class="btn-secondary flex items-center gap-2">
          <span>🔄</span> Actualizar
        </button>
      </div>

      <!-- Summary cards -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="card text-center">
          <p class="text-3xl font-bold text-purple-600">{{ total() }}</p>
          <p class="text-xs text-gray-500 mt-1">Total asignados</p>
        </div>
        <div class="card text-center">
          <p class="text-3xl font-bold text-amber-500">{{ enCamino() }}</p>
          <p class="text-xs text-gray-500 mt-1">En camino</p>
        </div>
        <div class="card text-center">
          <p class="text-3xl font-bold text-green-600">{{ atendidos() }}</p>
          <p class="text-xs text-gray-500 mt-1">Atendidos</p>
        </div>
      </div>

      <!-- Assignments list -->
      @if (loading()) {
        <div class="space-y-3">
          @for (_ of [1,2,3]; track $index) {
            <div class="h-24 bg-gray-100 rounded-xl animate-pulse"></div>
          }
        </div>
      } @else if (assignments().length === 0) {
        <div class="card text-center py-16">
          <div class="text-5xl mb-4">📋</div>
          <p class="text-gray-500 font-medium">Sin asignaciones activas</p>
          <p class="text-gray-400 text-sm mt-1">Las solicitudes que aceptes aparecerán aquí</p>
          <a routerLink="/requests" class="btn-primary mt-4 inline-block">Ver solicitudes</a>
        </div>
      } @else {
        <div class="space-y-4">
          @for (a of assignments(); track a.id_asignacion) {
            <div class="card">
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-xl flex-shrink-0">
                  {{ classIcon(a.incidente?.clasificacion || 'OTROS') }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <h3 class="font-semibold text-gray-900">{{ a.incidente?.clasificacion || 'Incidente' }}</h3>
                    @if (a.incidente) {
                      <span [class]="'badge ' + estadoBadge(a.incidente.estado)">
                        {{ a.incidente.estado.split('_').join(' ') }}
                      </span>
                    }
                  </div>
                  <p class="text-xs text-gray-400 font-mono mb-2"># {{ a.id_incidente.substring(0,8).toUpperCase() }}</p>
                  <div class="flex items-center gap-4 text-xs text-gray-500">
                    <span>📅 Asignado: {{ formatDate(a.fecha_asignacion) }}</span>
                    @if (a.tecnico) {
                      <span>👷 {{ a.tecnico.nombre_completo }}</span>
                    }
                    @if (a.incidente?.prioridad) {
                      <span [class]="priorityColor(a.incidente!.prioridad)">
                        ⚡ {{ a.incidente!.prioridad }}
                      </span>
                    }
                  </div>
                  @if (a.incidente?.resumen_ia) {
                    <p class="text-sm text-gray-500 mt-2 line-clamp-2">
                      🤖 {{ a.incidente!.resumen_ia }}
                    </p>
                  }
                </div>
                <a [routerLink]="['/requests', a.id_incidente]"
                   class="btn-secondary text-sm flex-shrink-0">
                  Ver detalle
                </a>
              </div>
            </div>
          }
        </div>
      }
    </div>
  `,
})
export class AssignmentsComponent implements OnInit {
  private incidentsService = inject(IncidentsService);
  private ws = inject(WebSocketService);

  loading = signal(true);
  assignments = signal<Asignacion[]>([]);

  total = computed(() => this.assignments().length);
  enCamino = computed(() => this.assignments().filter(a => a.incidente?.estado === 'EN_CAMINO').length);
  atendidos = computed(() => this.assignments().filter(a => a.incidente?.estado === 'ATENDIDO').length);

  ngOnInit(): void {
    this.reload();
    this.ws.messages$.subscribe(() => this.reload());
  }

  reload(): void {
    this.loading.set(true);
    this.incidentsService.getAssignedToTaller().subscribe({
      next: (list) => { this.assignments.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  classIcon(c: string): string {
    return { BATERIA: '🔋', LLANTA: '🔄', CHOQUE: '💥', MOTOR: '⚙️', OTROS: '🚗', INCIERTO: '❓' }[c] || '🚗';
  }

  estadoBadge(e: string): string {
    const map: Record<string, string> = {
      ASIGNADO: 'bg-purple-100 text-purple-700',
      EN_CAMINO: 'bg-amber-100 text-amber-700',
      EN_PROCESO: 'bg-teal-100 text-teal-700',
      ATENDIDO: 'bg-green-100 text-green-700',
    };
    return map[e] || 'bg-gray-100 text-gray-600';
  }

  priorityColor(p: string): string {
    return { ALTA: 'text-red-600 font-medium', MEDIA: 'text-amber-600', BAJA: 'text-green-600' }[p] || 'text-gray-500';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  }
}
