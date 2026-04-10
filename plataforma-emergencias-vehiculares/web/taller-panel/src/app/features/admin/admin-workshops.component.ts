import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService } from '../../core/services/admin.service';
import { Taller, TallerCreate } from '../../models';

@Component({
  selector: 'app-admin-workshops',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-5 fade-in">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">Gestión de talleres</h1>
          <p class="page-subtitle">{{ talleres().length }} talleres registrados</p>
        </div>
        <div class="flex gap-2">
          <button (click)="reload()" class="btn-ghost text-xs">🔄</button>
          <button (click)="openCreate()" class="btn-primary text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Nuevo taller
          </button>
        </div>
      </div>

      <!-- Filter & search -->
      <div class="surface p-3 flex items-center gap-3">
        <div class="relative flex-1">
          <input [(ngModel)]="search" class="input pl-8 py-2 text-sm" placeholder="Buscar talleres..." />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style="color: var(--text-muted);">🔍</span>
        </div>
        <div class="flex gap-1.5">
          @for (f of statusFilters; track f.value) {
            <button (click)="filterActivo.set(f.value)"
                    [class]="'filter-tab ' + (filterActivo() === f.value ? 'active' : '')">
              {{ f.label }}
            </button>
          }
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(16,185,129,0.12);">🏪</div>
          <div>
            <p class="stat-label">Activos</p>
            <p class="stat-value text-green-400">{{ activos() }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(239,68,68,0.12);">🚫</div>
          <div>
            <p class="stat-label">Inactivos</p>
            <p class="stat-value text-red-400">{{ inactivos() }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(59,130,246,0.12);">📊</div>
          <div>
            <p class="stat-label">Comisión promedio</p>
            <p class="stat-value">{{ avgComision() }}<span class="text-sm">%</span></p>
          </div>
        </div>
      </div>

      <!-- Grid de talleres -->
      @if (loading()) {
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          @for (_ of [1,2,3,4,5,6]; track $index) {
            <div class="h-40 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (filtered().length === 0) {
        <div class="surface p-16 text-center">
          <span class="text-5xl block mb-3">🏪</span>
          <p class="text-sm" style="color: var(--text-muted);">Sin talleres registrados</p>
          <button (click)="openCreate()" class="btn-primary mt-4 text-sm">Crear primer taller</button>
        </div>
      } @else {
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          @for (t of filtered(); track t.id_taller) {
            <div class="surface p-5 flex flex-col gap-4 hover:border-blue-500/30 transition-all"
                 style="border-color: var(--border);">
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                       style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2);">🏪</div>
                  <div>
                    <p class="font-semibold text-sm" style="color: var(--text-primary);">{{ t.nombre_negocio }}</p>
                    @if (t.nit) {
                      <p class="text-xs" style="color: var(--text-muted);">NIT: {{ t.nit }}</p>
                    }
                  </div>
                </div>
                <span [class]="t.activo ? 'badge-green badge' : 'badge-red badge'" style="font-size:10px; flex-shrink: 0;">
                  {{ t.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </div>

              <div class="space-y-1.5">
                @if (t.direccion) {
                  <div class="flex items-center gap-2 text-xs" style="color: var(--text-muted);">
                    <span>📍</span> {{ t.direccion }}
                  </div>
                }
                <div class="flex items-center gap-2 text-xs" style="color: var(--text-muted);">
                  <span>💰</span> Comisión: <span class="font-semibold" style="color: var(--text-secondary);">{{ t.tasa_comision }}%</span>
                </div>
                <div class="flex items-center gap-2 text-xs" style="color: var(--text-muted);">
                  <span>📅</span> Desde {{ formatDate(t.fecha_creacion) }}
                </div>
              </div>

              <div class="flex gap-2 pt-1" style="border-top: 1px solid var(--border);">
                <button (click)="openEdit(t)" class="btn-ghost text-xs flex-1">✏️ Editar</button>
                <button (click)="toggleActive(t)"
                        [class]="t.activo ? 'btn-danger text-xs flex-1' : 'btn-success text-xs flex-1'">
                  {{ t.activo ? 'Desactivar' : 'Activar' }}
                </button>
              </div>
            </div>
          }
        </div>
      }
    </div>

    <!-- Modal -->
    @if (showModal()) {
      <div class="modal-overlay" (click)="closeModal()">
        <div class="modal fade-in" (click)="$event.stopPropagation()">
          <h2 class="text-base font-semibold mb-5" style="color: var(--text-primary);">
            {{ editingId() ? 'Editar taller' : 'Crear nuevo taller' }}
          </h2>

          @if (formError()) {
            <div class="rounded-lg px-4 py-3 mb-4 text-sm"
                 style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); color: #fca5a5;">
              {{ formError() }}
            </div>
          }

          <div class="space-y-4">
            <div>
              <label class="block text-xs font-medium mb-1.5" style="color: var(--text-secondary);">Nombre del negocio *</label>
              <input type="text" [(ngModel)]="form.nombre_negocio" class="input" placeholder="Taller Central S.A." />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--text-secondary);">NIT</label>
                <input type="text" [(ngModel)]="form.nit" class="input" placeholder="1234567890" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--text-secondary);">Comisión (%)</label>
                <input type="number" [(ngModel)]="form.tasa_comision" class="input" min="0" max="100" step="0.5" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium mb-1.5" style="color: var(--text-secondary);">Dirección</label>
              <input type="text" [(ngModel)]="form.direccion" class="input" placeholder="Av. Principal 123, La Paz" />
            </div>
            @if (editingId()) {
              <div class="flex items-center gap-3 p-3 rounded-lg" style="background: var(--bg-base);">
                <input type="checkbox" [(ngModel)]="formActivo" id="activo" class="w-4 h-4" />
                <label for="activo" class="text-sm" style="color: var(--text-secondary);">Taller activo</label>
              </div>
            }
          </div>

          <div class="flex gap-2 mt-5">
            <button (click)="save()" [disabled]="formLoading() || !form.nombre_negocio" class="btn-primary flex-1">
              {{ formLoading() ? 'Guardando...' : (editingId() ? 'Actualizar' : 'Crear taller') }}
            </button>
            <button (click)="closeModal()" class="btn-ghost">Cancelar</button>
          </div>
        </div>
      </div>
    }
  `,
})
export class AdminWorkshopsComponent implements OnInit {
  private adminService = inject(AdminService);

  loading = signal(true);
  talleres = signal<Taller[]>([]);
  showModal = signal(false);
  editingId = signal<string | null>(null);
  formLoading = signal(false);
  formError = signal<string | null>(null);
  filterActivo = signal('');
  search = '';
  formActivo = true;

  form: TallerCreate = { nombre_negocio: '', nit: '', direccion: '', tasa_comision: 10 };

  statusFilters = [
    { label: 'Todos', value: '' },
    { label: 'Activos', value: 'true' },
    { label: 'Inactivos', value: 'false' },
  ];

  activos = computed(() => this.talleres().filter(t => t.activo).length);
  inactivos = computed(() => this.talleres().filter(t => !t.activo).length);
  avgComision = computed(() => {
    const list = this.talleres();
    if (!list.length) return 0;
    const avg = list.reduce((a, b) => a + Number(b.tasa_comision), 0) / list.length;
    return avg.toFixed(1);
  });

  filtered = computed(() => {
    let list = this.talleres();
    const s = this.search.toLowerCase();
    if (s) list = list.filter(t => t.nombre_negocio.toLowerCase().includes(s) || (t.nit || '').includes(s));
    if (this.filterActivo()) list = list.filter(t => String(t.activo) === this.filterActivo());
    return list;
  });

  ngOnInit(): void { this.reload(); }

  reload(): void {
    this.loading.set(true);
    this.adminService.getWorkshops(false).subscribe({
      next: (list) => { this.talleres.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  openCreate(): void {
    this.editingId.set(null);
    this.form = { nombre_negocio: '', nit: '', direccion: '', tasa_comision: 10 };
    this.formActivo = true;
    this.formError.set(null);
    this.showModal.set(true);
  }

  openEdit(t: Taller): void {
    this.editingId.set(t.id_taller);
    this.form = { nombre_negocio: t.nombre_negocio, nit: t.nit || '', direccion: t.direccion || '', tasa_comision: Number(t.tasa_comision) };
    this.formActivo = t.activo;
    this.formError.set(null);
    this.showModal.set(true);
  }

  closeModal(): void { this.showModal.set(false); this.formError.set(null); }

  save(): void {
    if (!this.form.nombre_negocio) return;
    this.formLoading.set(true);
    this.formError.set(null);
    const payload = { ...this.form, activo: this.formActivo };
    const id = this.editingId();
    const obs = id
      ? this.adminService.updateWorkshop(id, payload)
      : this.adminService.createWorkshop(this.form);

    obs.subscribe({
      next: () => { this.formLoading.set(false); this.closeModal(); this.reload(); },
      error: (err) => { this.formError.set(err.error?.detail || 'Error al guardar'); this.formLoading.set(false); },
    });
  }

  toggleActive(t: Taller): void {
    this.adminService.toggleWorkshop(t.id_taller, !t.activo).subscribe({
      next: () => this.reload(),
    });
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', year: 'numeric' });
  }
}
