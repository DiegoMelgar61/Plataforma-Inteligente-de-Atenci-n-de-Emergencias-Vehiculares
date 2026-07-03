import { Component, inject, signal, OnInit, OnDestroy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { forkJoin, Subject } from 'rxjs';
import { throttleTime } from 'rxjs/operators';
import { IncidentsService } from '../requests/incidents.service';
import { TechniciansService } from '../technicians/technicians.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { AuthService } from '../../core/services/auth.service';
import { AdminService } from '../admin/admin.service';
import { NotificationStore } from '../../core/services/notification-store.service';
import { Incident, Tecnico, User, Taller } from '../../models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  styles: [`
    .dashboard-card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow-card);
      animation: dashboardSlideUp 620ms cubic-bezier(0.22,1,0.36,1) both;
    }
    .soft-row {
      border-radius: 16px;
      transition: background 200ms ease, transform 200ms ease;
    }
    .soft-row:hover { background: var(--bg-elevated); transform: translateX(3px); }
    .activity-bar {
      background: var(--accent-gradient);
      border-radius: 999px 999px 8px 8px;
      min-height: 12px;
      transition: transform 220ms ease, filter 220ms ease;
      box-shadow: 0 10px 22px rgba(124,92,255,0.18);
    }
    .activity-bar:hover { transform: translateY(-4px); filter: saturate(1.12); }
    .donut-progress {
      transition: stroke-dasharray 700ms cubic-bezier(0.22,1,0.36,1);
      filter: drop-shadow(0 8px 16px rgba(124,92,255,0.22));
    }
  `],
  template: `
    <div class="space-y-6">

      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">{{ greeting() }}, {{ firstName() }}</h1>
          <p class="page-subtitle">{{ today() }} · Todo está bajo control</p>
        </div>
        <button (click)="loadData()" class="btn-ghost text-xs gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Actualizar
        </button>
      </div>

      <!-- WS pill -->
      @if (ws.connected()) {
        <div class="flex items-center gap-2 w-fit px-3 py-1.5 rounded-full text-xs font-medium"
             style="background: var(--bg-elevated); border: 1px solid var(--border); color: var(--text-secondary);">
          <span class="rounded-full" style="width: 6px; height: 6px; background: var(--success);"></span>
          Tiempo real
        </div>
      }

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="stat-card" style="animation-delay: 40ms;">
          <div class="stat-icon absolute top-4 right-4" [innerHTML]="metricIcon('requests')"></div>
          <div class="pr-8 w-full">
            <p class="stat-label">Pendientes</p>
            <p class="stat-value">{{ pendientes() }}</p>
            <a routerLink="/requests" class="text-xs mt-4 block" style="color: var(--accent);">Ver →</a>
          </div>
        </div>
        <div class="stat-card" style="animation-delay: 90ms;">
          <div class="stat-icon absolute top-4 right-4" [innerHTML]="metricIcon('assignments')"></div>
          <div class="pr-8 w-full">
            <p class="stat-label">Asignados</p>
            <p class="stat-value">{{ asignados() }}</p>
            <a routerLink="/assignments" class="text-xs mt-4 block" style="color: var(--accent);">Ver →</a>
          </div>
        </div>
        <div class="stat-card" style="animation-delay: 140ms;">
          <div class="stat-icon absolute top-4 right-4" [innerHTML]="metricIcon('process')"></div>
          <div class="pr-8 w-full">
            <p class="stat-label">En proceso</p>
            <p class="stat-value">{{ enProceso() }}</p>
          </div>
        </div>
        <div class="stat-card" style="animation-delay: 190ms;">
          <div class="stat-icon absolute top-4 right-4" [innerHTML]="metricIcon('technicians')"></div>
          <div class="pr-8 w-full">
            <p class="stat-label">Técnicos disponibles</p>
            <p class="stat-value">
              {{ tecnicosDisponibles() }}
              <span class="text-base font-normal" style="color: var(--text-muted);">/{{ totalTecnicos() }}</span>
            </p>
            <a routerLink="/technicians" class="text-xs mt-4 block" style="color: var(--accent);">Gestionar →</a>
          </div>
        </div>
        @if (auth.isAdmin()) {
          <div class="stat-card" style="animation-delay: 240ms;">
            <div class="stat-icon absolute top-4 right-4" [innerHTML]="metricIcon('users')"></div>
            <div class="pr-8 w-full">
              <p class="stat-label">Total usuarios</p>
              <p class="stat-value">{{ totalUsers() }}</p>
              <a routerLink="/admin/users" class="text-xs mt-4 block" style="color: var(--accent);">Ver →</a>
            </div>
          </div>
          <div class="stat-card" style="animation-delay: 290ms;">
            <div class="stat-icon absolute top-4 right-4" [innerHTML]="metricIcon('workshops')"></div>
            <div class="pr-8 w-full">
              <p class="stat-label">Talleres activos</p>
              <p class="stat-value">{{ talleresActivos() }}</p>
              <a routerLink="/admin/workshops" class="text-xs mt-4 block" style="color: var(--accent);">Gestionar →</a>
            </div>
          </div>
          <div class="stat-card" style="animation-delay: 340ms;">
            <div class="stat-icon absolute top-4 right-4" [innerHTML]="metricIcon('done')"></div>
            <div class="pr-8 w-full">
              <p class="stat-label">Atendidos hoy</p>
              <p class="stat-value" style="color: var(--success);">{{ atendidos() }}</p>
            </div>
          </div>
          <div class="stat-card" style="animation-delay: 390ms;">
            <div class="stat-icon absolute top-4 right-4" [innerHTML]="metricIcon('cancelled')"></div>
            <div class="pr-8 w-full">
              <p class="stat-label">Cancelados</p>
              <p class="stat-value" style="color: var(--danger);">{{ cancelados() }}</p>
            </div>
          </div>
        }
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <div class="dashboard-card p-6 lg:col-span-3" style="animation-delay: 160ms;">
          <div class="flex items-start justify-between gap-4 mb-8">
            <div>
              <h2 class="text-base font-bold" style="color: var(--text-primary);">Actividad</h2>
              <p class="text-sm mt-1" style="color: var(--text-muted);">Incidentes agrupados por estado actual</p>
            </div>
            <span class="badge-purple">{{ incidents().length }} total</span>
          </div>
          <div class="flex items-end gap-3 sm:gap-5 h-56 px-1">
            @for (bar of statusBars(); track bar.label) {
              <div class="flex-1 h-full flex flex-col items-center justify-end gap-3 group" [title]="bar.label + ': ' + bar.value">
                <div class="relative w-full flex items-end justify-center" style="height: 180px;">
                  <div class="activity-bar w-full max-w-12" [style.height.%]="bar.height"></div>
                  <span class="absolute -top-7 opacity-0 group-hover:opacity-100 transition-opacity text-xs font-semibold px-2 py-1 rounded-full"
                        style="background: var(--text-primary); color: #fff;">{{ bar.value }}</span>
                </div>
                <span class="text-[10px] sm:text-xs font-semibold text-center uppercase tracking-wide" style="color: var(--text-muted);">{{ bar.short }}</span>
              </div>
            }
          </div>
        </div>

        <div class="dashboard-card p-6 lg:col-span-2 flex flex-col justify-between" style="animation-delay: 220ms;">
          <div>
            <h2 class="text-base font-bold" style="color: var(--text-primary);">Atención</h2>
            <p class="text-sm mt-1" style="color: var(--text-muted);">Porcentaje de incidentes atendidos</p>
          </div>
          <div class="flex items-center justify-center py-7">
            <div class="relative w-48 h-48">
              <svg class="w-full h-full -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="48" fill="none" stroke="var(--accent-soft)" stroke-width="14" />
                <circle class="donut-progress" cx="60" cy="60" r="48" fill="none" stroke="url(#attendedGradient)" stroke-width="14" stroke-linecap="round"
                        [attr.stroke-dasharray]="attendedDasharray()" stroke-dashoffset="0" />
                <defs>
                  <linearGradient id="attendedGradient" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#7c5cff" />
                    <stop offset="100%" stop-color="#a78bfa" />
                  </linearGradient>
                </defs>
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="font-mono text-4xl font-medium" style="color: var(--text-primary);">{{ attendedPercent() }}%</span>
                <span class="text-xs font-semibold uppercase tracking-wide" style="color: var(--text-muted);">atendidos</span>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl p-3" style="background: var(--bg-elevated);">
              <p class="text-xs" style="color: var(--text-muted);">Atendidos</p>
              <p class="font-mono text-xl" style="color: var(--text-primary);">{{ atendidos() }}</p>
            </div>
            <div class="rounded-2xl p-3" style="background: var(--bg-elevated);">
              <p class="text-xs" style="color: var(--text-muted);">Restantes</p>
              <p class="font-mono text-xl" style="color: var(--text-primary);">{{ pendingAttention() }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <!-- Recent incidents -->
        <div class="dashboard-card p-5 lg:col-span-3" style="animation-delay: 280ms;">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Actividad reciente</h2>
            <a routerLink="/requests" class="text-xs" style="color: var(--accent);">Ver todos →</a>
          </div>

          @if (loading()) {
            <div class="space-y-3">
              @for (_ of [1,2,3,4]; track $index) {
                <div class="h-12 shimmer rounded-lg"></div>
              }
            </div>
          } @else if (recentIncidents().length === 0) {
            <div class="flex flex-col items-center justify-center py-10" style="color: var(--text-muted);">
              <p class="text-sm">Sin actividad reciente</p>
            </div>
          } @else {
            <div>
              @for (inc of recentIncidents(); track inc.id_incidente) {
                <a [routerLink]="['/requests', inc.id_incidente]"
                    class="soft-row flex items-center gap-3 px-3 transition-all group"
                    style="height: 52px;">
                   <div class="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0" style="background: var(--accent-soft); color: var(--accent);">
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                   </div>
                   <span class="text-sm font-medium flex-1 truncate" style="color: var(--text-primary);">{{ inc.clasificacion }}</span>
                  <span class="text-xs" style="color: var(--text-muted);">{{ formatShort(inc.fecha_creacion) }}</span>
                  <span [class]="'badge text-xs ' + estadoBadgeClass(inc.estado)">{{ inc.estado.split('_').join(' ') }}</span>
                </a>
              }
            </div>
          }
        </div>

        <!-- Technicians panel -->
        <div class="dashboard-card p-5 lg:col-span-2" style="animation-delay: 340ms;">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Equipo técnico</h2>
            <a routerLink="/technicians" class="text-xs" style="color: var(--accent);">Gestionar →</a>
          </div>

          @if (loading()) {
            <div class="space-y-3">
              @for (_ of [1,2,3]; track $index) {
                <div class="h-10 shimmer rounded-lg"></div>
              }
            </div>
          } @else if (tecnicos().length === 0) {
            <div class="flex flex-col items-center justify-center py-8" style="color: var(--text-muted);">
              <p class="text-sm">Sin técnicos</p>
              <a routerLink="/technicians" class="text-xs mt-2" style="color: var(--accent);">Agregar →</a>
            </div>
          } @else {
            <div>
              @for (t of tecnicos().slice(0, 6); track t.id_tecnico) {
                <div class="soft-row flex items-center gap-3 px-3" style="height: 52px;">
                  <div class="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                       [style.background]="t.disponible ? 'var(--accent-gradient)' : 'linear-gradient(135deg,#b9b4c5,#d6d1e2)'">
                    {{ t.nombre_completo[0].toUpperCase() }}
                  </div>
                  <span class="text-sm flex-1 truncate" style="color: var(--text-secondary);">{{ t.nombre_completo }}</span>
                  <span [class]="t.disponible ? 'badge-green badge' : 'badge-gray badge'" style="font-size:10px;">
                    {{ t.disponible ? 'Libre' : 'Ocupado' }}
                  </span>
                </div>
              }
              @if (tecnicos().length > 6) {
                <p class="text-xs text-center pt-1" style="color: var(--text-muted);">+{{ tecnicos().length - 6 }} más</p>
              }
            </div>
          }
        </div>
      </div>

      <!-- Admin: Talleres overview -->
      @if (auth.isAdmin() && talleres().length > 0) {
        <div class="dashboard-card p-5" style="animation-delay: 400ms;">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Talleres registrados</h2>
            <a routerLink="/admin/workshops" class="text-xs" style="color: var(--accent);">Gestionar →</a>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            @for (t of talleres().slice(0, 4); track t.id_taller) {
              <div class="rounded-lg p-3" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                <div class="flex items-start justify-between mb-2">
                  <span class="text-xs uppercase tracking-wider" style="color: var(--text-muted);">Taller</span>
                  <span [class]="t.activo ? 'badge-green badge' : 'badge-red badge'" style="font-size:10px;">
                    {{ t.activo ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <p class="text-sm font-medium truncate" style="color: var(--text-primary);">{{ t.nombre_negocio }}</p>
                @if (t.nit) {
                  <p class="text-xs mt-0.5" style="color: var(--text-muted);">NIT: {{ t.nit }}</p>
                }
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class DashboardComponent implements OnInit, OnDestroy {
  private incidentsService = inject(IncidentsService);
  private techniciansService = inject(TechniciansService);
  private adminService = inject(AdminService);
  protected ws = inject(WebSocketService);
  protected auth = inject(AuthService);
  private notifStore = inject(NotificationStore);

  private reloadSubject = new Subject<void>();
  private recentNotifs = new Set<string>();

  loading = signal(true);
  incidents = signal<Incident[]>([]);
  tecnicos = signal<Tecnico[]>([]);
  users = signal<User[]>([]);
  talleres = signal<Taller[]>([]);

  pendientes = computed(() => this.incidents().filter(i => ['CLASIFICADO','PENDIENTE'].includes(i.estado)).length);
  asignados = computed(() => this.incidents().filter(i => i.estado === 'ASIGNADO').length);
  enProceso = computed(() => this.incidents().filter(i => ['EN_PROCESO','EN_CAMINO'].includes(i.estado)).length);
  atendidos = computed(() => this.incidents().filter(i => i.estado === 'ATENDIDO').length);
  cancelados = computed(() => this.incidents().filter(i => i.estado === 'CANCELADO').length);
  tecnicosDisponibles = computed(() => this.tecnicos().filter(t => t.disponible).length);
  totalTecnicos = computed(() => this.tecnicos().length);
  totalUsers = computed(() => this.users().length);
  talleresActivos = computed(() => this.talleres().filter(t => t.activo).length);
  recentIncidents = computed(() => this.incidents().slice(0, 6));
  pendingAttention = computed(() => Math.max(this.incidents().length - this.atendidos(), 0));
  attendedPercent = computed(() => {
    const total = this.incidents().length;
    return total === 0 ? 0 : Math.round((this.atendidos() / total) * 100);
  });
  attendedDasharray = computed(() => {
    const circumference = 2 * Math.PI * 48;
    const filled = (this.attendedPercent() / 100) * circumference;
    return `${filled} ${circumference - filled}`;
  });
  statusBars = computed(() => {
    const items = [
      { key: 'PENDIENTE', label: 'Pendiente', short: 'Pend.' },
      { key: 'CLASIFICADO', label: 'Clasificado', short: 'Clas.' },
      { key: 'ASIGNADO', label: 'Asignado', short: 'Asig.' },
      { key: 'EN_CAMINO', label: 'En camino', short: 'Cam.' },
      { key: 'EN_PROCESO', label: 'En proceso', short: 'Proc.' },
      { key: 'ATENDIDO', label: 'Atendido', short: 'Atend.' },
      { key: 'CANCELADO', label: 'Cancelado', short: 'Canc.' },
    ];
    const counts = new Map<string, number>();
    for (const incident of this.incidents()) {
      counts.set(incident.estado, (counts.get(incident.estado) || 0) + 1);
    }
    const max = Math.max(...items.map(item => counts.get(item.key) || 0), 1);
    return items.map(item => {
      const value = counts.get(item.key) || 0;
      return { ...item, value, height: value === 0 ? 6 : Math.max(12, Math.round((value / max) * 100)) };
    });
  });

  firstName = () => (this.auth.user()?.nombre_completo || '').split(' ')[0] || 'Usuario';
  greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Buenos días';
    if (h < 19) return 'Buenas tardes';
    return 'Buenas noches';
  };
  today = () => new Date().toLocaleDateString('es-BO', { weekday: 'long', day: 'numeric', month: 'long' });

  ngOnInit(): void {
    this.reloadSubject.pipe(throttleTime(30000)).subscribe(() => this.loadData());
    this.loadData();
    this.ws.connectGlobal();
    this.ws.messages$.subscribe((msg) => {
      const tipo = msg.tipo || msg.type || '';
      if (tipo === 'conectado') return;

      const key = `${tipo}-${msg.incidente_id || ''}`;
      if (this.recentNotifs.has(key)) return;
      this.recentNotifs.add(key);
      setTimeout(() => this.recentNotifs.delete(key), 10000);

      const mensajes: Record<string, string> = {
        'estado_actualizado': `Incidente actualizado: ${msg.nuevo_estado || ''}`,
        'incidente_reportado': `Nuevo incidente: ${msg.clasificacion || 'INCIERTO'} · ${msg.prioridad || ''}`,
        'nueva_asignacion': `Incidente asignado a taller`,
        'nuevo_usuario': `Nuevo usuario registrado`,
      };
      const texto = mensajes[tipo] ?? (msg.mensaje || msg.data?.message || 'Nuevo evento');
      this.notifStore.push(texto, tipo === 'incidente_reportado' ? 'warning' : 'info');
      this.reloadSubject.next();
    });
  }

  ngOnDestroy(): void {
    this.reloadSubject.complete();
  }

  loadData(): void {
    this.loading.set(true);
    const base$ = forkJoin({
      incidents: this.incidentsService.getAll(),
      tecnicos: this.techniciansService.getAll(),
    });

    base$.subscribe({
      next: ({ incidents, tecnicos }) => {
        this.incidents.set(incidents);
        this.tecnicos.set(tecnicos);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });

    if (this.auth.isAdmin()) {
      forkJoin({
        users: this.adminService.getUsers(),
        talleres: this.adminService.getWorkshops(false),
      }).subscribe({
        next: ({ users, talleres }) => {
          this.users.set(users);
          this.talleres.set(talleres);
        },
      });
    }
  }

  dotColor(e: string): string {
    const m: Record<string,string> = {
      PENDIENTE: 'bg-orange-400', CLASIFICADO: 'bg-blue-400', ASIGNADO: 'bg-purple-400',
      EN_CAMINO: 'bg-amber-400', EN_PROCESO: 'bg-teal-400', ATENDIDO: 'bg-green-400', CANCELADO: 'bg-red-400',
    };
    return m[e] || 'bg-violet-200';
  }

  estadoBadgeClass(e: string): string {
    const m: Record<string,string> = {
      PENDIENTE: 'badge-orange', CLASIFICADO: 'badge-blue', ASIGNADO: 'badge-purple',
      EN_CAMINO: 'badge-amber', EN_PROCESO: 'badge-teal', ATENDIDO: 'badge-green', CANCELADO: 'badge-red',
    };
    return m[e] || 'badge-gray';
  }

  formatShort(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short' });
  }

  metricIcon(name: string): string {
    const icons: Record<string, string> = {
      requests: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v4m0 4h.01M10.3 4.4L2.8 18a2 2 0 001.7 3h15a2 2 0 001.7-3L13.7 4.4a2 2 0 00-3.4 0z"/></svg>',
      assignments: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5h6m-8 4h10M7 13h6m-6 4h4M5 3h14v18H5V3z"/></svg>',
      process: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6h4m-7 6h10m-8 6h6M5 3h14v18H5V3z"/></svg>',
      technicians: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 12a4 4 0 100-8 4 4 0 000 8zm-7 9a7 7 0 0114 0"/></svg>',
      users: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2m8-10a4 4 0 100-8 4 4 0 000 8"/></svg>',
      workshops: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21h18M5 21V8l7-4 7 4v13M9 21v-6h6v6"/></svg>',
      done: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
      cancelled: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
    };
    return icons[name] || icons['requests'];
  }
}
