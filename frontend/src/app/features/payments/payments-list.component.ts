import { Component, inject, signal, computed, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { PaymentsService } from './payments.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { AuthService } from '../../core/services/auth.service';
import { Payment, PaymentStats } from './payment.model';
import { PaymentConfirmDialogComponent } from './payment-confirm-dialog.component';

@Component({
  selector: 'app-payments-list',
  standalone: true,
  imports: [CommonModule, FormsModule, PaymentConfirmDialogComponent],
  template: `
    <div class="space-y-5 fade-in">

      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">Pagos y Transacciones</h1>
          <p class="page-subtitle">Gestión de cobros por servicios prestados</p>
        </div>
        <button (click)="recargar()" class="btn-ghost text-xs">Actualizar</button>
      </div>

      <!-- Stats cards -->
      @if (stats()) {
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="stat-card">
            <div class="stat-icon">Bs</div>
            <div>
              <p class="stat-label">Total cobrado</p>
              <p class="stat-value" style="color:var(--success);">Bs. {{ stats()!.total_cobrado | number:'1.2-2' }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">P</div>
            <div>
              <p class="stat-label">Pendientes</p>
              <p class="stat-value" style="color:var(--warning);">{{ stats()!.count_por_estado['PENDIENTE'] ?? 0 }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">!</div>
            <div>
              <p class="stat-label">Sin pagar</p>
              <p class="stat-value" style="color:var(--danger);">{{ stats()!.count_por_estado['NO_PAGO'] ?? 0 }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">#</div>
            <div>
              <p class="stat-label">Total registros</p>
              <p class="stat-value">{{ totalRegistros() }}</p>
            </div>
          </div>
        </div>
      }

      <!-- Filtros -->
      <div class="surface p-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--text-muted);">Estado pago</label>
            <select [(ngModel)]="filtroEstado" (ngModelChange)="aplicarFiltros()" class="input text-sm">
              <option value="">Todos</option>
              <option value="NO_PAGO">Sin pagar</option>
              <option value="PENDIENTE">Pendiente revisión</option>
              <option value="PAGADO">Pagado</option>
              <option value="RECHAZADO">Rechazado</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--text-muted);">Desde</label>
            <input type="date" [(ngModel)]="filtroDesde" (ngModelChange)="aplicarFiltros()" class="input text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--text-muted);">Hasta</label>
            <input type="date" [(ngModel)]="filtroHasta" (ngModelChange)="aplicarFiltros()" class="input text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--text-muted);">Buscar incidente</label>
            <input type="text" [(ngModel)]="busqueda" placeholder="ID incidente..." class="input text-sm" />
          </div>
        </div>
      </div>

      <!-- Tabla / lista -->
      @if (cargando()) {
        <div class="space-y-2">
          @for (_ of [1,2,3,4]; track $index) {
            <div class="h-16 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (errorMsg()) {
        <div class="surface p-10 text-center">
          <p class="text-sm font-medium" style="color: var(--danger);">{{ errorMsg() }}</p>
          <button (click)="recargar()" class="btn-ghost text-sm mt-4">Reintentar</button>
        </div>
      } @else if (pagosFiltrados().length === 0) {
        <div class="surface p-16 text-center">
          <p class="text-sm font-medium" style="color: var(--text-secondary);">Sin pagos registrados</p>
          <p class="text-xs mt-1" style="color: var(--text-muted);">Los pagos aparecen automáticamente cuando un incidente es marcado como atendido</p>
        </div>
      } @else {
        <div class="surface overflow-hidden">
          <!-- Cabecera tabla -->
          <div class="hidden lg:grid grid-cols-12 gap-4 px-4 py-3 text-xs font-semibold uppercase tracking-wide"
               style="color: var(--text-muted); border-bottom: 1px solid var(--border); background: var(--bg-elevated);">
            <div class="col-span-3">Incidente</div>
            <div class="col-span-2">Estado Atención</div>
            <div class="col-span-2">Estado Pago</div>
            <div class="col-span-2">Monto</div>
            <div class="col-span-2">Fecha</div>
            <div class="col-span-1 text-center">Acción</div>
          </div>

          <!-- Filas -->
          @for (p of pagosFiltrados(); track p.id_pago) {
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 lg:gap-4 px-4 py-3.5 items-center transition-colors"
                 style="border-bottom: 1px solid var(--border);"
                 onmouseenter="this.style.background='var(--bg-elevated)'"
                 onmouseleave="this.style.background='transparent'">

              <!-- Incidente -->
              <div class="lg:col-span-3 flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm flex-shrink-0"
                     style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.15);">
                   Bs
                </div>
                <div>
                  <p class="text-xs font-mono font-semibold" style="color: var(--text-primary);">
                    #{{ p.id_incidente }}
                  </p>
                  <p class="text-xs" style="color: var(--text-muted);">{{ formatDate(p.fecha_creacion) }}</p>
                </div>
              </div>

              <!-- Estado atención (no disponible en listado, placeholder) -->
              <div class="lg:col-span-2">
                <span class="badge badge-gray text-xs">Servicio</span>
              </div>

              <!-- Estado pago -->
              <div class="lg:col-span-2">
                <span [class]="'badge text-xs ' + estadoBadge(p.estado)">{{ estadoLabel(p.estado) }}</span>
              </div>

              <!-- Monto -->
              <div class="lg:col-span-2">
                <p class="text-sm font-semibold" style="color: var(--text-primary);">Bs. {{ p.monto | number:'1.2-2' }}</p>
              </div>

              <!-- Fecha marcado -->
              <div class="lg:col-span-2">
                <p class="text-xs" style="color: var(--text-muted);">
                  @if (p.fecha_marcado_pago) {
                    {{ formatDate(p.fecha_marcado_pago) }}
                  } @else {
                    —
                  }
                </p>
              </div>

              <!-- Acción -->
              <div class="lg:col-span-1 flex justify-start lg:justify-center">
                @if (p.estado === 'PENDIENTE') {
                  <button (click)="abrirDialog(p)"
                          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                          style="background: rgba(245,158,11,0.15); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3);">
                    Revisar
                  </button>
                } @else if (p.estado === 'PAGADO' || p.estado === 'RECHAZADO') {
                  <button (click)="abrirDialog(p)"
                          class="btn-ghost text-xs py-1.5 px-3">
                    Ver
                  </button>
                } @else {
                  <span class="text-xs" style="color: var(--text-muted);">—</span>
                }
              </div>
            </div>
          }
        </div>
      }
    </div>

    <!-- Dialog -->
    @if (pagoSeleccionado()) {
      <app-payment-confirm-dialog
        [payment]="pagoSeleccionado()!"
        (closed)="cerrarDialog()"
        (actionCompleted)="recargar()" />
    }
  `,
})
export class PaymentsListComponent implements OnInit, OnDestroy {
  private paymentsService = inject(PaymentsService);
  private ws = inject(WebSocketService);
  private auth = inject(AuthService);
  private wsSub?: Subscription;

  cargando = signal(true);
  errorMsg = signal<string | null>(null);
  pagos = signal<Payment[]>([]);
  stats = signal<PaymentStats | null>(null);
  pagoSeleccionado = signal<Payment | null>(null);

  filtroEstado = '';
  filtroDesde = '';
  filtroHasta = '';
  busqueda = '';

  pagosFiltrados = computed(() => {
    const texto = this.busqueda.trim().toLowerCase();
    return this.pagos().filter(p =>
      !texto || String(p.id_incidente).includes(texto)
    );
  });

  totalRegistros = computed(() => {
    const s = this.stats();
    if (!s) return 0;
    return Object.values(s.count_por_estado).reduce((a, b) => a + b, 0);
  });

  ngOnInit(): void {
    this.recargar();
    this.ws.connectGlobal();
    this.wsSub = this.ws.messages$.subscribe(msg => {
      const tipo = msg.tipo || msg.type || '';
      if (['pago_pendiente', 'pago_confirmado', 'pago_rechazado'].includes(tipo)) {
        this.recargar();
      }
    });
  }

  ngOnDestroy(): void {
    this.wsSub?.unsubscribe();
  }

  recargar(): void {
    this.cargando.set(true);
    this.errorMsg.set(null);
    const filtros: any = {};
    if (this.filtroEstado) filtros.estado = this.filtroEstado;
    if (this.filtroDesde) filtros.fecha_desde = this.filtroDesde;
    if (this.filtroHasta) filtros.fecha_hasta = this.filtroHasta;

    this.paymentsService.listar(filtros).subscribe({
      next: (lista) => { this.pagos.set(lista); this.cargando.set(false); },
      error: (err) => {
        this.errorMsg.set(err.error?.detail || 'Error al cargar los pagos');
        this.cargando.set(false);
      },
    });

    this.paymentsService.obtenerStats().subscribe({
      next: (s) => this.stats.set(s),
      error: () => {},
    });
  }

  aplicarFiltros(): void {
    this.recargar();
  }

  abrirDialog(p: Payment): void {
    this.pagoSeleccionado.set(p);
  }

  cerrarDialog(): void {
    this.pagoSeleccionado.set(null);
  }

  estadoLabel(e: string): string {
    return { NO_PAGO: 'Sin pagar', PENDIENTE: 'Pendiente', PAGADO: 'Pagado', RECHAZADO: 'Rechazado' }[e] || e;
  }

  estadoBadge(e: string): string {
    return { NO_PAGO: 'badge-red', PENDIENTE: 'badge-amber', PAGADO: 'badge-green', RECHAZADO: 'badge-gray' }[e] || 'badge-gray';
  }

  formatDate(d?: string): string {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('es-BO', {
      day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
    });
  }
}
