import { Component, inject, signal, OnInit, OnDestroy, AfterViewInit, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import * as L from 'leaflet';
import { IncidentsService } from '../requests/incidents.service';
import { TechniciansService } from '../technicians/technicians.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { Incident, Tecnico } from '../../models';
import { forkJoin, interval, Subject, Subscription } from 'rxjs';
import { switchMap, throttleTime } from 'rxjs/operators';

// Santa Cruz de la Sierra, Bolivia
const DEFAULT_CENTER: L.LatLngTuple = [-17.7833, -63.1812];
const DEFAULT_ZOOM = 12;

// Marker color by incident state
const ESTADO_COLOR: Record<string, string> = {
  PENDIENTE: '#f97316',   // orange
  CLASIFICADO: '#3b82f6', // blue
  ASIGNADO: '#a855f7',    // purple
  EN_CAMINO: '#eab308',   // yellow
  EN_PROCESO: '#14b8a6',  // teal
};

function incidentIcon(color: string, label: string): L.DivIcon {
  return L.divIcon({
    html: `<div style="background:${color};width:30px;height:30px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;">
             <span style="transform:rotate(45deg);color:#fff;font-size:10px;font-weight:700;">${label}</span>
           </div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -28],
    className: '',
  });
}

function tecnicoIcon(disponible: boolean): L.DivIcon {
  const color = disponible ? '#22c55e' : '#6b7280';
  return L.divIcon({
    html: `<div style="background:${color};width:22px;height:22px;border-radius:50%;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;color:#fff;font-size:9px;font-weight:700;">T</div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -10],
    className: '',
  });
}

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
              <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
              En vivo
            </div>
          }
          <button (click)="reload()" class="btn-ghost text-xs">Actualizar</button>
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

      <!-- Real Leaflet map -->
      <div class="surface overflow-hidden">
        <div id="operations-map" style="height: 480px; width: 100%;"></div>

        @if (incidentsWithLocation().length === 0) {
          <div class="px-4 py-3 text-center" style="border-top: 1px solid var(--border);">
            <p class="text-xs" style="color: var(--text-muted);">
              {{ activeIncidents().length > 0 ? 'Los incidentes activos no tienen ubicación GPS registrada' : 'Sin incidentes activos en el mapa' }}
            </p>
          </div>
        }

        <!-- Legend -->
        <div class="px-4 py-2.5 flex items-center gap-5 flex-wrap" style="border-top: 1px solid var(--border);">
          @for (leg of legend; track leg.label) {
            <div class="flex items-center gap-1.5 text-xs" style="color: var(--text-muted);">
              <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" [style.background]="leg.color"></span>
              {{ leg.label }}
            </div>
          }
        </div>
      </div>

      <!-- Active table -->
      <div class="table-wrap">
        <div class="px-4 py-3" style="border-bottom: 1px solid var(--border);">
          <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Incidentes activos ({{ activeIncidents().length }})</h2>
        </div>
        @if (activeIncidents().length === 0) {
          <div class="p-12 text-center">
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
                  <td class="text-sm">{{ inc.clasificacion }}</td>
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
export class MapComponent implements OnInit, AfterViewInit, OnDestroy {
  private incidentsService = inject(IncidentsService);
  private techniciansService = inject(TechniciansService);
  private router = inject(Router);
  protected ws = inject(WebSocketService);

  loading = signal(false);
  incidents = signal<Incident[]>([]);
  tecnicos = signal<Tecnico[]>([]);
  private subs: Subscription[] = [];
  private wsReloadSubject = new Subject<void>();

  private map: L.Map | null = null;
  private markersLayer: L.LayerGroup | null = null;
  private resizeObserver: ResizeObserver | null = null;

  activeIncidents = computed(() => this.incidents().filter(i =>
    ['CLASIFICADO', 'ASIGNADO', 'EN_CAMINO', 'EN_PROCESO', 'PENDIENTE'].includes(i.estado)
  ));
  incidentsWithLocation = computed(() => this.activeIncidents().filter(i => i.latitud != null && i.longitud != null));
  tecnicosWithLocation = computed(() => this.tecnicos().filter(t => t.ubicacion_lat != null && t.ubicacion_lng != null));
  availableTecnicos = computed(() => this.tecnicos().filter(t => t.disponible));
  inRoute = computed(() => this.incidents().filter(i => i.estado === 'EN_CAMINO'));
  inProcess = computed(() => this.incidents().filter(i => i.estado === 'EN_PROCESO'));

  legend = [
    { color: '#f97316', label: 'Pendiente' },
    { color: '#3b82f6', label: 'Clasificado' },
    { color: '#a855f7', label: 'Asignado' },
    { color: '#eab308', label: 'En camino' },
    { color: '#14b8a6', label: 'En proceso' },
    { color: '#22c55e', label: 'Técnico libre' },
    { color: '#6b7280', label: 'Técnico ocupado' },
  ];

  constructor() {
    // Re-render markers whenever incident/technician data changes (poll + WS).
    effect(() => {
      const incs = this.incidentsWithLocation();
      const tecs = this.tecnicosWithLocation();
      this.renderMarkers(incs, tecs);
    });
  }

  ngOnInit(): void {
    this.reload();
    this.ws.connectGlobal();
    this.subs.push(
      interval(30000).pipe(switchMap(() => forkJoin({ incidents: this.incidentsService.getAll(), tecnicos: this.techniciansService.getAll() }))).subscribe(({ incidents, tecnicos }) => { this.incidents.set(incidents); this.tecnicos.set(tecnicos); }),
      this.wsReloadSubject.pipe(throttleTime(30000)).subscribe(() => this.reload()),
      this.ws.messages$.subscribe(() => this.wsReloadSubject.next()),
    );
  }

  ngAfterViewInit(): void {
    // 300ms delay so the container has real dimensions before Leaflet measures
    // it. On slow-loading prod bundles (Vercel) a 0ms tick renders a black map.
    setTimeout(() => this.initMap(), 300);
  }

  ngOnDestroy(): void {
    this.subs.forEach(s => s.unsubscribe());
    this.wsReloadSubject.complete();
    this.destroyMap();
  }

  reload(): void {
    forkJoin({ incidents: this.incidentsService.getAll(), tecnicos: this.techniciansService.getAll() }).subscribe({
      next: ({ incidents, tecnicos }) => { this.incidents.set(incidents); this.tecnicos.set(tecnicos); },
    });
  }

  private initMap(): void {
    if (this.map) return;
    const container = document.getElementById('operations-map');
    if (!container) return;

    this.map = L.map(container).setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(this.map);
    this.markersLayer = L.layerGroup().addTo(this.map);

    // Render whatever data is already loaded.
    this.renderMarkers(this.incidentsWithLocation(), this.tecnicosWithLocation());

    // Recalculate size once tiles/layout settle — fixes the black map in prod.
    setTimeout(() => { if (this.map) this.map.invalidateSize(); }, 400);

    // Keep the map sized correctly whenever the container changes dimensions.
    this.resizeObserver = new ResizeObserver(() => {
      if (this.map) this.map.invalidateSize();
    });
    this.resizeObserver.observe(container);
  }

  private renderMarkers(incidents: Incident[], tecnicos: Tecnico[]): void {
    if (!this.map || !this.markersLayer) return;
    this.markersLayer.clearLayers();

    for (const inc of incidents) {
      const color = ESTADO_COLOR[inc.estado] || '#6b7280';
      const marker = L.marker([inc.latitud!, inc.longitud!], { icon: incidentIcon(color, this.classIcon(inc.clasificacion)) });
      const popupHtml = `
        <div style="min-width:170px;font-family:inherit;">
          <p style="font-weight:700;margin:0 0 2px;">${inc.clasificacion}</p>
          <p style="font-size:11px;color:#555;margin:0 0 8px;">Estado: ${inc.estado.split('_').join(' ')}</p>
          <button class="popup-detail-btn" data-id="${inc.id_incidente}"
                  style="cursor:pointer;background:#3b82f6;color:#fff;border:none;border-radius:6px;padding:5px 10px;font-size:12px;font-weight:600;width:100%;">
            Ver detalle
          </button>
        </div>`;
      marker.bindPopup(popupHtml);
      this.markersLayer.addLayer(marker);
    }

    for (const t of tecnicos) {
      const marker = L.marker([t.ubicacion_lat!, t.ubicacion_lng!], { icon: tecnicoIcon(t.disponible) });
      marker.bindPopup(`<div style="font-family:inherit;"><p style="font-weight:700;margin:0;">${t.nombre_completo}</p><p style="font-size:11px;color:#555;margin:2px 0 0;">${t.disponible ? 'Disponible' : 'Ocupado'}</p></div>`);
      this.markersLayer.addLayer(marker);
    }

    // Wire the "Ver detalle" button inside Leaflet popups to Angular routing.
    this.map.off('popupopen');
    this.map.on('popupopen', (e: L.PopupEvent) => {
      const btn = e.popup.getElement()?.querySelector<HTMLButtonElement>('.popup-detail-btn');
      if (btn) {
        btn.addEventListener('click', () => {
          const id = btn.getAttribute('data-id');
          if (id) this.router.navigate(['/requests', id]);
        });
      }
    });
  }

  private destroyMap(): void {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
    if (this.map) {
      this.map.remove();
      this.map = null;
      this.markersLayer = null;
    }
  }

  classIcon(c: string): string {
    return { BATERIA: 'BA', LLANTA: 'LL', CHOQUE: 'CH', MOTOR: 'MO', OTROS: 'OT', INCIERTO: '?' }[c] || 'OT';
  }

  estadoBadge(e: string): string {
    const m: Record<string,string> = { PENDIENTE: 'badge-orange', CLASIFICADO: 'badge-blue', ASIGNADO: 'badge-purple', EN_CAMINO: 'badge-amber', EN_PROCESO: 'badge-teal', ATENDIDO: 'badge-green' };
    return m[e] || 'badge-gray';
  }

  prioridadBadge(p: string): string {
    return { ALTA: 'badge-red', MEDIA: 'badge-amber', BAJA: 'badge-green' }[p] || 'badge-gray';
  }
}
