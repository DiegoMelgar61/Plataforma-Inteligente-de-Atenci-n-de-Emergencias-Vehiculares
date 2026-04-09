import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { IncidentsService } from '../../core/services/incidents.service';
import { TechniciansService } from '../../core/services/technicians.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { Incident, Tecnico } from '../../models';
import { forkJoin, interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div>
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Mapa en vivo</h1>
          <p class="text-gray-500 text-sm">Ubicación de incidentes activos y técnicos</p>
        </div>
        <div class="flex items-center gap-3">
          @if (ws.connected()) {
            <span class="flex items-center gap-1.5 text-xs text-green-600 bg-green-50 border border-green-200 rounded-full px-3 py-1.5">
              <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Tiempo real
            </span>
          }
          <button (click)="reload()" class="btn-secondary">🔄 Actualizar</button>
        </div>
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-4 gap-3 mb-6">
        <div class="card py-3 text-center">
          <p class="text-2xl font-bold text-orange-500">{{ activeIncidents().length }}</p>
          <p class="text-xs text-gray-500">Incidentes activos</p>
        </div>
        <div class="card py-3 text-center">
          <p class="text-2xl font-bold text-green-600">{{ availableTecnicos().length }}</p>
          <p class="text-xs text-gray-500">Técnicos disponibles</p>
        </div>
        <div class="card py-3 text-center">
          <p class="text-2xl font-bold text-amber-500">{{ inRoute().length }}</p>
          <p class="text-xs text-gray-500">En camino</p>
        </div>
        <div class="card py-3 text-center">
          <p class="text-2xl font-bold text-teal-600">{{ inProcess().length }}</p>
          <p class="text-xs text-gray-500">En proceso</p>
        </div>
      </div>

      <!-- Map area -->
      <div class="card p-0 overflow-hidden mb-6">
        <div class="bg-gradient-to-b from-blue-50 to-green-50 h-96 flex items-center justify-center relative">
          <!-- Grid lines for map feel -->
          <div class="absolute inset-0 opacity-10"
               style="background-image: linear-gradient(#93c5fd 1px, transparent 1px), linear-gradient(90deg, #93c5fd 1px, transparent 1px);
                      background-size: 40px 40px;">
          </div>

          <!-- Incident markers -->
          @for (inc of activeIncidents(); track inc.id_incidente) {
            @if (inc.latitud && inc.longitud) {
              <div class="absolute flex flex-col items-center cursor-pointer group"
                   [style.left.%]="toMapX(inc.longitud!)"
                   [style.top.%]="toMapY(inc.latitud!)"
                   (click)="selectedIncident.set(inc)">
                <div [class]="'w-8 h-8 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-sm ' + incidentDot(inc.estado)">
                  {{ classIcon(inc.clasificacion) }}
                </div>
                <div class="hidden group-hover:block absolute bottom-10 bg-gray-900 text-white text-xs rounded-lg px-2 py-1 whitespace-nowrap z-10">
                  {{ inc.clasificacion }} · {{ inc.estado }}
                </div>
              </div>
            }
          }

          <!-- Tecnico markers -->
          @for (t of tecnicos(); track t.id_tecnico) {
            @if (t.ubicacion_lat && t.ubicacion_lng) {
              <div class="absolute flex flex-col items-center"
                   [style.left.%]="toMapX(t.ubicacion_lng!)"
                   [style.top.%]="toMapY(t.ubicacion_lat!)">
                <div [class]="'w-7 h-7 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-xs ' + (t.disponible ? 'bg-green-500' : 'bg-gray-400')">
                  👷
                </div>
              </div>
            }
          }

          <!-- No location data -->
          @if (incidentsWithLocation().length === 0) {
            <div class="text-center z-10">
              <div class="text-5xl mb-3">🗺️</div>
              <p class="text-gray-600 font-medium">Mapa de incidentes activos</p>
              <p class="text-gray-400 text-sm mt-1">
                {{ activeIncidents().length > 0
                  ? 'Los incidentes activos no tienen ubicación GPS registrada'
                  : 'No hay incidentes activos en este momento' }}
              </p>
            </div>
          }
        </div>
        <div class="p-3 bg-gray-50 border-t flex items-center gap-4 text-xs text-gray-500">
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-orange-400 inline-block"></span>Pendiente</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-amber-400 inline-block"></span>En camino</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-teal-400 inline-block"></span>En proceso</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-green-500 inline-block"></span>Técnico disponible</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-gray-400 inline-block"></span>Técnico ocupado</span>
        </div>
      </div>

      <!-- Incident detail popup -->
      @if (selectedIncident()) {
        <div class="card border-2 border-blue-100 mb-6">
          <div class="flex items-start justify-between">
            <div>
              <h3 class="font-semibold text-gray-900">{{ selectedIncident()!.clasificacion }}</h3>
              <p class="text-xs text-gray-400"># {{ selectedIncident()!.id_incidente.substring(0,8).toUpperCase() }}</p>
            </div>
            <button (click)="selectedIncident.set(null)" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          <div class="mt-3 flex items-center gap-3">
            <span [class]="'badge ' + estadoBadge(selectedIncident()!.estado)">{{ selectedIncident()!.estado }}</span>
            <span class="text-sm text-gray-500">Prioridad: {{ selectedIncident()!.prioridad }}</span>
          </div>
          @if (selectedIncident()!.resumen_ia) {
            <p class="text-sm text-gray-600 mt-2">🤖 {{ selectedIncident()!.resumen_ia }}</p>
          }
          <a [routerLink]="['/requests', selectedIncident()!.id_incidente]" class="btn-primary text-sm mt-3 inline-block">
            Ver detalle completo →
          </a>
        </div>
      }

      <!-- Active incidents table -->
      <div class="card">
        <h2 class="font-semibold text-gray-900 mb-4">Incidentes activos ({{ activeIncidents().length }})</h2>
        @if (activeIncidents().length === 0) {
          <div class="text-center py-8 text-gray-400">
            <div class="text-3xl mb-2">✅</div>
            <p class="text-sm">No hay incidentes activos</p>
          </div>
        } @else {
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-100">
                  <th class="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th class="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Tipo</th>
                  <th class="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Estado</th>
                  <th class="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Prioridad</th>
                  <th class="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Ubicación</th>
                  <th class="text-right py-2 px-3"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                @for (inc of activeIncidents(); track inc.id_incidente) {
                  <tr class="hover:bg-gray-50">
                    <td class="py-3 px-3 font-mono text-xs text-gray-500">#{{ inc.id_incidente.substring(0,8).toUpperCase() }}</td>
                    <td class="py-3 px-3">{{ classIcon(inc.clasificacion) }} {{ inc.clasificacion }}</td>
                    <td class="py-3 px-3">
                      <span [class]="'badge ' + estadoBadge(inc.estado)">{{ inc.estado.split('_').join(' ') }}</span>
                    </td>
                    <td class="py-3 px-3">
                      <span [class]="priorityColor(inc.prioridad)">{{ inc.prioridad }}</span>
                    </td>
                    <td class="py-3 px-3 text-gray-400">
                      {{ inc.latitud ? (inc.latitud.toFixed(3) + ', ' + inc.longitud!.toFixed(3)) : 'Sin GPS' }}
                    </td>
                    <td class="py-3 px-3 text-right">
                      <a [routerLink]="['/requests', inc.id_incidente]" class="text-blue-600 hover:underline text-xs">Ver →</a>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
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

  activeIncidents = () => this.incidents().filter(i =>
    ['CLASIFICADO', 'ASIGNADO', 'EN_CAMINO', 'EN_PROCESO', 'PENDIENTE'].includes(i.estado)
  );
  incidentsWithLocation = () => this.activeIncidents().filter(i => i.latitud != null);
  availableTecnicos = () => this.tecnicos().filter(t => t.disponible);
  inRoute = () => this.incidents().filter(i => i.estado === 'EN_CAMINO');
  inProcess = () => this.incidents().filter(i => i.estado === 'EN_PROCESO');

  ngOnInit(): void {
    this.reload();
    this.ws.connectGlobal();

    // Auto-refresh every 30s
    const refresh = interval(30000).pipe(
      switchMap(() => forkJoin({
        incidents: this.incidentsService.getAll(),
        tecnicos: this.techniciansService.getAll(),
      }))
    ).subscribe(({ incidents, tecnicos }) => {
      this.incidents.set(incidents);
      this.tecnicos.set(tecnicos);
    });
    this.subs.push(refresh);

    // Real-time updates
    const wsSub = this.ws.messages$.subscribe(() => this.reload());
    this.subs.push(wsSub);
  }

  ngOnDestroy(): void {
    this.subs.forEach(s => s.unsubscribe());
  }

  reload(): void {
    forkJoin({
      incidents: this.incidentsService.getAll(),
      tecnicos: this.techniciansService.getAll(),
    }).subscribe({
      next: ({ incidents, tecnicos }) => {
        this.incidents.set(incidents);
        this.tecnicos.set(tecnicos);
      },
    });
  }

  // Convert lng to X% on map (rough)
  toMapX(lng: number): number {
    return Math.max(5, Math.min(95, ((lng + 180) / 360) * 100));
  }

  // Convert lat to Y% on map (rough, inverted)
  toMapY(lat: number): number {
    return Math.max(5, Math.min(95, ((90 - lat) / 180) * 100));
  }

  incidentDot(e: string): string {
    const map: Record<string, string> = {
      PENDIENTE: 'bg-orange-400',
      CLASIFICADO: 'bg-blue-400',
      ASIGNADO: 'bg-purple-400',
      EN_CAMINO: 'bg-amber-400',
      EN_PROCESO: 'bg-teal-400',
    };
    return map[e] || 'bg-gray-300';
  }

  classIcon(c: string): string {
    return { BATERIA: '🔋', LLANTA: '🔄', CHOQUE: '💥', MOTOR: '⚙️', OTROS: '🚗', INCIERTO: '❓' }[c] || '🚗';
  }

  estadoBadge(e: string): string {
    const map: Record<string, string> = {
      PENDIENTE: 'bg-orange-100 text-orange-700',
      CLASIFICADO: 'bg-blue-100 text-blue-700',
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
}
