import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { IncidentsService } from '../../core/services/incidents.service';
import { TechniciansService } from '../../core/services/technicians.service';
import { WebSocketService, WsMessage } from '../../core/services/websocket.service';
import { Incident, Tecnico } from '../../models';
import { environment } from '../../../environments/environment';

declare const L: any;

interface TechnicianLocation {
  lat: number;
  lng: number;
  tecnicoId?: string;
  timestamp?: string;
}

@Component({
  selector: 'app-request-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="space-y-5 fade-in max-w-5xl">
      <div class="flex items-center gap-3">
        <a routerLink="/requests" class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
           style="color: var(--text-muted); border: 1px solid var(--border);"
           onmouseenter="this.style.background='var(--bg-elevated)'"
           onmouseleave="this.style.background='transparent'">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </a>
        <div>
          <h1 class="page-title">Detalle del incidente</h1>
          @if (incident()) {
            <p class="page-subtitle font-mono">#{{ incident()!.id_incidente.substring(0,8).toUpperCase() }}</p>
          }
        </div>
      </div>

      @if (loading()) {
        <div class="grid grid-cols-3 gap-4">
          @for (_ of [1,2,3]; track $index) {
            <div class="h-48 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (incident()) {
        <!-- Status banner -->
        <div class="rounded-xl p-5 flex items-center justify-between"
             [style]="bannerStyle(incident()!.estado)">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                 style="background: rgba(0,0,0,0.15);">
              {{ stateIcon(incident()!.estado) }}
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest opacity-70">Estado actual</p>
              <p class="text-xl font-bold">{{ incident()!.estado.split('_').join(' ') }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-xs opacity-70 mb-1">Prioridad</p>
            <span [class]="'badge text-sm ' + prioridadBadge(incident()!.prioridad)">{{ incident()!.prioridad }}</span>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <!-- Left: main info -->
          <div class="lg:col-span-2 space-y-4">
            <!-- Details card -->
            <div class="surface p-5">
              <h2 class="text-sm font-semibold mb-4" style="color: var(--text-primary);">Información del incidente</h2>
              <dl class="space-y-3">
                @for (row of detailRows(); track row.label) {
                  <div class="flex items-start gap-3">
                    <dt class="text-xs w-28 flex-shrink-0 pt-0.5" style="color: var(--text-muted);">{{ row.label }}</dt>
                    <dd class="text-sm flex-1" style="color: var(--text-secondary);">{{ row.value }}</dd>
                  </div>
                }
                @if (incident()!.latitud && incident()!.longitud) {
                  <div class="flex items-start gap-3">
                    <dt class="text-xs w-28 flex-shrink-0 pt-0.5" style="color: var(--text-muted);">Ubicación</dt>
                    <dd class="flex items-center gap-2">
                      <span class="text-sm" style="color: var(--text-secondary);">
                        {{ incident()!.latitud!.toFixed(5) }}, {{ incident()!.longitud!.toFixed(5) }}
                      </span>
                      <a [href]="mapsUrl()" target="_blank" class="text-xs px-2 py-0.5 rounded"
                         style="color: var(--accent); background: var(--accent-glow);">
                        Maps →
                      </a>
                    </dd>
                  </div>
                }
              </dl>
            </div>

            <!-- AI Summary -->
            @if (incident()!.resumen_ia) {
              <div class="surface p-5" style="border-left: 3px solid var(--accent);">
                <div class="flex items-center gap-2 mb-3">
                  <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Analisis IA</h2>
                  <span class="badge-blue badge text-xs">Clasificación automática</span>
                </div>
                <p class="text-sm leading-relaxed" style="color: var(--text-secondary);">{{ aiResumenPrincipal() }}</p>
                @if (aiDanosVisibles()) {
                  <div class="mt-3 p-3 rounded-lg" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                    <p class="text-xs font-semibold uppercase tracking-wider mb-1" style="color: var(--text-muted);">Danos visibles</p>
                    <p class="text-sm" style="color: var(--text-secondary);">{{ aiDanosVisibles() }}</p>
                  </div>
                }
                @if (aiRecomendaciones()) {
                  <div class="mt-3 p-3 rounded-lg" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                    <p class="text-xs font-semibold uppercase tracking-wider mb-1" style="color: var(--text-muted);">Recomendaciones</p>
                    <p class="text-sm" style="color: var(--text-secondary);">{{ aiRecomendaciones() }}</p>
                  </div>
                }
                @if (aiConfianza()) {
                  <p class="text-xs mt-3" style="color: var(--text-muted);">Confianza IA: {{ aiConfianza() }}</p>
                }
              </div>
            }

            <!-- Evidence -->
            @if (incident()!.evidencias && incident()!.evidencias!.length > 0) {
              <div class="surface p-5">
                <h2 class="text-sm font-semibold mb-4" style="color: var(--text-primary);">
                  Evidencias <span class="text-xs font-normal ml-1" style="color: var(--text-muted);">({{ incident()!.evidencias!.length }})</span>
                </h2>
                <div class="space-y-3">
                  @for (ev of incident()!.evidencias!; track ev.id_evidencia) {
                    <div class="flex items-start gap-3 p-3 rounded-lg" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                      <div class="w-9 h-9 rounded-lg flex items-center justify-center text-lg flex-shrink-0"
                           style="background: var(--bg-base);">
                        {{ evidenceIcon(ev.tipo) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <span [class]="'badge text-xs mb-1.5 block w-fit ' + evidenceBadge(ev.tipo)">{{ ev.tipo }}</span>
                        @if (ev.texto_transcrito) {
                          <p class="text-sm" style="color: var(--text-secondary);">{{ ev.texto_transcrito }}</p>
                        }
                        @if (ev.tipo === 'IMAGEN') {
                          @if (evidenceUrl(ev.url_archivo)) {
                            <img [src]="evidenceUrl(ev.url_archivo)" alt="Evidencia"
                                 class="mt-2 rounded-lg max-h-48 object-cover" />
                          } @else {
                            <p class="text-xs mt-1" style="color: var(--text-muted);">Imagen no disponible</p>
                          }
                        }
                        @if (ev.tipo !== 'IMAGEN') {
                          @if (evidenceUrl(ev.url_archivo)) {
                            <a [href]="evidenceUrl(ev.url_archivo)" target="_blank"
                               class="text-xs" style="color: var(--accent);">
                              Ver archivo →
                            </a>
                          } @else {
                            <span class="text-xs" style="color: var(--text-muted);">Archivo no disponible</span>
                          }
                        }
                      </div>
                    </div>
                  }
                </div>
              </div>
            }

            <!-- Tracking / Location card -->
            @if (shouldShowTrackingSection()) {
              <div class="surface p-5">
                <div class="flex items-center justify-between mb-3">
                  <div>
                    <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Tracking del técnico</h2>
                    <p class="text-xs mt-1" style="color: var(--text-muted);">Ubicación en vivo recibida por WebSocket</p>
                  </div>
                  <span [class]="technicianLocation() ? 'badge-green badge' : 'badge-amber badge'">
                    {{ technicianLocation() ? 'En vivo' : 'Esperando GPS' }}
                  </span>
                </div>

                @if (technicianLocation()) {
                  <div id="tracking-map" class="rounded-xl overflow-hidden h-72" style="border: 1px solid var(--border);"></div>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
                    <div class="rounded-lg p-3" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                      <p class="text-xs mb-1" style="color: var(--text-muted);">Incidente</p>
                      <p class="text-xs font-mono" style="color: var(--text-secondary);">
                        {{ incident()!.latitud!.toFixed(5) }}, {{ incident()!.longitud!.toFixed(5) }}
                      </p>
                    </div>
                    <div class="rounded-lg p-3" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                      <p class="text-xs mb-1" style="color: var(--text-muted);">Técnico</p>
                      <p class="text-xs font-mono" style="color: var(--text-secondary);">
                        {{ technicianLocation()!.lat.toFixed(5) }}, {{ technicianLocation()!.lng.toFixed(5) }}
                      </p>
                    </div>
                  </div>
                } @else {
                  <div class="rounded-xl p-6 text-center" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                    <p class="text-sm font-medium" style="color: var(--text-secondary);">Esperando ubicación del técnico</p>
                    <p class="text-xs mt-1" style="color: var(--text-muted);">El mapa aparecerá cuando el técnico inicie el tracking GPS desde la app móvil.</p>
                  </div>
                }
              </div>
            } @else if (incident()!.latitud && incident()!.longitud) {
              <div class="surface p-5">
                <h2 class="text-sm font-semibold mb-3" style="color: var(--text-primary);">Ubicación GPS</h2>
                <div class="rounded-xl flex items-center justify-center h-40"
                     style="background: var(--bg-elevated); border: 1px solid var(--border);">
                  <div class="text-center">
                    <p class="text-sm font-mono" style="color: var(--text-secondary);">
                      {{ incident()!.latitud!.toFixed(5) }}, {{ incident()!.longitud!.toFixed(5) }}
                    </p>
                    <a [href]="mapsUrl()" target="_blank" class="btn-primary text-xs py-1.5 px-4 inline-flex mt-3">
                      Abrir Google Maps
                    </a>
                  </div>
                </div>
              </div>
            } @else {
              <div class="surface p-5">
                <h2 class="text-sm font-semibold mb-3" style="color: var(--text-primary);">Tracking del técnico</h2>
                <div class="rounded-xl p-6 text-center" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                  <p class="text-sm font-medium" style="color: var(--text-secondary);">Mapa no disponible</p>
                  <p class="text-xs mt-1" style="color: var(--text-muted);">Este incidente no tiene coordenadas GPS suficientes.</p>
                </div>
              </div>
            }
          </div>

          <!-- Right: Actions -->
          <div class="space-y-4">
            <!-- Accept / Reject -->
            @if (canAssign()) {
              <div class="surface p-5">
                <h3 class="text-sm font-semibold mb-4" style="color: var(--text-primary);">Tomar acción</h3>

                @if (actionError()) {
                  <div class="text-xs rounded-lg px-3 py-2 mb-3"
                       style="background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.2);">
                    {{ actionError() }}
                  </div>
                }
                @if (actionSuccess()) {
                  <div class="text-xs rounded-lg px-3 py-2 mb-3"
                       style="background: rgba(16,185,129,0.1); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.2);">
                    {{ actionSuccess() }}
                  </div>
                }

                <label class="block text-xs font-medium mb-1.5" style="color: var(--text-secondary);">Técnico asignado</label>
                <select [(ngModel)]="selectedTecnico" class="input mb-4 text-sm">
                  <option value="">Sin técnico específico</option>
                  @for (t of tecnicos(); track t.id_tecnico) {
                    <option [value]="t.id_tecnico" [disabled]="!t.disponible">
                      {{ t.nombre_completo }}{{ t.disponible ? '' : ' (Ocupado)' }}
                    </option>
                  }
                </select>

                <button (click)="accept()" [disabled]="actionLoading()" class="btn-success w-full mb-2">
                  @if (actionLoading()) { Procesando... } @else { Aceptar y asignar }
                </button>
                <button (click)="showReject.set(!showReject())" class="btn-ghost w-full text-sm">
                  Rechazar solicitud
                </button>

                @if (showReject()) {
                  <div class="mt-3 space-y-2">
                    <textarea [(ngModel)]="rejectReason" class="input resize-none text-sm" rows="3"
                              placeholder="Motivo del rechazo..."></textarea>
                    <button (click)="reject()" [disabled]="!rejectReason || actionLoading()" class="btn-danger w-full text-sm">
                      Confirmar rechazo
                    </button>
                  </div>
                }
              </div>
            }

            <!-- Status updates -->
            @if (canUpdateStatus()) {
              <div class="surface p-5">
                <h3 class="text-sm font-semibold mb-3" style="color: var(--text-primary);">Actualizar estado</h3>
                @for (s of nextStates(); track s.value) {
                  <button (click)="updateStatus(s.value)" [disabled]="actionLoading()"
                          class="w-full mb-2 py-2.5 px-4 rounded-lg text-sm font-medium transition-all text-left flex items-center gap-2"
                          [style]="s.style">
                    {{ s.label }}
                  </button>
                }
              </div>
            }

            <!-- Quick summary -->
            <div class="surface p-4 space-y-3">
              <h3 class="text-xs font-semibold uppercase tracking-widest" style="color: var(--text-muted);">Resumen</h3>
              @for (row of summaryRows(); track row.key) {
                <div class="flex items-center justify-between">
                  <span class="text-xs" style="color: var(--text-muted);">{{ row.key }}</span>
                  <span class="text-xs font-semibold" style="color: var(--text-secondary);">{{ row.val }}</span>
                </div>
              }
            </div>
          </div>
        </div>
      } @else {
        <div class="surface p-16 text-center">
          <p style="color: var(--text-muted);">No se pudo cargar el incidente</p>
          <a routerLink="/requests" class="btn-ghost text-sm mt-4 inline-flex">← Volver</a>
        </div>
      }
    </div>
  `,
})
export class RequestDetailComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private incidentsService = inject(IncidentsService);
  private techniciansService = inject(TechniciansService);
  private ws = inject(WebSocketService);

  loading = signal(true);
  incident = signal<Incident | null>(null);
  tecnicos = signal<Tecnico[]>([]);
  actionLoading = signal(false);
  actionError = signal<string | null>(null);
  actionSuccess = signal<string | null>(null);
  showReject = signal(false);
  technicianLocation = signal<TechnicianLocation | null>(null);
  selectedTecnico = '';
  rejectReason = '';

  private wsSub?: Subscription;
  private map: any = null;
  private incidentMarker: any = null;
  private technicianMarker: any = null;

  get incidentId(): string {
    return this.route.snapshot.paramMap.get('id') || '';
  }

  ngOnInit(): void {
    this.loadData();
    this.ws.connect(this.incidentId);
    this.wsSub = this.ws.messages$.subscribe(msg => this.handleWsMessage(msg));
    this.techniciansService.getAll().subscribe(t => this.tecnicos.set(t));
  }

  ngOnDestroy(): void {
    this.wsSub?.unsubscribe();
    this.ws.disconnect();
    this.destroyMap();
  }

  loadData(): void {
    this.loading.set(true);
    this.incidentsService.getById(this.incidentId).subscribe({
      next: (inc) => {
        this.incident.set(inc);
        this.loading.set(false);
        this.syncTrackingMap();
      },
      error: () => {
        this.incident.set(null);
        this.loading.set(false);
        this.destroyMap();
      },
    });
  }

  shouldShowTrackingSection(): boolean {
    const inc = this.incident();
    return inc?.latitud != null && inc?.longitud != null && ['EN_CAMINO', 'EN_PROCESO'].includes(inc.estado);
  }

  private handleWsMessage(msg: WsMessage): void {
    if (msg.tipo === 'ubicacion_tecnico') {
      const lat = this.toNumber(msg['lat'] ?? msg['latitud']);
      const lng = this.toNumber(msg['lng'] ?? msg['longitud']);
      if (lat == null || lng == null) return;

      this.technicianLocation.set({
        lat,
        lng,
        tecnicoId: msg['tecnico_id'] ?? msg['id_tecnico'],
        timestamp: msg['timestamp'],
      });
      this.syncTrackingMap();
      return;
    }

    if (msg.tipo === 'tracking_finalizado') {
      this.technicianLocation.set(null);
      this.destroyMap();
      this.loadData();
      return;
    }

    if (msg.tipo !== 'conectado') this.loadData();
  }

  private toNumber(value: unknown): number | null {
    if (typeof value === 'number') return value;
    if (typeof value === 'string') {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : null;
    }
    return null;
  }

  private syncTrackingMap(): void {
    if (!this.shouldShowTrackingSection() || !this.technicianLocation()) {
      this.destroyMap();
      return;
    }
    setTimeout(() => this.renderTrackingMap(), 0);
  }

  private renderTrackingMap(): void {
    const inc = this.incident();
    const tech = this.technicianLocation();
    const container = document.getElementById('tracking-map');
    if (inc?.latitud == null || inc?.longitud == null || !tech || !container || typeof L === 'undefined') return;

    const incidentLatLng: [number, number] = [inc.latitud, inc.longitud];
    const techLatLng: [number, number] = [tech.lat, tech.lng];

    if (!this.map) {
      this.map = L.map(container, { zoomControl: true }).setView(techLatLng, 14);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(this.map);
      this.incidentMarker = L.marker(incidentLatLng, { icon: this.incidentIcon() })
        .addTo(this.map)
        .bindPopup('Incidente');
      this.technicianMarker = L.marker(techLatLng, { icon: this.technicianIcon() })
        .addTo(this.map)
        .bindPopup('Técnico');
    } else {
      this.incidentMarker?.setLatLng(incidentLatLng);
      this.technicianMarker?.setLatLng(techLatLng);
    }

    const bounds = L.latLngBounds([incidentLatLng, techLatLng]);
    this.map.fitBounds(bounds, { padding: [28, 28], maxZoom: 16 });
    this.map.invalidateSize();
  }

  private destroyMap(): void {
    if (this.map) {
      this.map.remove();
      this.map = null;
      this.incidentMarker = null;
      this.technicianMarker = null;
    }
  }

  private incidentIcon(): any {
    return L.divIcon({
      html: '<div style="width:18px;height:18px;border-radius:50%;background:#ef4444;border:3px solid white;box-shadow:0 2px 10px rgba(0,0,0,.4);"></div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
      className: '',
    });
  }

  private technicianIcon(): any {
    return L.divIcon({
      html: '<div style="width:28px;height:28px;border-radius:50%;background:#2563eb;border:3px solid white;box-shadow:0 0 0 8px rgba(37,99,235,.22),0 2px 12px rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;color:white;font-size:12px;font-weight:700;">T</div>',
      iconSize: [34, 34],
      iconAnchor: [17, 17],
      className: '',
    });
  }

  detailRows() {
    const inc = this.incident();
    if (!inc) return [];
    return [
      { label: 'Clasificación', value: inc.clasificacion },
      { label: 'Prioridad', value: inc.prioridad },
      { label: 'Fecha', value: new Date(inc.fecha_creacion).toLocaleString('es-BO') },
      ...(inc.tiempo_estimado_llegada_minutos ? [{ label: 'ETA', value: `${inc.tiempo_estimado_llegada_minutos} minutos` }] : []),
    ];
  }

  summaryRows() {
    const inc = this.incident();
    if (!inc) return [];
    return [
      { key: 'Estado', val: inc.estado.split('_').join(' ') },
      { key: 'Prioridad', val: inc.prioridad },
      { key: 'Tipo', val: inc.clasificacion },
      { key: 'Evidencias', val: String(inc.evidencias?.length ?? 0) },
    ];
  }

  canAssign(): boolean {
    return ['CLASIFICADO', 'PENDIENTE'].includes(this.incident()?.estado || '');
  }

  canUpdateStatus(): boolean {
    return ['ASIGNADO', 'EN_CAMINO', 'EN_PROCESO'].includes(this.incident()?.estado || '');
  }

  nextStates() {
    const e = this.incident()?.estado;
    if (e === 'ASIGNADO') return [{ value: 'EN_CAMINO', label: 'Marcar en camino', style: 'background:rgba(245,158,11,0.1);color:#fcd34d;border:1px solid rgba(245,158,11,0.2)' }];
    if (e === 'EN_CAMINO') return [{ value: 'EN_PROCESO', label: 'Iniciar servicio', style: 'background:rgba(20,184,166,0.1);color:#5eead4;border:1px solid rgba(20,184,166,0.2)' }];
    if (e === 'EN_PROCESO') return [{ value: 'ATENDIDO', label: 'Marcar como atendido', style: 'background:rgba(16,185,129,0.1);color:#6ee7b7;border:1px solid rgba(16,185,129,0.2)' }];
    return [];
  }

  accept(): void {
    this.actionLoading.set(true);
    this.actionError.set(null);
    this.incidentsService.assign(this.incidentId, { id_tecnico: this.selectedTecnico || undefined }).subscribe({
      next: () => {
        this.actionSuccess.set('Incidente aceptado correctamente');
        this.actionLoading.set(false);
        this.loadData();
        setTimeout(() => this.actionSuccess.set(null), 3000);
      },
      error: (err) => { this.actionError.set(err.error?.detail || 'Error al asignar'); this.actionLoading.set(false); },
    });
  }

  reject(): void {
    this.actionLoading.set(true);
    this.incidentsService.rejectAssignment(this.incidentId, this.rejectReason).subscribe({
      next: () => {
        this.actionLoading.set(false);
        this.showReject.set(false);
        setTimeout(() => this.router.navigate(['/requests']), 800);
      },
      error: (err) => { this.actionError.set(err.error?.detail || 'Error'); this.actionLoading.set(false); },
    });
  }

  updateStatus(estado: string): void {
    this.actionLoading.set(true);
    this.incidentsService.updateStatus(this.incidentId, estado).subscribe({
      next: () => { this.actionLoading.set(false); this.loadData(); },
      error: (err) => { this.actionError.set(err.error?.detail || 'Error'); this.actionLoading.set(false); },
    });
  }

  mapsUrl(): string {
    const inc = this.incident();
    return `https://maps.google.com/?q=${inc?.latitud},${inc?.longitud}`;
  }
  aiResumenPrincipal(): string {
    const raw = this.incident()?.resumen_ia || '';
    if (!raw) return '';
    return raw
      .split('\n')
      .filter(line =>
        !line.startsWith('Recomendaciones:') &&
        !line.startsWith('Danos visibles:') &&
        !line.startsWith('Confianza IA:')
      )
      .join(' ')
      .trim();
  }

  aiRecomendaciones(): string {
    return this.extractAiSection('Recomendaciones:');
  }

  aiDanosVisibles(): string {
    return this.extractAiSection('Danos visibles:');
  }

  aiConfianza(): string {
    return this.extractAiSection('Confianza IA:');
  }

  private extractAiSection(prefix: string): string {
    const raw = this.incident()?.resumen_ia || '';
    if (!raw) return '';
    const line = raw
      .split('\n')
      .map(x => x.trim())
      .find(x => x.startsWith(prefix));
    return line ? line.replace(prefix, '').trim() : '';
  }
  bannerStyle(e: string): string {
    const styles: Record<string,string> = {
      PENDIENTE: 'background:linear-gradient(135deg,rgba(249,115,22,0.15),rgba(249,115,22,0.08));color:#fdba74;border:1px solid rgba(249,115,22,0.2)',
      CLASIFICADO: 'background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(59,130,246,0.08));color:#93c5fd;border:1px solid rgba(59,130,246,0.2)',
      ASIGNADO: 'background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(139,92,246,0.08));color:#c4b5fd;border:1px solid rgba(139,92,246,0.2)',
      EN_CAMINO: 'background:linear-gradient(135deg,rgba(245,158,11,0.15),rgba(245,158,11,0.08));color:#fcd34d;border:1px solid rgba(245,158,11,0.2)',
      EN_PROCESO: 'background:linear-gradient(135deg,rgba(20,184,166,0.15),rgba(20,184,166,0.08));color:#5eead4;border:1px solid rgba(20,184,166,0.2)',
      ATENDIDO: 'background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(16,185,129,0.08));color:#6ee7b7;border:1px solid rgba(16,185,129,0.2)',
      CANCELADO: 'background:linear-gradient(135deg,rgba(239,68,68,0.15),rgba(239,68,68,0.08));color:#fca5a5;border:1px solid rgba(239,68,68,0.2)',
    };
    return styles[e] || 'background:var(--bg-elevated);color:var(--text-secondary);border:1px solid var(--border)';
  }

  stateIcon(e: string): string {
    return { PENDIENTE: 'PE', CLASIFICADO: 'CL', ASIGNADO: 'AS', EN_CAMINO: 'EC', EN_PROCESO: 'EP', ATENDIDO: 'AT', CANCELADO: 'CA' }[e] || '?';
  }

  prioridadBadge(p: string): string {
    return { ALTA: 'badge-red', MEDIA: 'badge-amber', BAJA: 'badge-green' }[p] || 'badge-gray';
  }

  evidenceIcon(t: string): string {
    return { IMAGEN: 'IMG', AUDIO: 'AUD', TEXTO: 'TXT' }[t] || 'FILE';
  }

  evidenceBadge(t: string): string {
    return { IMAGEN: 'badge-blue', AUDIO: 'badge-orange', TEXTO: 'badge-gray' }[t] || 'badge-gray';
  }

  evidenceUrl(url: string | undefined | null): string {
    if (!url || url.startsWith('temporal:')) return '';
    if (url.startsWith('http')) return url;
    return `${environment.apiUrl.replace('/api/v1', '')}${url}`;
  }
}



