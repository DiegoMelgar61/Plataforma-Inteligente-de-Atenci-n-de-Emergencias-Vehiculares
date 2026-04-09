import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { IncidentsService } from '../../core/services/incidents.service';
import { TechniciansService } from '../../core/services/technicians.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { Incident, Tecnico } from '../../models';

@Component({
  selector: 'app-request-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="max-w-4xl mx-auto">
      <!-- Back -->
      <a routerLink="/requests" class="flex items-center gap-2 text-gray-500 hover:text-gray-700 text-sm mb-6">
        ← Volver a solicitudes
      </a>

      @if (loading()) {
        <div class="space-y-4">
          @for (_ of [1,2,3]; track $index) {
            <div class="h-32 bg-gray-100 rounded-xl animate-pulse"></div>
          }
        </div>
      } @else if (incident()) {
        <!-- Status Banner -->
        <div [class]="'rounded-xl p-5 mb-6 border ' + bannerClass(incident()!.estado)">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-3xl">{{ stateIcon(incident()!.estado) }}</span>
              <div>
                <p class="text-xs font-medium opacity-70 uppercase tracking-wide">Estado actual</p>
                <p class="text-xl font-bold">{{ incident()!.estado.split('_').join(' ') }}</p>
              </div>
            </div>
            <span [class]="'badge text-sm ' + prioridadBadge(incident()!.prioridad)">
              Prioridad {{ incident()!.prioridad }}
            </span>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Main info -->
          <div class="lg:col-span-2 space-y-4">
            <!-- Incident info -->
            <div class="card">
              <h2 class="font-semibold text-gray-900 mb-4">Información del incidente</h2>
              <dl class="space-y-3">
                <div class="flex gap-4">
                  <dt class="text-sm text-gray-500 w-32 flex-shrink-0">ID</dt>
                  <dd class="text-sm font-mono font-medium"># {{ incident()!.id_incidente.substring(0,8).toUpperCase() }}</dd>
                </div>
                <div class="flex gap-4">
                  <dt class="text-sm text-gray-500 w-32 flex-shrink-0">Clasificación</dt>
                  <dd class="text-sm font-medium flex items-center gap-2">
                    <span>{{ classIcon(incident()!.clasificacion) }}</span>
                    {{ incident()!.clasificacion }}
                  </dd>
                </div>
                <div class="flex gap-4">
                  <dt class="text-sm text-gray-500 w-32 flex-shrink-0">Fecha</dt>
                  <dd class="text-sm">{{ formatDate(incident()!.fecha_creacion) }}</dd>
                </div>
                @if (incident()!.latitud && incident()!.longitud) {
                  <div class="flex gap-4">
                    <dt class="text-sm text-gray-500 w-32 flex-shrink-0">Ubicación</dt>
                    <dd class="text-sm">
                      {{ incident()!.latitud!.toFixed(5) }}, {{ incident()!.longitud!.toFixed(5) }}
                      <a [href]="mapsUrl(incident()!)" target="_blank"
                         class="ml-2 text-blue-600 hover:underline text-xs">Ver en mapa →</a>
                    </dd>
                  </div>
                }
                @if (incident()!.tiempo_estimado_llegada_minutos) {
                  <div class="flex gap-4">
                    <dt class="text-sm text-gray-500 w-32 flex-shrink-0">ETA</dt>
                    <dd class="text-sm font-medium">{{ incident()!.tiempo_estimado_llegada_minutos }} minutos</dd>
                  </div>
                }
              </dl>
            </div>

            <!-- AI Summary -->
            @if (incident()!.resumen_ia) {
              <div class="card border-l-4 border-blue-500">
                <div class="flex items-center gap-2 mb-3">
                  <span class="text-xl">🤖</span>
                  <h2 class="font-semibold text-gray-900">Análisis de IA</h2>
                </div>
                <p class="text-gray-700 text-sm leading-relaxed">{{ incident()!.resumen_ia }}</p>
              </div>
            }

            <!-- Evidence -->
            @if (incident()!.evidencias && incident()!.evidencias!.length > 0) {
              <div class="card">
                <h2 class="font-semibold text-gray-900 mb-4">Evidencias ({{ incident()!.evidencias!.length }})</h2>
                <div class="space-y-3">
                  @for (ev of incident()!.evidencias!; track ev.id_evidencia) {
                    <div class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <div [class]="'w-10 h-10 rounded-lg flex items-center justify-center text-xl flex-shrink-0 ' + evidenceBg(ev.tipo)">
                        {{ evidenceIcon(ev.tipo) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-xs font-medium text-gray-600 uppercase">{{ ev.tipo }}</p>
                        @if (ev.texto_transcrito) {
                          <p class="text-sm text-gray-700 mt-1">{{ ev.texto_transcrito }}</p>
                        }
                        @if (ev.url_archivo && ev.tipo === 'IMAGEN') {
                          <img [src]="ev.url_archivo" alt="Evidencia" class="mt-2 rounded-lg max-h-40 object-cover" />
                        }
                        @if (ev.url_archivo && ev.tipo !== 'IMAGEN') {
                          <a [href]="ev.url_archivo" target="_blank" class="text-xs text-blue-600 hover:underline mt-1 block">
                            Ver archivo →
                          </a>
                        }
                      </div>
                    </div>
                  }
                </div>
              </div>
            }

            <!-- Map placeholder -->
            @if (incident()!.latitud && incident()!.longitud) {
              <div class="card p-0 overflow-hidden">
                <div class="bg-gray-100 h-48 flex items-center justify-center relative">
                  <div class="text-center">
                    <div class="text-4xl mb-2">📍</div>
                    <p class="text-gray-600 text-sm font-medium">
                      {{ incident()!.latitud!.toFixed(5) }}, {{ incident()!.longitud!.toFixed(5) }}
                    </p>
                    <a [href]="mapsUrl(incident()!)" target="_blank"
                       class="mt-2 btn-primary inline-block text-xs py-1.5 px-3">
                      Abrir en Google Maps
                    </a>
                  </div>
                </div>
              </div>
            }
          </div>

          <!-- Sidebar actions -->
          <div class="space-y-4">
            <!-- Assign -->
            @if (canAssign()) {
              <div class="card">
                <h3 class="font-semibold text-gray-900 mb-3">Asignar técnico</h3>
                @if (actionError()) {
                  <div class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-2 mb-3 text-xs">
                    {{ actionError() }}
                  </div>
                }
                @if (actionSuccess()) {
                  <div class="bg-green-50 border border-green-200 text-green-700 rounded-lg p-2 mb-3 text-xs">
                    {{ actionSuccess() }}
                  </div>
                }
                <select [(ngModel)]="selectedTecnico" class="input-field mb-3">
                  <option value="">Sin técnico asignado</option>
                  @for (t of tecnicos(); track t.id_tecnico) {
                    <option [value]="t.id_tecnico" [disabled]="!t.disponible">
                      {{ t.nombre_completo }} {{ t.disponible ? '' : '(Ocupado)' }}
                    </option>
                  }
                </select>
                <button (click)="accept()" [disabled]="actionLoading()" class="btn-success w-full mb-2">
                  @if (actionLoading()) { Procesando... } @else { ✅ Aceptar y asignar }
                </button>
                <button (click)="showReject.set(true)" class="btn-danger w-full">
                  ❌ Rechazar
                </button>

                @if (showReject()) {
                  <div class="mt-3">
                    <textarea
                      [(ngModel)]="rejectReason"
                      class="input-field resize-none"
                      rows="3"
                      placeholder="Motivo del rechazo..."
                    ></textarea>
                    <button (click)="reject()" [disabled]="!rejectReason || actionLoading()"
                      class="btn-danger w-full mt-2">
                      Confirmar rechazo
                    </button>
                  </div>
                }
              </div>
            }

            <!-- Status update -->
            @if (canUpdateStatus()) {
              <div class="card">
                <h3 class="font-semibold text-gray-900 mb-3">Actualizar estado</h3>
                @for (s of nextStates(); track s.value) {
                  <button (click)="updateStatus(s.value)" [disabled]="actionLoading()"
                    [class]="'w-full mb-2 py-2 px-3 rounded-lg text-sm font-medium transition-colors ' + s.cls">
                    {{ s.label }}
                  </button>
                }
              </div>
            }

            <!-- Quick info -->
            <div class="card">
              <h3 class="font-semibold text-gray-900 mb-3">Resumen rápido</h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-500">Estado</span>
                  <span class="font-medium">{{ incident()!.estado.split('_').join(' ') }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">Prioridad</span>
                  <span [class]="'font-medium ' + priorityColor(incident()!.prioridad)">{{ incident()!.prioridad }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">Clasificación</span>
                  <span class="font-medium">{{ incident()!.clasificacion }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      } @else {
        <div class="card text-center py-16">
          <div class="text-5xl mb-4">⚠️</div>
          <p class="text-gray-500">No se pudo cargar el incidente</p>
          <a routerLink="/requests" class="btn-primary mt-4 inline-block">Volver</a>
        </div>
      }
    </div>
  `,
})
export class RequestDetailComponent implements OnInit {
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
  selectedTecnico = '';
  rejectReason = '';

  get incidentId(): string {
    return this.route.snapshot.paramMap.get('id') || '';
  }

  ngOnInit(): void {
    this.loadData();
    this.ws.connect(this.incidentId);
    this.ws.messages$.subscribe(() => this.loadData());
    this.techniciansService.getAll().subscribe(t => this.tecnicos.set(t));
  }

  loadData(): void {
    this.loading.set(true);
    this.incidentsService.getById(this.incidentId).subscribe({
      next: (inc) => { this.incident.set(inc); this.loading.set(false); },
      error: () => { this.incident.set(null); this.loading.set(false); },
    });
  }

  canAssign(): boolean {
    return ['CLASIFICADO', 'PENDIENTE'].includes(this.incident()?.estado || '');
  }

  canUpdateStatus(): boolean {
    return ['ASIGNADO', 'EN_CAMINO', 'EN_PROCESO'].includes(this.incident()?.estado || '');
  }

  nextStates(): { value: string; label: string; cls: string }[] {
    const estado = this.incident()?.estado;
    if (estado === 'ASIGNADO') return [{ value: 'EN_CAMINO', label: '🚗 En camino', cls: 'bg-amber-100 text-amber-700 hover:bg-amber-200' }];
    if (estado === 'EN_CAMINO') return [{ value: 'EN_PROCESO', label: '🔧 En proceso', cls: 'bg-teal-100 text-teal-700 hover:bg-teal-200' }];
    if (estado === 'EN_PROCESO') return [{ value: 'ATENDIDO', label: '✅ Atendido', cls: 'bg-green-100 text-green-700 hover:bg-green-200' }];
    return [];
  }

  accept(): void {
    this.actionLoading.set(true);
    this.actionError.set(null);
    this.incidentsService.assign(this.incidentId, {
      id_tecnico: this.selectedTecnico || undefined,
    }).subscribe({
      next: () => {
        this.actionSuccess.set('Incidente aceptado y asignado correctamente');
        this.actionLoading.set(false);
        this.loadData();
        setTimeout(() => this.actionSuccess.set(null), 3000);
      },
      error: (err) => {
        this.actionError.set(err.error?.detail || 'Error al asignar');
        this.actionLoading.set(false);
      },
    });
  }

  reject(): void {
    this.actionLoading.set(true);
    this.incidentsService.rejectAssignment(this.incidentId, this.rejectReason).subscribe({
      next: () => {
        this.actionSuccess.set('Solicitud rechazada');
        this.actionLoading.set(false);
        this.showReject.set(false);
        this.loadData();
        setTimeout(() => this.router.navigate(['/requests']), 1500);
      },
      error: (err) => {
        this.actionError.set(err.error?.detail || 'Error al rechazar');
        this.actionLoading.set(false);
      },
    });
  }

  updateStatus(estado: string): void {
    this.actionLoading.set(true);
    this.incidentsService.updateStatus(this.incidentId, estado).subscribe({
      next: () => {
        this.actionLoading.set(false);
        this.loadData();
      },
      error: (err) => {
        this.actionError.set(err.error?.detail || 'Error al actualizar');
        this.actionLoading.set(false);
      },
    });
  }

  mapsUrl(inc: Incident): string {
    return `https://maps.google.com/?q=${inc.latitud},${inc.longitud}`;
  }

  bannerClass(e: string): string {
    const map: Record<string, string> = {
      PENDIENTE: 'bg-orange-50 border-orange-200 text-orange-800',
      CLASIFICADO: 'bg-blue-50 border-blue-200 text-blue-800',
      ASIGNADO: 'bg-purple-50 border-purple-200 text-purple-800',
      EN_CAMINO: 'bg-amber-50 border-amber-200 text-amber-800',
      EN_PROCESO: 'bg-teal-50 border-teal-200 text-teal-800',
      ATENDIDO: 'bg-green-50 border-green-200 text-green-800',
      CANCELADO: 'bg-red-50 border-red-200 text-red-800',
    };
    return map[e] || 'bg-gray-50 border-gray-200 text-gray-800';
  }

  stateIcon(e: string): string {
    const map: Record<string, string> = {
      PENDIENTE: '⏳', CLASIFICADO: '🔍', ASIGNADO: '📋',
      EN_CAMINO: '🚗', EN_PROCESO: '🔧', ATENDIDO: '✅', CANCELADO: '❌',
    };
    return map[e] || '❓';
  }

  prioridadBadge(p: string): string {
    return { ALTA: 'bg-red-100 text-red-700', MEDIA: 'bg-amber-100 text-amber-700', BAJA: 'bg-green-100 text-green-700' }[p] || 'bg-gray-100 text-gray-600';
  }

  priorityColor(p: string): string {
    return { ALTA: 'text-red-600', MEDIA: 'text-amber-600', BAJA: 'text-green-600' }[p] || 'text-gray-600';
  }

  classIcon(c: string): string {
    return { BATERIA: '🔋', LLANTA: '🔄', CHOQUE: '💥', MOTOR: '⚙️', OTROS: '🚗', INCIERTO: '❓' }[c] || '🚗';
  }

  evidenceIcon(t: string): string {
    return { IMAGEN: '🖼️', AUDIO: '🎵', TEXTO: '📝' }[t] || '📎';
  }

  evidenceBg(t: string): string {
    return { IMAGEN: 'bg-blue-100', AUDIO: 'bg-orange-100', TEXTO: 'bg-gray-100' }[t] || 'bg-gray-100';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleString('es-BO');
  }
}
