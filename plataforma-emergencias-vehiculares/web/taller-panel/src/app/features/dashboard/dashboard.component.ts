import { Component, inject, signal, OnInit, OnDestroy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { forkJoin, Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import { IncidentsService } from '../../core/services/incidents.service';
import { TechniciansService } from '../../core/services/technicians.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { AuthService } from '../../core/services/auth.service';
import { AdminService } from '../../core/services/admin.service';
import { NotificationStore } from '../../core/services/notification-store.service';
import { Incident, Tecnico, User, Taller } from '../../models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
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
             style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); color: #6ee7b7;">
          <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
          Tiempo real activo
        </div>
      }

      <!-- Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(249,115,22,0.12);">🚨</div>
          <div>
            <p class="stat-label">Pendientes</p>
            <p class="stat-value">{{ pendientes() }}</p>
            <a routerLink="/requests" class="text-xs mt-1 block" style="color: var(--accent);">Ver →</a>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(139,92,246,0.12);">📋</div>
          <div>
            <p class="stat-label">Asignados</p>
            <p class="stat-value">{{ asignados() }}</p>
            <a routerLink="/assignments" class="text-xs mt-1 block" style="color: var(--accent);">Ver →</a>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(20,184,166,0.12);">🔧</div>
          <div>
            <p class="stat-label">En proceso</p>
            <p class="stat-value">{{ enProceso() }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(59,130,246,0.12);">👷</div>
          <div>
            <p class="stat-label">Técnicos disponibles</p>
            <p class="stat-value">
              {{ tecnicosDisponibles() }}
              <span class="text-base font-normal" style="color: var(--text-muted);">/{{ totalTecnicos() }}</span>
            </p>
            <a routerLink="/technicians" class="text-xs mt-1 block" style="color: var(--accent);">Gestionar →</a>
          </div>
        </div>
        @if (auth.isAdmin()) {
          <div class="stat-card">
            <div class="stat-icon" style="background: rgba(245,158,11,0.12);">👥</div>
            <div>
              <p class="stat-label">Total usuarios</p>
              <p class="stat-value">{{ totalUsers() }}</p>
              <a routerLink="/admin/users" class="text-xs mt-1 block" style="color: var(--accent);">Ver →</a>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: rgba(16,185,129,0.12);">🏪</div>
            <div>
              <p class="stat-label">Talleres activos</p>
              <p class="stat-value">{{ talleresActivos() }}</p>
              <a routerLink="/admin/workshops" class="text-xs mt-1 block" style="color: var(--accent);">Gestionar →</a>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: rgba(16,185,129,0.12);">✅</div>
            <div>
              <p class="stat-label">Atendidos hoy</p>
              <p class="stat-value text-green-400">{{ atendidos() }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: rgba(239,68,68,0.12);">❌</div>
            <div>
              <p class="stat-label">Cancelados</p>
              <p class="stat-value text-red-400">{{ cancelados() }}</p>
            </div>
          </div>
        }
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <!-- Recent incidents -->
        <div class="surface p-5 lg:col-span-3">
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
              <span class="text-3xl mb-2">📭</span>
              <p class="text-sm">Sin actividad reciente</p>
            </div>
          } @else {
            <div class="space-y-1.5">
              @for (inc of recentIncidents(); track inc.id_incidente) {
                <a [routerLink]="['/requests', inc.id_incidente]"
                   class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group"
                   style="border: 1px solid transparent;"
                   onmouseenter="this.style.background='var(--bg-elevated)';this.style.borderColor='var(--border)'"
                   onmouseleave="this.style.background='transparent';this.style.borderColor='transparent'">
                  <div class="w-2 h-2 rounded-full flex-shrink-0" [class]="dotColor(inc.estado)"></div>
                  <span class="text-sm font-medium flex-1 truncate" style="color: var(--text-primary);">{{ inc.clasificacion }}</span>
                  <span class="text-xs" style="color: var(--text-muted);">{{ formatShort(inc.fecha_creacion) }}</span>
                  <span [class]="'badge text-xs ' + estadoBadgeClass(inc.estado)">{{ inc.estado.split('_').join(' ') }}</span>
                </a>
              }
            </div>
          }
        </div>

        <!-- Technicians panel -->
        <div class="surface p-5 lg:col-span-2">
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
              <span class="text-3xl mb-2">👷</span>
              <p class="text-sm">Sin técnicos</p>
              <a routerLink="/technicians" class="text-xs mt-2" style="color: var(--accent);">Agregar →</a>
            </div>
          } @else {
            <div class="space-y-2">
              @for (t of tecnicos().slice(0, 6); track t.id_tecnico) {
                <div class="flex items-center gap-3">
                  <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                       [style.background]="t.disponible ? 'var(--success)' : 'var(--text-muted)'">
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
        <div class="surface p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Talleres registrados</h2>
            <a routerLink="/admin/workshops" class="text-xs" style="color: var(--accent);">Gestionar →</a>
          </div>
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
            @for (t of talleres().slice(0, 4); track t.id_taller) {
              <div class="rounded-lg p-3" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                <div class="flex items-start justify-between mb-2">
                  <span class="text-lg">🏪</span>
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

  firstName = () => (this.auth.user()?.nombre_completo || '').split(' ')[0] || 'Usuario';
  greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Buenos días';
    if (h < 19) return 'Buenas tardes';
    return 'Buenas noches';
  };
  today = () => new Date().toLocaleDateString('es-BO', { weekday: 'long', day: 'numeric', month: 'long' });

  ngOnInit(): void {
    this.reloadSubject.pipe(debounceTime(2000)).subscribe(() => this.loadData());
    this.loadData();
    this.ws.connectGlobal();
    this.ws.messages$.subscribe((msg) => {
      const tipo = msg.tipo || msg.type || '';
      if (tipo !== 'conectado') {
        this.notifStore.push(msg.data?.message || msg.mensaje || 'Nuevo evento', 'info');
        this.reloadSubject.next();
      }
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
    return m[e] || 'bg-gray-400';
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
}
