import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TenantsService } from '../../core/services/tenants.service';
import { Tenant } from '../../models/tenant.model';
import { DashboardsIaService, DashboardIa } from './dashboards-ia.service';

declare const Chart: any;

const PALETA = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#14b8a6', '#a855f7', '#3b82f6', '#ec4899'];

@Component({
  selector: 'app-dashboards-ia',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-5 fade-in">
      <div>
        <h1 class="page-title">Dashboards IA</h1>
        <p class="page-subtitle">Pedí un informe en texto o audio y la IA arma los gráficos con datos reales</p>
      </div>

      <!-- Panel de pedido -->
      <div class="surface p-5 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label class="block text-xs mb-1" style="color: var(--text-muted);">Tenant a analizar</label>
            <select [(ngModel)]="selectedTenant" class="input text-sm">
              <option value="">Todos los tenants</option>
              @for (t of tenants(); track t.id_tenant) {
                <option [value]="t.id_tenant">{{ t.nombre }}</option>
              }
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="block text-xs mb-1" style="color: var(--text-muted);">Pedido en texto</label>
            <input [(ngModel)]="texto" class="input text-sm"
                   placeholder="Ej: desempeño por taller de este mes, qué técnico atendió más y el problema más recurrente" />
          </div>
        </div>

        <div class="flex items-center gap-3 flex-wrap">
          <button (click)="toggleGrabacion()" class="btn-ghost text-sm flex items-center gap-2"
                  [style.color]="grabando() ? 'var(--danger)' : 'var(--text-secondary)'">
            <span class="w-2 h-2 rounded-full" [style.background]="grabando() ? 'var(--danger)' : 'var(--text-muted)'"
                  [class.animate-pulse]="grabando()"></span>
            {{ grabando() ? 'Detener grabación' : 'Hablar (grabar audio)' }}
          </button>
          @if (audioListo()) {
            <span class="text-xs" style="color: var(--success);">Audio listo ✓</span>
            <button (click)="limpiarAudio()" class="text-xs" style="color: var(--text-muted);">Quitar</button>
          }
          <div class="flex-1"></div>
          <button (click)="generar()" [disabled]="loading()" class="btn-primary text-sm">
            {{ loading() ? 'Generando...' : 'Generar dashboard' }}
          </button>
        </div>

        @if (error()) {
          <div class="text-xs rounded-lg px-3 py-2"
               style="background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.2);">
            {{ error() }}
          </div>
        }
      </div>

      <!-- Resultado -->
      @if (dashboard(); as dash) {
        <div class="surface p-5">
          <div class="flex items-start justify-between mb-1">
            <div>
              <h2 class="text-lg font-bold" style="color: var(--text-primary);">{{ dash.titulo }}</h2>
              <p class="text-sm mt-1" style="color: var(--text-secondary);">
                <span style="color: var(--text-muted);">Orden:</span> {{ dash.orden }}
              </p>
              <p class="text-xs mt-1" style="color: var(--text-muted);">
                Generado por {{ dash.origen === 'gemini' ? 'IA (Gemini)' : 'reglas' }} · {{ dash.paneles.length }} paneles
              </p>
            </div>
            <button (click)="exportarPdf()" class="btn-ghost text-xs">Exportar PDF</button>
          </div>
        </div>

        @if (dash.paneles.length === 0) {
          <div class="surface p-12 text-center">
            <p class="text-sm" style="color: var(--text-muted);">La IA no encontró métricas para este pedido. Probá reformularlo.</p>
          </div>
        } @else {
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
            @for (panel of dash.paneles; track $index) {
              <div class="surface p-4">
                <h3 class="text-sm font-semibold mb-3" style="color: var(--text-primary);">{{ panel.titulo }}</h3>
                <div style="position: relative; height: 280px;">
                  <canvas [id]="'chart-' + $index"></canvas>
                </div>
              </div>
            }
          </div>
        }
      }
    </div>
  `,
})
export class DashboardsIaComponent implements OnInit, OnDestroy {
  private tenantsService = inject(TenantsService);
  private dashboardsService = inject(DashboardsIaService);

  tenants = signal<Tenant[]>([]);
  selectedTenant = '';
  texto = '';
  grabando = signal(false);
  audioListo = signal(false);
  loading = signal(false);
  error = signal<string | null>(null);
  dashboard = signal<DashboardIa | null>(null);

  private mediaRecorder: MediaRecorder | null = null;
  private chunks: BlobPart[] = [];
  private audioBlob: Blob | null = null;
  private charts: any[] = [];

  ngOnInit(): void {
    this.tenantsService.listar(true).subscribe({
      next: (list) => this.tenants.set(list),
      error: () => {},
    });
  }

  ngOnDestroy(): void {
    this.destruirCharts();
  }

  async toggleGrabacion(): Promise<void> {
    if (this.grabando()) {
      this.mediaRecorder?.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.chunks = [];
      this.mediaRecorder = new MediaRecorder(stream);
      this.mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) this.chunks.push(e.data); };
      this.mediaRecorder.onstop = () => {
        this.audioBlob = new Blob(this.chunks, { type: 'audio/webm' });
        this.audioListo.set(true);
        this.grabando.set(false);
        stream.getTracks().forEach((t) => t.stop());
      };
      this.mediaRecorder.start();
      this.grabando.set(true);
      this.audioListo.set(false);
    } catch {
      this.error.set('No se pudo acceder al micrófono. Revisá los permisos del navegador.');
    }
  }

  limpiarAudio(): void {
    this.audioBlob = null;
    this.audioListo.set(false);
  }

  generar(): void {
    if (!this.texto.trim() && !this.audioBlob) {
      this.error.set('Escribí un pedido o grabá un audio.');
      return;
    }
    this.loading.set(true);
    this.error.set(null);

    const form = new FormData();
    if (this.selectedTenant) form.append('id_tenant', this.selectedTenant);
    if (this.texto.trim()) form.append('texto', this.texto.trim());
    if (this.audioBlob) form.append('audio', this.audioBlob, 'pedido.webm');

    this.dashboardsService.generar(form).subscribe({
      next: (dash) => {
        this.dashboard.set(dash);
        this.loading.set(false);
        setTimeout(() => this.renderCharts(dash), 80);
      },
      error: (e) => {
        this.error.set(e?.error?.detail || 'No se pudo generar el dashboard.');
        this.loading.set(false);
      },
    });
  }

  private destruirCharts(): void {
    this.charts.forEach((c) => { try { c.destroy(); } catch { /* */ } });
    this.charts = [];
  }

  private renderCharts(dash: DashboardIa): void {
    if (typeof Chart === 'undefined') return;
    this.destruirCharts();
    dash.paneles.forEach((panel, i) => {
      const el = document.getElementById('chart-' + i) as HTMLCanvasElement | null;
      if (!el) return;
      const esTorta = panel.tipo === 'pie' || panel.tipo === 'doughnut';
      const data = esTorta
        ? {
            labels: panel.labels,
            datasets: [{ data: panel.series[0]?.data ?? [], backgroundColor: PALETA }],
          }
        : {
            labels: panel.labels,
            datasets: panel.series.map((s, idx) => ({
              label: s.label,
              data: s.data,
              backgroundColor: panel.tipo === 'line' ? 'transparent' : PALETA[idx % PALETA.length],
              borderColor: PALETA[idx % PALETA.length],
              borderWidth: 2,
              tension: 0.3,
            })),
          };
      const chart = new Chart(el, {
        type: panel.tipo,
        data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: esTorta || panel.series.length > 1 } },
        },
      });
      this.charts.push(chart);
    });
  }

  async exportarPdf(): Promise<void> {
    const dash = this.dashboard();
    if (!dash) return;
    const { jsPDF } = await import('jspdf'); // lazy: solo al exportar
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const ancho = doc.internal.pageSize.getWidth();

    doc.setFontSize(16);
    doc.text(dash.titulo, 14, 18);
    doc.setFontSize(10);
    doc.setTextColor(90);
    const orden = doc.splitTextToSize('Orden: ' + (dash.orden || '—'), ancho - 28);
    doc.text(orden, 14, 26);

    let y = 26 + orden.length * 5 + 6;
    dash.paneles.forEach((panel, i) => {
      const el = document.getElementById('chart-' + i) as HTMLCanvasElement | null;
      if (!el) return;
      const img = el.toDataURL('image/png', 1.0);
      const imgH = 75;
      if (y + imgH + 12 > doc.internal.pageSize.getHeight()) {
        doc.addPage();
        y = 18;
      }
      doc.setFontSize(12);
      doc.setTextColor(20);
      doc.text(panel.titulo, 14, y);
      y += 5;
      doc.addImage(img, 'PNG', 14, y, ancho - 28, imgH);
      y += imgH + 12;
    });

    const stamp = new Date().toISOString().slice(0, 16).replace(/[:T]/g, '');
    doc.save(`informe_ia_${stamp}.pdf`);
  }
}
