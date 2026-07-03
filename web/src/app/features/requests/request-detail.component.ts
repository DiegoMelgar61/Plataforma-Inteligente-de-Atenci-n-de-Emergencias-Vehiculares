import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { IncidentsService } from './incidents.service';
import { TechniciansService } from '../technicians/technicians.service';
import { WebSocketService, WsMessage } from '../../core/services/websocket.service';
import { AuthService } from '../../core/services/auth.service';
import { Asignacion, CotizacionDetalle, Incident, Tecnico } from '../../models';
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
              <div class="surface overflow-hidden" style="border-left: 3px solid var(--accent); background: linear-gradient(135deg, var(--bg-surface), var(--bg-elevated));">
                <div class="p-5 space-y-5">
                  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                           style="background: var(--accent-glow); color: var(--accent); border: 1px solid var(--border);">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3c-1.2 0-2.2.7-2.7 1.7A3.4 3.4 0 0 0 5 8a3.6 3.6 0 0 0 .4 6.9A3.8 3.8 0 0 0 9 20c1 0 1.9-.4 2.5-1.1.6.7 1.5 1.1 2.5 1.1a3.8 3.8 0 0 0 3.6-5.1A3.6 3.6 0 0 0 18 8a3.4 3.4 0 0 0-4.3-3.3A3 3 0 0 0 12 3Z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9h.01M15 9h.01M9.5 14c.8.7 1.7 1 2.5 1s1.7-.3 2.5-1"/>
                        </svg>
                      </div>
                      <div>
                        <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Analisis por IA</h2>
                        <p class="text-xs" style="color: var(--text-muted);">Resultado de clasificacion automatica</p>
                      </div>
                    </div>
                    <div class="flex flex-wrap items-center gap-2">
                      <span class="badge text-xs" style="background: var(--accent-glow); color: var(--accent); border: 1px solid var(--accent);">Clasificacion automatica</span>
                      @if (aiConfianza()) {
                        <span class="badge text-xs"
                              [style.background]="+aiConfianza() >= 0.75 ? 'var(--success)' : (+aiConfianza() >= 0.5 ? 'var(--warning)' : 'var(--danger)')"
                              style="color: white; border: 0;">
                          Confianza {{ (+aiConfianza() * 100).toFixed(0) }}%
                        </span>
                      }
                    </div>
                  </div>

                  <div class="flex justify-center">
                    <div class="inline-flex items-center gap-3 px-5 py-3 rounded-xl shadow-lg"
                         style="background: linear-gradient(135deg, var(--accent), var(--accent-glow)); color: white; border-radius: 12px; box-shadow: 0 18px 40px rgba(0,0,0,0.22);">
                      @switch (incident()!.clasificacion) {
                        @case ('BATERIA') {
                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h13a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2Zm15 3h1v2h-1M7 12h5m-2.5-2.5v5"/>
                          </svg>
                        }
                        @case ('LLANTA') {
                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <circle cx="12" cy="12" r="8" stroke-width="2"/>
                            <circle cx="12" cy="12" r="3" stroke-width="2"/>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v5m0 6v5m8-8h-5M9 12H4m3.6-5.6 3.5 3.5m2.8 2.8 3.5 3.5m0-10.6-3.5 3.5m-2.8 2.8-3.5 3.5"/>
                          </svg>
                        }
                        @case ('CHOQUE') {
                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3 2.8 19a1.5 1.5 0 0 0 1.3 2.2h15.8a1.5 1.5 0 0 0 1.3-2.2L12 3Zm0 6v5m0 4h.01"/>
                          </svg>
                        }
                        @case ('MOTOR') {
                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.3 4.3 11 2h2l.7 2.3a7.8 7.8 0 0 1 1.8.8l2.1-1.1 1.4 1.4-1.1 2.1c.4.6.6 1.2.8 1.8L21 10v2l-2.3.7a7.8 7.8 0 0 1-.8 1.8l1.1 2.1-1.4 1.4-2.1-1.1c-.6.4-1.2.6-1.8.8L13 20h-2l-.7-2.3a7.8 7.8 0 0 1-1.8-.8L6.4 18 5 16.6l1.1-2.1a7.8 7.8 0 0 1-.8-1.8L3 12v-2l2.3-.7c.2-.6.4-1.2.8-1.8L5 5.4 6.4 4l2.1 1.1c.6-.4 1.2-.6 1.8-.8Z"/>
                            <circle cx="12" cy="11" r="3" stroke-width="2"/>
                          </svg>
                        }
                        @case ('INCIERTO') {
                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 18h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 8.5 4.5 4.5 0 0 0 7 18Z"/>
                          </svg>
                        }
                        @default {
                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.1 9a3 3 0 1 1 4.6 2.5c-.9.5-1.7 1.1-1.7 2.5m0 3h.01M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z"/>
                          </svg>
                        }
                      }
                      <span class="text-lg font-bold tracking-wide">{{ incident()!.clasificacion }}</span>
                    </div>
                  </div>

                  <div class="p-4 rounded-xl" style="background: var(--bg-base); border: 1px solid var(--border);">
                    <p class="text-sm" style="color: var(--text-secondary); line-height: 1.7;">{{ aiResumenPrincipal() }}</p>
                  </div>

                  @if (aiDanosVisibles() || aiRecomendaciones()) {
                    <div class="grid grid-cols-1 gap-3" [ngClass]="aiDanosVisibles() && aiRecomendaciones() ? 'md:grid-cols-2' : ''">
                      @if (aiDanosVisibles()) {
                        <div class="p-4 rounded-xl" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                          <div class="flex items-center gap-2 mb-2" style="color: var(--warning);">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.3-4.3m2.3-5.2a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Z"/>
                            </svg>
                            <p class="text-xs font-semibold uppercase tracking-wider">Danos visibles</p>
                          </div>
                          <p class="text-sm leading-relaxed" style="color: var(--text-secondary);">{{ aiDanosVisibles() }}</p>
                        </div>
                      }
                      @if (aiRecomendaciones()) {
                        <div class="p-4 rounded-xl" style="background: var(--bg-elevated); border: 1px solid var(--border);">
                          <div class="flex items-center gap-2 mb-2" style="color: var(--success);">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12.5 11 15l4.5-5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
                            </svg>
                            <p class="text-xs font-semibold uppercase tracking-wider">Recomendaciones</p>
                          </div>
                          <p class="text-sm leading-relaxed" style="color: var(--text-secondary);">{{ aiRecomendaciones() }}</p>
                        </div>
                      }
                    </div>
                  }
                </div>
                <div class="px-5 py-3 border-t text-right" style="border-color: var(--border);">
                  <p class="text-xs" style="color: var(--text-muted);">Procesado automaticamente por Gemini AI</p>
                </div>
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
                <div id="static-location-map" class="rounded-xl overflow-hidden"
                     style="height: 220px; width: 100%; border: 1px solid var(--border);"></div>
                <div class="flex items-center justify-between mt-3">
                  <p class="text-xs font-mono" style="color: var(--text-secondary);">
                    {{ incident()!.latitud!.toFixed(5) }}, {{ incident()!.longitud!.toFixed(5) }}
                  </p>
                  <a [href]="mapsUrl()" target="_blank" class="btn-primary text-xs py-1.5 px-4 inline-flex">
                    Abrir Google Maps
                  </a>
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

            @if (showQuotationCard()) {
              <div class="surface p-5" style="border-left: 3px solid var(--accent);">
                <div class="flex items-start justify-between gap-3 mb-4">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-widest mb-1" style="color: var(--text-muted);">Cotizacion</p>
                    <h3 class="text-sm font-semibold" style="color: var(--text-primary);">Propuesta del taller</h3>
                  </div>
                  @if (canViewQuotationStatus()) {
                    <span [class]="quotationStatusBadge()">{{ quotationStatusLabel() }}</span>
                  }
                </div>

                @if (hasQuotation()) {
                  <div class="rounded-xl p-4 mb-4" style="background: linear-gradient(135deg, var(--accent-glow), var(--bg-elevated)); border: 1px solid var(--border);">
                    <p class="text-xs mb-1" style="color: var(--text-muted);">Monto cotizado</p>
                    <p class="text-2xl font-bold" style="color: var(--text-primary);">Bs. {{ quotationAmount() | number:'1.2-2' }}</p>
                    <div class="grid grid-cols-1 gap-3 mt-4">
                      @if (quotationTime()) {
                        <div>
                          <p class="text-xs" style="color: var(--text-muted);">Tiempo estimado</p>
                          <p class="text-sm font-semibold" style="color: var(--text-secondary);">{{ quotationTime() }} min</p>
                        </div>
                      }
                      @if (quotationNotes()) {
                        <div>
                          <p class="text-xs" style="color: var(--text-muted);">Notas</p>
                          <p class="text-sm leading-relaxed" style="color: var(--text-secondary);">{{ quotationNotes() }}</p>
                        </div>
                      }
                    </div>
                  </div>
                } @else {
                  <div class="rounded-xl p-4 mb-4" style="background: var(--bg-elevated); border: 1px dashed var(--border);">
                    <p class="text-sm font-medium" style="color: var(--text-secondary);">Sin cotizacion enviada</p>
                    <p class="text-xs mt-1" style="color: var(--text-muted);">El taller puede proponer monto, tiempo y notas para que el cliente decida.</p>
                  </div>
                }

                @if (auth.isTaller()) {
                  @if (quotationError()) {
                    <div class="text-xs rounded-lg px-3 py-2 mb-3" style="background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.2);">
                      {{ quotationError() }}
                    </div>
                  }
                  @if (quotationSuccess()) {
                    <div class="text-xs rounded-lg px-3 py-2 mb-3" style="background: rgba(16,185,129,0.1); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.2);">
                      {{ quotationSuccess() }}
                    </div>
                  }

                  <div class="space-y-3 pt-1">
                    <div>
                      <label class="block text-xs font-medium mb-1" style="color: var(--text-muted);">Monto</label>
                      <input type="number" min="0" step="0.01" [(ngModel)]="quotationMonto" class="input text-sm" placeholder="Ej. 180.00" />
                    </div>
                    <div>
                      <label class="block text-xs font-medium mb-1" style="color: var(--text-muted);">Tiempo estimado (min)</label>
                      <input type="number" min="0" step="1" [(ngModel)]="quotationTiempo" class="input text-sm" placeholder="Ej. 45" />
                    </div>
                    <div>
                      <label class="block text-xs font-medium mb-1" style="color: var(--text-muted);">Notas</label>
                      <textarea [(ngModel)]="quotationNotas" class="input resize-none text-sm" rows="3" placeholder="Detalle del servicio propuesto..."></textarea>
                    </div>
                    <button (click)="submitQuotation()" [disabled]="quotationLoading() || !quotationMonto" class="btn-primary w-full text-sm">
                      @if (quotationLoading()) { Enviando... } @else { Enviar cotizacion }
                    </button>
                  </div>
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

            <!-- Asignación automática (taller + técnico) -->
            @if (incident()!.taller_asignado || incident()!.tecnico_asignado) {
              <div class="surface p-4 space-y-3">
                <h3 class="text-xs font-semibold uppercase tracking-widest" style="color: var(--text-muted);">Asignación</h3>
                @if (incident()!.taller_asignado) {
                  <div class="flex items-center justify-between">
                    <span class="text-xs" style="color: var(--text-muted);">Taller</span>
                    <span class="text-xs font-semibold" style="color: var(--text-secondary);">{{ incident()!.taller_asignado }}</span>
                  </div>
                }
                @if (incident()!.tecnico_asignado) {
                  <div class="flex items-center justify-between">
                    <span class="text-xs" style="color: var(--text-muted);">Técnico</span>
                    <span class="text-xs font-semibold" style="color: var(--text-primary);">{{ incident()!.tecnico_asignado }}</span>
                  </div>
                }
                @if (incident()!.tecnico_telefono) {
                  <div class="flex items-center justify-between">
                    <span class="text-xs" style="color: var(--text-muted);">Teléfono</span>
                    <span class="text-xs font-mono" style="color: var(--text-secondary);">{{ incident()!.tecnico_telefono }}</span>
                  </div>
                }
                @if (incident()!.monto_estimado != null) {
                  <div class="flex items-center justify-between pt-2" style="border-top: 1px solid var(--border);">
                    <span class="text-xs" style="color: var(--text-muted);">Total estimado (IA)</span>
                    <span class="text-sm font-bold" style="color: var(--success);">Bs. {{ incident()!.monto_estimado | number:'1.2-2' }}</span>
                  </div>
                }
              </div>
            }
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
  auth = inject(AuthService);

  loading = signal(true);
  incident = signal<Incident | null>(null);
  tecnicos = signal<Tecnico[]>([]);
  currentAssignment = signal<Asignacion | null>(null);
  currentQuotation = signal<CotizacionDetalle | null>(null);
  actionLoading = signal(false);
  actionError = signal<string | null>(null);
  actionSuccess = signal<string | null>(null);
  quotationLoading = signal(false);
  quotationError = signal<string | null>(null);
  quotationSuccess = signal<string | null>(null);
  showReject = signal(false);
  technicianLocation = signal<TechnicianLocation | null>(null);
  selectedTecnico = '';
  rejectReason = '';
  quotationMonto: number | null = null;
  quotationTiempo: number | null = null;
  quotationNotas = '';

  private wsSub?: Subscription;
  private map: any = null;
  private incidentMarker: any = null;
  private technicianMarker: any = null;
  private staticMap: any = null;

  get incidentId(): string {
    return this.route.snapshot.paramMap.get('id') || '';
  }

  ngOnInit(): void {
    this.loadData();
    this.ws.connect(this.incidentId);
    this.wsSub = this.ws.messages$.subscribe(msg => this.handleWsMessage(msg));
    this.techniciansService.getAll().subscribe(t => this.tecnicos.set(t));
    this.loadAssignment();
  }

  ngOnDestroy(): void {
    this.wsSub?.unsubscribe();
    this.ws.disconnect();
    this.destroyMap();
    this.destroyStaticMap();
  }

  loadData(): void {
    this.loading.set(true);
    this.incidentsService.getById(this.incidentId).subscribe({
      next: (inc) => {
        this.incident.set(inc);
        this.loading.set(false);
        this.syncTrackingMap();
        this.syncStaticMap();
      },
      error: () => {
        this.incident.set(null);
        this.loading.set(false);
        this.destroyMap();
        this.destroyStaticMap();
      },
    });
  }

  private loadAssignment(): void {
    this.incidentsService.getAssignedToTaller().subscribe({
      next: (assignments) => {
        const assignment = assignments.find(a => a.id_incidente === this.incidentId) || null;
        this.currentAssignment.set(assignment);
        if (assignment) this.syncQuotationForm(assignment);
        this.loadQuotation();
      },
      error: () => {
        this.currentAssignment.set(null);
        this.loadQuotation();
      },
    });
  }

  private loadQuotation(): void {
    this.incidentsService.getQuotation(this.incidentId).subscribe({
      next: (quotation) => {
        this.currentQuotation.set(quotation);
        this.syncQuotationForm(quotation);
      },
      error: () => this.currentQuotation.set(null),
    });
  }

  private syncQuotationForm(quotation: Asignacion | CotizacionDetalle): void {
    if (quotation.monto_cotizado != null) this.quotationMonto = Number(quotation.monto_cotizado);
    const time = 'tiempo_estimado_reparacion' in quotation
      ? quotation.tiempo_estimado_reparacion
      : quotation.tiempo_estimado_minutos;
    if (time != null) this.quotationTiempo = time;
    if (quotation.notas_cotizacion) this.quotationNotas = quotation.notas_cotizacion;
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

  private syncStaticMap(): void {
    const inc = this.incident();
    // Static map only when there are coords but no live technician tracking.
    if (this.shouldShowTrackingSection() || inc?.latitud == null || inc?.longitud == null) {
      this.destroyStaticMap();
      return;
    }
    // 200ms delay so the container has real dimensions before Leaflet measures it.
    setTimeout(() => this.renderStaticMap(), 200);
  }

  private renderStaticMap(): void {
    const inc = this.incident();
    const container = document.getElementById('static-location-map');
    if (inc?.latitud == null || inc?.longitud == null || !container || typeof L === 'undefined') return;

    const latLng: [number, number] = [inc.latitud, inc.longitud];
    if (!this.staticMap) {
      this.staticMap = L.map(container, { zoomControl: true }).setView(latLng, 14);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(this.staticMap);
      L.marker(latLng, { icon: this.incidentIcon() }).addTo(this.staticMap).bindPopup('Incidente');
    } else {
      this.staticMap.setView(latLng, 14);
    }
    // Recalculate size once the tiles/layout settle — fixes the blank/gray map.
    this.staticMap.invalidateSize();
  }

  private destroyStaticMap(): void {
    if (this.staticMap) {
      this.staticMap.remove();
      this.staticMap = null;
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

  showQuotationCard(): boolean {
    return !!this.currentAssignment() || !!this.currentQuotation() || this.auth.isTaller();
  }

  hasQuotation(): boolean {
    return this.currentQuotation()?.monto_cotizado != null || this.currentAssignment()?.monto_cotizado != null;
  }

  quotationAmount(): number {
    return Number(this.currentQuotation()?.monto_cotizado ?? this.currentAssignment()?.monto_cotizado ?? 0);
  }

  quotationTime(): number | null {
    return this.currentQuotation()?.tiempo_estimado_reparacion
      ?? this.currentAssignment()?.tiempo_estimado_reparacion
      ?? this.currentAssignment()?.tiempo_estimado_minutos
      ?? null;
  }

  quotationNotes(): string | null {
    return this.currentQuotation()?.notas_cotizacion ?? this.currentAssignment()?.notas_cotizacion ?? null;
  }

  canViewQuotationStatus(): boolean {
    return this.auth.isAdmin() || this.auth.isTaller();
  }

  quotationStatusLabel(): string {
    const quotation = this.currentQuotation();
    const assignment = this.currentAssignment();
    if (!this.hasQuotation()) return 'Sin enviar';
    if (assignment?.estado_cotizacion) return assignment.estado_cotizacion.split('_').join(' ');
    if (quotation?.cotizacion_aceptada === true || assignment?.cotizacion_aceptada === true || assignment?.fecha_aceptacion_cotizacion) return 'Aceptada';
    if (quotation?.cotizacion_aceptada === false || assignment?.cotizacion_aceptada === false || assignment?.fecha_rechazo_cotizacion) return 'Rechazada';
    return 'Pendiente';
  }

  quotationStatusBadge(): string {
    const status = this.quotationStatusLabel().toUpperCase();
    if (status.includes('ACEPT')) return 'badge-green badge text-xs';
    if (status.includes('RECH')) return 'badge-red badge text-xs';
    if (status.includes('PEND')) return 'badge-amber badge text-xs';
    return 'badge-gray badge text-xs';
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

  submitQuotation(): void {
    if (!this.quotationMonto) return;
    this.quotationLoading.set(true);
    this.quotationError.set(null);
    this.quotationSuccess.set(null);
    this.incidentsService.proposeQuotation(this.incidentId, {
      monto_cotizado: Number(this.quotationMonto),
      tiempo_estimado_reparacion: this.quotationTiempo ? Number(this.quotationTiempo) : null,
      notas_cotizacion: this.quotationNotas?.trim() || null,
    }).subscribe({
      next: (quotation) => {
        this.currentQuotation.set(quotation);
        this.syncQuotationForm(quotation);
        this.quotationLoading.set(false);
        this.quotationSuccess.set('Cotizacion enviada correctamente');
        setTimeout(() => this.quotationSuccess.set(null), 3000);
      },
      error: (err) => {
        this.quotationError.set(err.error?.detail || 'Error al enviar cotizacion');
        this.quotationLoading.set(false);
      },
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



