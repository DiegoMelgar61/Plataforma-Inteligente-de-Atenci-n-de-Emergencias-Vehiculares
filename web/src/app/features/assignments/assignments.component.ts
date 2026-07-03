import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { IncidentsService } from '../requests/incidents.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { AuthService } from '../../core/services/auth.service';
import { Asignacion } from '../../models';

@Component({
  selector: 'app-assignments',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="space-y-5 fade-in">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">Mis asignaciones</h1>
          <p class="page-subtitle">Incidentes aceptados por tu taller</p>
        </div>
        <button (click)="reload()" class="btn-ghost text-xs">Actualizar</button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="stat-card">
          <div class="stat-icon">A</div>
          <div>
            <p class="stat-label">Total asignados</p>
            <p class="stat-value">{{ total() }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">R</div>
          <div>
            <p class="stat-label">En camino</p>
            <p class="stat-value" style="color:var(--warning);">{{ enCamino() }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">OK</div>
          <div>
            <p class="stat-label">Atendidos</p>
            <p class="stat-value" style="color:var(--success);">{{ atendidos() }}</p>
          </div>
        </div>
      </div>

      <!-- List -->
      @if (loading()) {
        <div class="space-y-3">
          @for (_ of [1,2,3]; track $index) {
            <div class="h-28 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (assignments().length === 0) {
        <div class="surface p-16 text-center">
          <p class="text-sm font-medium" style="color: var(--text-secondary);">Sin asignaciones activas</p>
          <p class="text-xs mt-1 mb-4" style="color: var(--text-muted);">Las solicitudes que aceptes aparecerán aquí</p>
          <a routerLink="/requests" class="btn-primary text-sm inline-flex">Ver solicitudes →</a>
        </div>
      } @else {
        <div class="space-y-3">
          @for (a of assignments(); track a.id_asignacion) {
            <div class="surface p-5">
              <div class="flex items-start gap-4">
                <div class="w-11 h-11 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                     style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.2);">
                  {{ classIcon(a.incidente?.clasificacion || 'OTROS') }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1.5">
                    <h3 class="text-sm font-semibold" style="color: var(--text-primary);">
                      {{ a.incidente?.clasificacion || 'Incidente' }}
                    </h3>
                    @if (a.incidente) {
                      <span [class]="'badge ' + estadoBadge(a.incidente.estado)">
                        {{ a.incidente.estado.split('_').join(' ') }}
                      </span>
                    }
                    @if (a.incidente?.prioridad) {
                      <span [class]="'badge ' + prioridadBadge(a.incidente!.prioridad)">{{ a.incidente!.prioridad }}</span>
                    }
                  </div>
                  <p class="text-xs font-mono mb-2" style="color: var(--text-muted);">
                    #{{ a.id_incidente.substring(0,8).toUpperCase() }}
                  </p>
                  <div class="flex flex-wrap items-center gap-3 text-xs" style="color: var(--text-muted);">
                    <span>{{ formatDate(a.fecha_asignacion) }}</span>
                    @if (a.tecnico) {
                      <span>Técnico: {{ a.tecnico.nombre_completo }}</span>
                    }
                  </div>
                  @if (a.incidente?.resumen_ia) {
                    <p class="text-xs mt-2 line-clamp-2" style="color: var(--text-muted);">
                      IA: {{ a.incidente!.resumen_ia }}
                    </p>
                  }
                </div>
                <a [routerLink]="['/requests', a.id_incidente]" class="btn-ghost text-xs flex-shrink-0">
                  Ver detalle →
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
  private auth = inject(AuthService);

  loading = signal(true);
  assignments = signal<Asignacion[]>([]);

  total = computed(() => this.assignments().length);
  enCamino = computed(() => this.assignments().filter(a => a.incidente?.estado === 'EN_CAMINO').length);
  atendidos = computed(() => this.assignments().filter(a => a.incidente?.estado === 'ATENDIDO').length);

  ngOnInit(): void { this.reload(); this.ws.messages$.subscribe(() => this.reload()); }

  reload(): void {
    if (!this.auth.isTaller()) {
      this.loading.set(false);
      return;
    }
    this.loading.set(true);
    this.incidentsService.getAssignedToTaller().subscribe({
      next: (list) => { this.assignments.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  classIcon(c: string): string {
    return { BATERIA: 'BA', LLANTA: 'LL', CHOQUE: 'CH', MOTOR: 'MO', OTROS: 'OT', INCIERTO: '?' }[c] || 'OT';
  }

  estadoBadge(e: string): string {
    const m: Record<string,string> = { ASIGNADO: 'badge-purple', EN_CAMINO: 'badge-amber', EN_PROCESO: 'badge-teal', ATENDIDO: 'badge-green' };
    return m[e] || 'badge-gray';
  }

  prioridadBadge(p: string): string {
    return { ALTA: 'badge-red', MEDIA: 'badge-amber', BAJA: 'badge-green' }[p] || 'badge-gray';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  }
}
