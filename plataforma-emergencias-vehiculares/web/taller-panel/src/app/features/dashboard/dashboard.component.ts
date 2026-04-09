import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { IncidentsService } from '../../core/services/incidents.service';
import { TechniciansService } from '../../core/services/technicians.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { AuthService } from '../../core/services/auth.service';
import { Incident, Asignacion, Tecnico } from '../../models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div>
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-gray-500 text-sm mt-1">Bienvenido, {{ userName() }} · Hoy {{ today() }}</p>
      </div>

      <!-- WS Status -->
      @if (ws.connected()) {
        <div class="mb-4 flex items-center gap-2 text-xs text-green-600 bg-green-50 border border-green-200 rounded-lg px-3 py-2 w-fit">
          <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          Conectado en tiempo real
        </div>
      }

      <!-- Stats Grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Pendientes</p>
              <p class="text-3xl font-bold text-orange-500 mt-1">{{ pendientes() }}</p>
            </div>
            <div class="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center text-2xl">⏳</div>
          </div>
          <a routerLink="/requests" class="text-xs text-blue-600 hover:underline mt-2 block">Ver todos →</a>
        </div>

        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Asignados</p>
              <p class="text-3xl font-bold text-purple-600 mt-1">{{ asignados() }}</p>
            </div>
            <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-2xl">📋</div>
          </div>
          <a routerLink="/assignments" class="text-xs text-blue-600 hover:underline mt-2 block">Ver asignaciones →</a>
        </div>

        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">En Proceso</p>
              <p class="text-3xl font-bold text-teal-600 mt-1">{{ enProceso() }}</p>
            </div>
            <div class="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center text-2xl">🔧</div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Técnicos Disp.</p>
              <p class="text-3xl font-bold text-blue-600 mt-1">
                {{ tecnicosDisponibles() }}<span class="text-lg text-gray-400">/{{ totalTecnicos() }}</span>
              </p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-2xl">👷</div>
          </div>
          <a routerLink="/technicians" class="text-xs text-blue-600 hover:underline mt-2 block">Gestionar →</a>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent incidents -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-semibold text-gray-900">Solicitudes recientes</h2>
            <a routerLink="/requests" class="text-xs text-blue-600 hover:underline">Ver todas</a>
          </div>
          @if (loading()) {
            <div class="space-y-3">
              @for (_ of [1,2,3]; track $index) {
                <div class="h-14 bg-gray-100 rounded-lg animate-pulse"></div>
              }
            </div>
          } @else if (recentIncidents().length === 0) {
            <div class="text-center py-8 text-gray-400">
              <div class="text-4xl mb-2">📭</div>
              <p class="text-sm">Sin solicitudes recientes</p>
            </div>
          } @else {
            <div class="space-y-3">
              @for (inc of recentIncidents(); track inc.id_incidente) {
                <a [routerLink]="['/requests', inc.id_incidente]"
                   class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors border border-gray-100">
                  <div [class]="'w-2 h-2 rounded-full flex-shrink-0 ' + estadoColor(inc.estado)"></div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900">{{ inc.clasificacion }}</p>
                    <p class="text-xs text-gray-400">{{ inc.id_incidente.substring(0,8).toUpperCase() }}</p>
                  </div>
                  <span [class]="'badge ' + badgeClass(inc.estado)">{{ inc.estado.replace('_',' ') }}</span>
                </a>
              }
            </div>
          }
        </div>

        <!-- Technicians status -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-semibold text-gray-900">Estado de técnicos</h2>
            <a routerLink="/technicians" class="text-xs text-blue-600 hover:underline">Gestionar</a>
          </div>
          @if (loading()) {
            <div class="space-y-3">
              @for (_ of [1,2,3]; track $index) {
                <div class="h-12 bg-gray-100 rounded-lg animate-pulse"></div>
              }
            </div>
          } @else if (tecnicos().length === 0) {
            <div class="text-center py-8 text-gray-400">
              <div class="text-4xl mb-2">👷</div>
              <p class="text-sm">Sin técnicos registrados</p>
              <a routerLink="/technicians" class="text-xs text-blue-600 hover:underline mt-2 block">Agregar técnico</a>
            </div>
          } @else {
            <div class="space-y-2">
              @for (t of tecnicos(); track t.id_tecnico) {
                <div class="flex items-center gap-3 p-3 rounded-lg border border-gray-100">
                  <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold text-gray-600">
                    {{ t.nombre_completo[0] }}
                  </div>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ t.nombre_completo }}</p>
                    @if (t.telefono) {
                      <p class="text-xs text-gray-400">{{ t.telefono }}</p>
                    }
                  </div>
                  <span [class]="t.disponible ? 'badge bg-green-100 text-green-700' : 'badge bg-gray-100 text-gray-500'">
                    {{ t.disponible ? 'Disponible' : 'Ocupado' }}
                  </span>
                </div>
              }
            </div>
          }
        </div>
      </div>
    </div>
  `,
})
export class DashboardComponent implements OnInit {
  private incidentsService = inject(IncidentsService);
  private techniciansService = inject(TechniciansService);
  protected ws = inject(WebSocketService);
  private authService = inject(AuthService);

  loading = signal(true);
  incidents = signal<Incident[]>([]);
  asignaciones = signal<Asignacion[]>([]);
  tecnicos = signal<Tecnico[]>([]);

  pendientes = computed(() => this.incidents().filter(i => i.estado === 'CLASIFICADO' || i.estado === 'PENDIENTE').length);
  asignados = computed(() => this.incidents().filter(i => i.estado === 'ASIGNADO').length);
  enProceso = computed(() => this.incidents().filter(i => i.estado === 'EN_PROCESO' || i.estado === 'EN_CAMINO').length);
  tecnicosDisponibles = computed(() => this.tecnicos().filter(t => t.disponible).length);
  totalTecnicos = computed(() => this.tecnicos().length);
  recentIncidents = computed(() => this.incidents().slice(0, 5));

  userName = () => this.authService.user()?.nombre_completo || 'Taller';
  today = () => new Date().toLocaleDateString('es-BO', { weekday: 'long', day: 'numeric', month: 'long' });

  ngOnInit(): void {
    this.loadData();
    this.ws.connectGlobal();
    this.ws.messages$.subscribe(() => this.loadData());
  }

  loadData(): void {
    this.loading.set(true);
    forkJoin({
      incidents: this.incidentsService.getAll(),
      tecnicos: this.techniciansService.getAll(),
    }).subscribe({
      next: ({ incidents, tecnicos }) => {
        this.incidents.set(incidents);
        this.tecnicos.set(tecnicos);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  estadoColor(estado: string): string {
    const map: Record<string, string> = {
      PENDIENTE: 'bg-orange-400',
      CLASIFICADO: 'bg-blue-400',
      ASIGNADO: 'bg-purple-400',
      EN_CAMINO: 'bg-amber-400',
      EN_PROCESO: 'bg-teal-400',
      ATENDIDO: 'bg-green-500',
      CANCELADO: 'bg-red-400',
    };
    return map[estado] || 'bg-gray-300';
  }

  badgeClass(estado: string): string {
    const map: Record<string, string> = {
      PENDIENTE: 'bg-orange-100 text-orange-700',
      CLASIFICADO: 'bg-blue-100 text-blue-700',
      ASIGNADO: 'bg-purple-100 text-purple-700',
      EN_CAMINO: 'bg-amber-100 text-amber-700',
      EN_PROCESO: 'bg-teal-100 text-teal-700',
      ATENDIDO: 'bg-green-100 text-green-700',
      CANCELADO: 'bg-red-100 text-red-700',
    };
    return map[estado] || 'bg-gray-100 text-gray-600';
  }
}
