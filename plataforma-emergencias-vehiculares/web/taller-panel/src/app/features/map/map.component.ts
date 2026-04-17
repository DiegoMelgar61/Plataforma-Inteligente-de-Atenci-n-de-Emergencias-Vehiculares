import { Component, inject, signal, OnInit, OnDestroy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { IncidentsService } from '../../core/services/incidents.service';
import { TechniciansService } from '../../core/services/technicians.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { Incident, Tecnico } from '../../models';
import { forkJoin, interval, Subject, Subscription } from 'rxjs';
import { switchMap, throttleTime } from 'rxjs/operators';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="space-y-5 fade-in">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">Mapa de operaciones</h1>
          <p class="page-subtitle">Incidentes activos y ubicación de técnicos</p>
        </div>
        <div class="flex items-center gap-2">
          @if (ws.connected()) {
            <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs"
                 style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); color: #6ee7b7;">
              <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
              En vivo
            </div>
          }
          <button (click)="reload()" class="btn-ghost text-xs">🔄</button>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-3">
        <div class="surface p-4 text-center">
          <p class="text-2xl font-bold" style="color: var(--warning);">{{ activeIncidents().length }}</p>
          <p class="text-xs mt-1" style="color: var(--text-muted);">Activos</p>
        </div>
        <div class="surface p-4 text-center">
          <p class="text-2xl font-bold" style="color: var(--success);">{{ availableTecnicos().length }}</p>
          <p class="text-xs mt-1" style="color: var(--text-muted);">Disponibles</p>
        </div>
        <div class="surface p-4 text-center">
          <p class="text-2xl font-bold" style="color: #fcd34d;">{{ inRoute().length }}</p>
          <p class="text-xs mt-1" style="color: var(--text-muted);">En camino</p>
        </div>
        <div class="surface p-4 text-center">
          <p class="text-2xl font-bold" style="color: #5eead4;">{{ inProcess().length }}</p>
          <p class="text-xs mt-1" style="color: var(--text-muted);">En proceso</p>
        </div>
      </div>

      <!-- Map canvas -->
      <div class="surface overflow-hidden">
        <div class="relative h-80 flex items-center justify-center"
             style="background: radial-gradient(ellipse at center, #0d1f3c 0%, #0a0f1e 100%);">
          <!-- Grid -->
          <div class="absolute inset-0 opacity-10"
               style="background-image:linear-gradient(rgba(59,130,246,0.4) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,0.4) 1px,transparent 1px);background-size:40px 40px;"></div>

          <!-- Incident dots -->
          @for (inc of incidentsWithLocation(); track inc.id_incidente) {
            <div class="absolute flex flex-col items-center cursor-pointer group"
                 [style.left.%]="toMapX(inc.longitud!)"
                 [style.top.%]="toMapY(inc.latitud!)"
                 (click)="selectedIncident.set(inc)">
              <div class="w-8 h-8 rounded-full border-2 border-white/20 flex items-center justify-center text-xs shadow-lg transition-transform group-hover:scale-110"
                   [class]="incidentDot(inc.estado)">
                {{ classIcon(inc.clasificacion) }}
              </div>
              <div class="hidden group-hover:block absolute bottom-10 left-1/2 -translate-x-1/2 rounded-lg px-2.5 py-1.5 text-xs whitespace-nowrap z-10 shadow-xl"
                   style="background: var(--bg-elevated); border: 1px solid var(--border-strong); color: var(--text-primary);">
                {{ inc.clasificacion }} · {{ inc.estado }}
              </div>
            </div>
          }

          <!-- Tecnico dots -->
          @for (t of tecnicosWithLocation(); track t.id_tecnico) {
            <div class="absolute flex items-center justify-center w-7 h-7 rounded-full border-2 border-white/30 text-xs shadow-lg"
                 [style.left.%]="toMapX(t.ubicacion_lng!)"
                 [style.top.%]="toMapY(t.ubicacion_lat!)"
                 [class]="t.disponible ? 'bg-green-500' : 'bg-gray-600'">
              👷
            </div>
          }

          <!-- Empty state -->
          @if (incidentsWithLocation().length === 0) {
            <div class="text-center z-10">
              <div class="text-5xl mb-3">🗺️</div>
              <p class="font-medium text-sm" style="color: var(--text-secondary);">
                {{ activeIncidents().length > 0 ? 'Sin coordenadas GPS' : 'Sin incidentes activos' }}
              </p>
              <p class="text-xs mt-1" style="color: var(--text-muted);">
                {{ activeIncidents().length > 0 ? 'Los incidentes activos no tienen ubicación registrada' : 'Cuando haya emergencias aparecerán aquí' }}
              </p>
            </div>
          }
        </div>

        <!-- Legend -->
        <div class="px-4 py-2.5 flex items-center gap-5 flex-wrap" style="border-top: 1px solid var(--border);">
          @for (leg of legend; track leg.label) {
            <div class="flex items-center gap-1.5 text-xs" style="color: var(--text-muted);">
              <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" [class]="leg.color"></span>
              {{ leg.label }}
            </div>
          }
        </div>
      </div>

      <!-- Selected incident popup -->
      @if (selectedIncident()) {
        <div class="surface p-4 fade-in" style="border-color: rgba(59,130,246,0.3);">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                   style="background: rgba(59,130,246,0.1);">
                {{ classIcon(selectedIncident()!.clasificacion) }}
              </div>
              <div>
                <h3 class="text-sm font-semibold" style="color: var(--text-primary);">{{ selectedIncident()!.clasificacion }}</h3>
                <p class="text-xs font-mono" style="color: var(--text-muted);">#{{ selectedIncident()!.id_incidente.substring(0,8).toUpperCase() }}</p>
              </div>
            </div>
            <button (click)="selectedIncident.set(null)" style="color: var(--text-muted);">✕</button>
          </div>
          <div class="flex items-center gap-3 mt-3">
            <span [class]="'badge ' + estadoBadge(selectedIncident()!.estado)">{{ selectedIncident()!.estado }}</span>
            <span [class]="'badge ' + prioridadBadge(selectedIncident()!.prioridad)">{{ selectedIncident()!.prioridad }}</span>
          </div>
          @if (selectedIncident()!.resumen_ia) {
            <p class="text-xs mt-2" style="color: var(--text-muted);">🤖 {{ selectedIncident()!.resumen_ia }}</p>
          }
          <a [routerLink]="['/requests', selectedIncident()!.id_incidente]" class="btn-primary text-xs mt-3 inline-flex">
            Ver detalle completo →
          </a>
        </div>
      }

      <!-- Active table -->
      <div class="table-wrap">
        <div class="px-4 py-3" style="border-bottom: 1px solid var(--border);">
          <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Incidentes activos ({{ activeIncidents().length }})</h2>
        </div>
        @if (activeIncidents().length === 0) {
          <div class="p-12 text-center">
            <span class="text-4xl block mb-2">✅</span>
            <p class="text-sm" style="color: var(--text-muted);">Sin incidentes activos</p>
          </div>
        } @else {
          <table class="w-full">
            <thead><tr>
              <th>ID</th><th>Tipo</th><th>Estado</th><th>Prioridad</th><th>Ubicación</th><th></th>
            </tr></thead>
            <tbody>
              @for (inc of activeIncidents(); track inc.id_incidente) {
                <tr>
                  <td class="font-mono text-xs" style="color: var(--text-muted);">#{{ inc.id_incidente.substring(0,8).toUpperCase() }}</td>
                  <td class="text-sm">{{ classIcon(inc.clasificacion) }} {{ inc.clasificacion }}</td>
                  <td><span [class]="'badge ' + estadoBadge(inc.estado)">{{ inc.estado.split('_').join(' ') }}</span></td>
                  <td><span [class]="'badge ' + prioridadBadge(inc.prioridad)">{{ inc.prioridad }}</span></td>
                  <td class="text-xs" style="color: var(--text-muted);">{{ inc.latitud ? (inc.latitud.toFixed(3) + ', ' + inc.longitud!.toFixed(3)) : 'Sin GPS' }}</td>
                  <td><a [routerLink]="['/requests', inc.id_incidente]" class="text-xs" style="color: var(--accent);">Ver →</a></td>
                </tr>
              }
            </tbody>
          </table>
        }
      </div>
    </div>
  `,
})
export class MapComponent implements OnInit, OnDestroy {
  private incidentsService = inject(IncidentsService);
  private techniciansService = inject(TechniciansService);
  protected ws = inject(WebSocketService);

  loading = signal(false);
  incidents = signal<Incident[]>([]);
  tecnicos = signal<Tecnico[]>([]);
  selectedIncident = signal<Incident | null>(null);
  private subs: Subscription[] = [];
  private wsReloadSubject = new Subject<void>();

  activeIncidents = computed(() => this.incidents().filter(i =>
    ['CLASIFICADO', 'ASIGNADO', 'EN_CAMINO', 'EN_PROCESO', 'PENDIENTE'].includes(i.estado)
  ));
  incidentsWithLocation = computed(() => this.activeIncidents().filter(i => i.latitud != null));
  tecnicosWithLocation = computed(() => this.tecnicos().filter(t => t.ubicacion_lat != null));
  availableTecnicos = computed(() => this.tecnicos().filter(t => t.disponible));
  inRoute = computed(() => this.incidents().filter(i => i.estado === 'EN_CAMINO'));
  inProcess = computed(() => this.incidents().filter(i => i.estado === 'EN_PROCESO'));

  legend = [
    { color: 'bg-orange-400', label: 'Pendiente' },
    { color: 'bg-blue-400', label: 'Clasificado' },
    { color: 'bg-amber-400', label: 'En camino' },
    { color: 'bg-teal-400', label: 'En proceso' },
    { color: 'bg-green-500', label: 'Técnico libre' },
    { color: 'bg-gray-500', label: 'Técnico ocupado' },
  ];

  ngOnInit(): void {
    this.reload();
    this.ws.connectGlobal();
    this.subs.push(
      interval(30000).pipe(switchMap(() => forkJoin({ incidents: this.incidentsService.getAll(), tecnicos: this.techniciansService.getAll() }))).subscribe(({ incidents, tecnicos }) => { this.incidents.set(incidents); this.tecnicos.set(tecnicos); }),
      this.wsReloadSubject.pipe(throttleTime(30000)).subscribe(() => this.reload()),
      this.ws.messages$.subscribe(() => this.wsReloadSubject.next()),
    );
  }

  ngOnDestroy(): void {
    this.subs.forEach(s => s.unsubscribe());
    this.wsReloadSubject.complete();
  }

  reload(): void {
    forkJoin({ incidents: this.incidentsService.getAll(), tecnicos: this.techniciansService.getAll() }).subscribe({
      next: ({ incidents, tecnicos }) => { this.incidents.set(incidents); this.tecnicos.set(tecnicos); },
    });
  }

  toMapX(lng: number): number { return Math.max(5, Math.min(92, ((lng + 180) / 360) * 100)); }
  toMapY(lat: number): number { return Math.max(5, Math.min(92, ((90 - lat) / 180) * 100)); }

  incidentDot(e: string): string {
    const m: Record<string,string> = { PENDIENTE: 'bg-orange-500', CLASIFICADO: 'bg-blue-500', ASIGNADO: 'bg-purple-500', EN_CAMINO: 'bg-amber-500', EN_PROCESO: 'bg-teal-500' };
    return m[e] || 'bg-gray-500';
  }

  classIcon(c: string): string {
    return { BATERIA: '🔋', LLANTA: '🔄', CHOQUE: '💥', MOTOR: '⚙️', OTROS: '🚗', INCIERTO: '❓' }[c] || '🚗';
  }

  estadoBadge(e: string): string {
    const m: Record<string,string> = { PENDIENTE: 'badge-orange', CLASIFICADO: 'badge-blue', ASIGNADO: 'badge-purple', EN_CAMINO: 'badge-amber', EN_PROCESO: 'badge-teal', ATENDIDO: 'badge-green' };
    return m[e] || 'badge-gray';
  }

  prioridadBadge(p: string): string {
    return { ALTA: 'badge-red', MEDIA: 'badge-amber', BAJA: 'badge-green' }[p] || 'badge-gray';
  }
}
