import { AfterViewInit, Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StatsService } from '../../core/services/stats.service';
import { DashboardStats } from '../../models';

declare const Chart: any;

@Component({
  selector: 'app-operations',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-y-5 fade-in">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h1 class="page-title">Operaciones</h1>
          <p class="page-subtitle">KPIs operacionales filtrados por tenant</p>
        </div>
        <button (click)="loadData()" class="btn-ghost text-xs">Actualizar</button>
      </div>

      @if (loading()) {
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          @for (_ of [1,2,3,4]; track $index) {
            <div class="h-32 shimmer rounded-xl"></div>
          }
        </div>
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-5">
          <div class="h-80 shimmer rounded-xl"></div>
          <div class="h-80 shimmer rounded-xl"></div>
        </div>
      } @else if (errorMsg()) {
        <div class="surface p-12 text-center">
          <p class="text-sm font-semibold" style="color: var(--danger);">{{ errorMsg() }}</p>
          <p class="text-xs mt-2" style="color: var(--text-muted);">Verifica que el backend exponga GET /stats/dashboard.</p>
          <button (click)="loadData()" class="btn-primary text-sm mt-4">Reintentar</button>
        </div>
      } @else if (stats()) {
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <div class="surface p-5 overflow-hidden relative">
            <div class="absolute -right-6 -top-6 w-20 h-20 rounded-full" style="background: var(--accent-glow);"></div>
            <p class="text-xs font-semibold uppercase tracking-widest mb-3" style="color: var(--text-muted);">Total incidentes</p>
            <p class="text-3xl font-bold" style="color: var(--text-primary);">{{ stats()!.total_incidentes | number }}</p>
            <p class="text-xs mt-2" style="color: var(--text-muted);">Actividad acumulada del tenant</p>
          </div>
          <div class="surface p-5 overflow-hidden relative">
            <div class="absolute -right-6 -top-6 w-20 h-20 rounded-full" style="background: rgba(16,185,129,0.12);"></div>
            <p class="text-xs font-semibold uppercase tracking-widest mb-3" style="color: var(--text-muted);">Atendidos</p>
            <p class="text-3xl font-bold" style="color: var(--success);">{{ attendedCount() | number }}</p>
            <p class="text-xs mt-2" style="color: var(--text-muted);">Servicios completados</p>
          </div>
          <div class="surface p-5 overflow-hidden relative">
            <div class="absolute -right-6 -top-6 w-20 h-20 rounded-full" style="background: rgba(245,158,11,0.12);"></div>
            <p class="text-xs font-semibold uppercase tracking-widest mb-3" style="color: var(--text-muted);">Recaudado</p>
            <p class="text-3xl font-bold" style="color: var(--warning);">Bs. {{ stats()!.total_recaudado | number:'1.2-2' }}</p>
            <p class="text-xs mt-2" style="color: var(--text-muted);">Ingresos confirmados</p>
          </div>
          <div class="surface p-5 overflow-hidden relative">
            <div class="absolute -right-6 -top-6 w-20 h-20 rounded-full" style="background: rgba(59,130,246,0.12);"></div>
            <p class="text-xs font-semibold uppercase tracking-widest mb-3" style="color: var(--text-muted);">Tiempo promedio</p>
            <p class="text-3xl font-bold" style="color: var(--accent);">{{ averageTimeLabel() }}</p>
            <p class="text-xs mt-2" style="color: var(--text-muted);">Atencion por incidente</p>
          </div>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-3 gap-5">
          <div class="surface p-5 xl:col-span-2">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Incidentes por clasificacion</h2>
                <p class="text-xs mt-1" style="color: var(--text-muted);">Distribucion del volumen operativo</p>
              </div>
            </div>
            <div class="h-72">
              <canvas id="classificationChart"></canvas>
            </div>
          </div>

          <div class="surface p-5" style="background: linear-gradient(135deg, var(--bg-surface), var(--bg-elevated)); border-left: 3px solid var(--success);">
            <p class="text-xs font-semibold uppercase tracking-widest mb-3" style="color: var(--text-muted);">Taller mas eficiente</p>
            @if (stats()!.taller_mas_eficiente) {
              <h2 class="text-xl font-bold leading-tight" style="color: var(--text-primary);">{{ stats()!.taller_mas_eficiente!.nombre_negocio }}</h2>
              <div class="grid grid-cols-2 gap-3 mt-5">
                <div class="rounded-xl p-3" style="background: var(--bg-base); border: 1px solid var(--border);">
                  <p class="text-xs" style="color: var(--text-muted);">Atendidos</p>
                  <p class="text-lg font-bold" style="color: var(--success);">{{ stats()!.taller_mas_eficiente!.incidentes_atendidos || 0 }}</p>
                </div>
                <div class="rounded-xl p-3" style="background: var(--bg-base); border: 1px solid var(--border);">
                  <p class="text-xs" style="color: var(--text-muted);">Promedio</p>
                  <p class="text-lg font-bold" style="color: var(--accent);">{{ workshopTimeLabel() }}</p>
                </div>
              </div>
            } @else {
              <div class="rounded-xl p-5 text-center" style="background: var(--bg-base); border: 1px dashed var(--border);">
                <p class="text-sm font-medium" style="color: var(--text-secondary);">Sin datos suficientes</p>
                <p class="text-xs mt-1" style="color: var(--text-muted);">Aparecera cuando existan atenciones completadas.</p>
              </div>
            }
          </div>
        </div>

        <div class="surface p-5">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-sm font-semibold" style="color: var(--text-primary);">Incidentes ultimos 7 dias</h2>
              <p class="text-xs mt-1" style="color: var(--text-muted);">Tendencia diaria de solicitudes</p>
            </div>
          </div>
          <div class="h-72">
            <canvas id="dailyChart"></canvas>
          </div>
        </div>
      }
    </div>
  `,
})
export class OperationsComponent implements OnInit, AfterViewInit, OnDestroy {
  private statsService = inject(StatsService);

  loading = signal(true);
  errorMsg = signal<string | null>(null);
  stats = signal<DashboardStats | null>(null);

  private viewReady = false;
  private classificationChart: any = null;
  private dailyChart: any = null;

  ngOnInit(): void {
    this.loadData();
  }

  ngAfterViewInit(): void {
    this.viewReady = true;
    this.renderCharts();
  }

  ngOnDestroy(): void {
    this.destroyCharts();
  }

  loadData(): void {
    this.loading.set(true);
    this.errorMsg.set(null);
    this.statsService.getDashboard().subscribe({
      next: (data) => {
        this.stats.set(this.normalizeStats(data));
        this.loading.set(false);
        setTimeout(() => this.renderCharts(), 0);
      },
      error: (err) => {
        this.errorMsg.set(err.error?.detail || 'No se pudieron cargar las metricas operacionales');
        this.loading.set(false);
        this.destroyCharts();
      },
    });
  }

  averageTimeLabel(): string {
    const minutes = this.stats()?.tiempo_promedio_atencion_minutos;
    return minutes == null ? '-' : `${Math.round(minutes)} min`;
  }

  workshopTimeLabel(): string {
    const minutes = this.stats()?.taller_mas_eficiente?.tiempo_promedio_atencion_minutos;
    return minutes == null ? '-' : `${Math.round(minutes)} min`;
  }

  private normalizeStats(data: DashboardStats): DashboardStats {
    return {
      total_incidentes: Number(data.total_incidentes || 0),
      incidentes_atendidos: Number(data.incidentes_atendidos ?? this.attendedFromStates(data.incidentes_por_estado || [])),
      incidentes_por_estado: data.incidentes_por_estado || [],
      total_recaudado: Number(data.total_recaudado || 0),
      tiempo_promedio_atencion_minutos: data.tiempo_promedio_atencion_minutos == null ? null : Number(data.tiempo_promedio_atencion_minutos),
      incidentes_por_clasificacion: this.classificationRecord(data.incidentes_por_clasificacion || {}),
      incidentes_ultimos_7_dias: data.incidentes_ultimos_7_dias || [],
      taller_top: data.taller_top || null,
      taller_mas_eficiente: data.taller_mas_eficiente || (data.taller_top ? {
        id_taller: data.taller_top.id_taller,
        nombre_negocio: data.taller_top.nombre_negocio,
        incidentes_atendidos: data.taller_top.total_atendidos,
        tiempo_promedio_atencion_minutos: data.tiempo_promedio_atencion_minutos,
      } : null),
    };
  }

  attendedCount(): number {
    return this.stats()?.incidentes_atendidos || 0;
  }

  private attendedFromStates(states: Array<{ estado: string; total: number }>): number {
    return states.find(item => item.estado === 'ATENDIDO')?.total || 0;
  }

  private classificationRecord(value: DashboardStats['incidentes_por_clasificacion']): Record<string, number> {
    if (Array.isArray(value)) {
      return value.reduce<Record<string, number>>((acc, item) => {
        acc[item.clasificacion] = item.total;
        return acc;
      }, {});
    }
    return value || {};
  }

  private renderCharts(): void {
    const data = this.stats();
    if (!this.viewReady || !data || typeof Chart === 'undefined') return;
    this.destroyCharts();

    const classificationCanvas = document.getElementById('classificationChart') as HTMLCanvasElement | null;
    const dailyCanvas = document.getElementById('dailyChart') as HTMLCanvasElement | null;

    if (classificationCanvas) {
      const classification = this.classificationRecord(data.incidentes_por_clasificacion);
      const labels = Object.keys(classification);
      const values = labels.map(label => classification[label]);
      this.classificationChart = new Chart(classificationCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Incidentes',
            data: values,
            backgroundColor: 'rgba(124, 58, 237, 0.72)',
            borderColor: 'rgba(124, 58, 237, 1)',
            borderWidth: 1,
            borderRadius: 10,
          }],
        },
        options: this.chartOptions(false),
      });
    }

    if (dailyCanvas) {
      this.dailyChart = new Chart(dailyCanvas, {
        type: 'line',
        data: {
          labels: data.incidentes_ultimos_7_dias.map(item => item.fecha || item.dia),
          datasets: [{
            label: 'Incidentes',
            data: data.incidentes_ultimos_7_dias.map(item => item.total),
            borderColor: 'rgba(16, 185, 129, 1)',
            backgroundColor: 'rgba(16, 185, 129, 0.14)',
            fill: true,
            tension: 0.38,
            pointRadius: 4,
            pointBackgroundColor: 'rgba(16, 185, 129, 1)',
          }],
        },
        options: this.chartOptions(true),
      });
    }
  }

  private chartOptions(suggestedMaxFromData: boolean): any {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.92)', padding: 12 },
      },
      scales: {
        x: {
          ticks: { color: 'rgba(148, 163, 184, 0.9)' },
          grid: { color: 'rgba(148, 163, 184, 0.08)' },
        },
        y: {
          beginAtZero: true,
          suggestedMax: suggestedMaxFromData ? undefined : 5,
          ticks: { color: 'rgba(148, 163, 184, 0.9)', precision: 0 },
          grid: { color: 'rgba(148, 163, 184, 0.1)' },
        },
      },
    };
  }

  private destroyCharts(): void {
    this.classificationChart?.destroy();
    this.dailyChart?.destroy();
    this.classificationChart = null;
    this.dailyChart = null;
  }
}
