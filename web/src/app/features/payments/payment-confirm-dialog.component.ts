import { Component, Input, Output, EventEmitter, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PaymentsService } from './payments.service';
import { Payment } from './payment.model';

@Component({
  selector: 'app-payment-confirm-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <!-- Backdrop -->
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4"
         style="background: rgba(0,0,0,0.6);"
         (click)="onBackdropClick($event)">
      <div class="w-full max-w-lg rounded-2xl shadow-2xl flex flex-col max-h-[90vh]"
           style="background: var(--bg-surface); border: 1px solid var(--border);"
           (click)="$event.stopPropagation()">

        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 flex-shrink-0"
             style="border-bottom: 1px solid var(--border);">
          <div class="flex items-center gap-3">
            <span class="text-xl">{{ estadoIcon(payment.estado) }}</span>
            <div>
              <h3 class="text-sm font-semibold" style="color: var(--text-primary);">Detalle del Pago</h3>
              <p class="text-xs font-mono" style="color: var(--text-muted);">#{{ payment.id_pago.substring(0,8).toUpperCase() }}</p>
            </div>
          </div>
          <button (click)="closed.emit()" class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
                  style="color: var(--text-muted); border: 1px solid var(--border);"
                  onmouseenter="this.style.background='var(--bg-elevated)'"
                  onmouseleave="this.style.background='transparent'">
            x
          </button>
        </div>

        <!-- Body -->
        <div class="overflow-y-auto flex-1 px-6 py-4 space-y-4">

          <!-- Estado badge -->
          <div class="flex items-center gap-2">
            <span [class]="'badge text-xs ' + estadoBadge(payment.estado)">{{ payment.estado }}</span>
          </div>

          <!-- Datos del pago -->
          <div class="rounded-xl p-4 space-y-3" style="background: var(--bg-elevated); border: 1px solid var(--border);">
            <div class="flex items-center justify-between text-sm">
              <span style="color: var(--text-muted);">Incidente</span>
              <span class="font-mono font-semibold" style="color: var(--text-primary);">#{{ payment.id_incidente.substring(0,8).toUpperCase() }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span style="color: var(--text-muted);">Monto total</span>
              <span class="font-bold text-base" style="color: var(--success);">Bs. {{ payment.monto | number:'1.2-2' }}</span>
            </div>
            @if (payment.comision_plataforma) {
              <div class="flex items-center justify-between text-sm">
                <span style="color: var(--text-muted);">Comisión plataforma (15%)</span>
                <span style="color: var(--text-secondary);">Bs. {{ payment.comision_plataforma | number:'1.2-2' }}</span>
              </div>
            }
            @if (payment.fecha_creacion) {
              <div class="flex items-center justify-between text-sm">
                <span style="color: var(--text-muted);">Creado</span>
                <span style="color: var(--text-secondary);">{{ formatDate(payment.fecha_creacion) }}</span>
              </div>
            }
            @if (payment.fecha_marcado_pago) {
              <div class="flex items-center justify-between text-sm">
                <span style="color: var(--text-muted);">Comprobante enviado</span>
                <span style="color: var(--text-secondary);">{{ formatDate(payment.fecha_marcado_pago) }}</span>
              </div>
            }
            @if (payment.fecha_confirmacion) {
              <div class="flex items-center justify-between text-sm">
                <span style="color: var(--text-muted);">Confirmado</span>
                <span style="color: var(--success);">{{ formatDate(payment.fecha_confirmacion) }}</span>
              </div>
            }
          </div>

          <!-- Notas del cliente -->
          @if (payment.notas_cliente) {
            <div class="rounded-xl p-4" style="background: rgba(59,130,246,0.05); border: 1px solid rgba(59,130,246,0.15);">
              <p class="text-xs font-semibold mb-1" style="color: var(--accent);">Notas del cliente</p>
              <p class="text-sm" style="color: var(--text-secondary);">{{ payment.notas_cliente }}</p>
            </div>
          }

          <!-- Comprobante -->
          <div>
            <p class="text-xs font-semibold uppercase tracking-widest mb-2" style="color: var(--text-muted);">Comprobante adjunto</p>
            @if (payment.comprobante_url) {
              <a [href]="fullUrl(payment.comprobante_url)" target="_blank" class="block group">
                <img [src]="fullUrl(payment.comprobante_url)"
                     alt="Comprobante de pago"
                     class="w-full rounded-xl object-cover max-h-64 transition-opacity group-hover:opacity-80"
                     style="border: 1px solid var(--border);"
                     (error)="onImgError($event)" />
                <p class="text-xs mt-1 text-center" style="color: var(--accent);">Click para ver en tamaño completo →</p>
              </a>
            } @else {
              <div class="rounded-xl p-6 text-center" style="background: var(--bg-elevated); border: 1px dashed var(--border);">
                <p class="text-xs" style="color: var(--text-muted);">Sin comprobante adjunto</p>
              </div>
            }
          </div>

          <!-- Motivo rechazo -->
          @if (payment.motivo_rechazo) {
            <div class="rounded-xl p-4" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);">
              <p class="text-xs font-semibold mb-1" style="color: var(--danger);">Motivo de rechazo</p>
              <p class="text-sm" style="color: #fca5a5;">{{ payment.motivo_rechazo }}</p>
            </div>
          }

          <!-- Input motivo rechazo -->
          @if (mostrarInputRechazo()) {
            <div class="rounded-xl p-4 space-y-2" style="background: var(--bg-elevated); border: 1px solid var(--border);">
              <p class="text-xs font-semibold" style="color: var(--text-secondary);">Motivo del rechazo</p>
              <textarea [(ngModel)]="motivoRechazo"
                        class="input resize-none text-sm w-full"
                        rows="3"
                        placeholder="Explica por qué se rechaza el comprobante...">
              </textarea>
            </div>
          }

          <!-- Mensajes de feedback -->
          @if (error()) {
            <div class="text-xs rounded-lg px-3 py-2"
                 style="background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.2);">
              {{ error() }}
            </div>
          }
          @if (exito()) {
            <div class="text-xs rounded-lg px-3 py-2"
                 style="background: rgba(16,185,129,0.1); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.2);">
              {{ exito() }}
            </div>
          }
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 flex gap-3 justify-end flex-shrink-0"
             style="border-top: 1px solid var(--border);">
          @if (payment.estado === 'PENDIENTE') {
            @if (!mostrarInputRechazo()) {
              <button (click)="mostrarInputRechazo.set(true)"
                      [disabled]="cargando()"
                      class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                      style="background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.2);">
                 Rechazar
              </button>
              <button (click)="confirmar()"
                      [disabled]="cargando()"
                      class="btn-success px-5 py-2 text-sm">
                 @if (cargando()) { Procesando... } @else { Confirmar pago }
              </button>
            } @else {
              <button (click)="mostrarInputRechazo.set(false)" class="btn-ghost text-sm">
                Cancelar
              </button>
              <button (click)="rechazar()"
                      [disabled]="!motivoRechazo.trim() || cargando()"
                      class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                      style="background: rgba(239,68,68,0.15); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3);">
                @if (cargando()) { Procesando... } @else { Confirmar rechazo }
              </button>
            }
          } @else {
            <button (click)="closed.emit()" class="btn-ghost text-sm px-5">
              Cerrar
            </button>
          }
        </div>
      </div>
    </div>
  `,
})
export class PaymentConfirmDialogComponent {
  private paymentsService = inject(PaymentsService);

  @Input({ required: true }) payment!: Payment;
  @Output() closed = new EventEmitter<void>();
  @Output() actionCompleted = new EventEmitter<void>();

  cargando = signal(false);
  error = signal<string | null>(null);
  exito = signal<string | null>(null);
  mostrarInputRechazo = signal(false);
  motivoRechazo = '';

  onBackdropClick(event: Event): void {
    if (event.target === event.currentTarget) this.closed.emit();
  }

  confirmar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.paymentsService.confirmar(this.payment.id_pago).subscribe({
      next: () => {
        this.exito.set('Pago confirmado correctamente');
        this.cargando.set(false);
        setTimeout(() => { this.actionCompleted.emit(); this.closed.emit(); }, 1000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al confirmar el pago');
        this.cargando.set(false);
      },
    });
  }

  rechazar(): void {
    if (!this.motivoRechazo.trim()) return;
    this.cargando.set(true);
    this.error.set(null);
    this.paymentsService.rechazar(this.payment.id_pago, this.motivoRechazo.trim()).subscribe({
      next: () => {
        this.exito.set('Comprobante rechazado. El cliente podrá subir uno nuevo.');
        this.cargando.set(false);
        setTimeout(() => { this.actionCompleted.emit(); this.closed.emit(); }, 1200);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al rechazar el pago');
        this.cargando.set(false);
      },
    });
  }

  onImgError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
  }

  fullUrl(url: string): string {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    const base = 'https://plataforma-inteligente-de-atenci-n-de-emergencia-production.up.railway.app';
    return `${base}${url}`;
  }

  estadoIcon(e: string): string {
    return { NO_PAGO: 'NP', PENDIENTE: 'PE', PAGADO: 'OK', RECHAZADO: 'RE' }[e] || 'PG';
  }

  estadoBadge(e: string): string {
    return { NO_PAGO: 'badge-red', PENDIENTE: 'badge-amber', PAGADO: 'badge-green', RECHAZADO: 'badge-gray' }[e] || 'badge-gray';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', {
      day: 'numeric', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }
}
