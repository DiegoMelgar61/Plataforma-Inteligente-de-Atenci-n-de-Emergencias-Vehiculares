import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';
import { TenantsService } from '../../core/services/tenants.service';
import { Tenant, TenantCreate, TenantUpdate } from '../../models/tenant.model';

@Component({
  selector: 'app-tenants',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    @if (!auth.isAdmin()) {
      <div class="surface p-10 text-center fade-in">
        <p class="text-sm font-semibold" style="color: var(--text-primary);">Acceso restringido</p>
        <p class="text-sm mt-1" style="color: var(--text-muted);">Solo administradores pueden gestionar tenants.</p>
      </div>
    } @else {
      <div class="space-y-5 fade-in">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 class="page-title">Gestión de tenants</h1>
            <p class="page-subtitle">{{ tenants().length }} tenants registrados</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <button (click)="reload()" [disabled]="loading()" class="btn-ghost text-xs">Actualizar</button>
            <button (click)="openCreate()" class="btn-primary text-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Nuevo Tenant
            </button>
          </div>
        </div>

        <div class="surface p-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <label class="inline-flex items-center gap-3 cursor-pointer select-none">
            <input type="checkbox" class="sr-only" [ngModel]="soloActivos()" (ngModelChange)="setSoloActivos($event)" />
            <span class="relative inline-flex h-6 w-11 rounded-full transition-colors"
                  [style.background]="soloActivos() ? 'var(--accent)' : 'var(--bg-elevated)'"
                  style="border: 1px solid var(--border);">
              <span class="absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform"
                    [style.transform]="soloActivos() ? 'translateX(20px)' : 'translateX(2px)'"></span>
            </span>
            <span class="text-sm font-semibold" style="color: var(--text-primary);">Solo activos</span>
          </label>
          <span class="text-xs" style="color: var(--text-muted);">Administración multi-tenant del sistema</span>
        </div>

        @if (error()) {
          <div class="rounded-2xl px-4 py-3 text-sm"
               style="background: rgba(251,113,133,0.12); border: 1px solid rgba(251,113,133,0.22); color: var(--danger);">
            {{ error() }}
          </div>
        }

        @if (showForm()) {
          <div class="surface p-5">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h2 class="text-base font-semibold" style="color: var(--text-primary);">
                  {{ editingTenant() ? 'Editar tenant' : 'Crear tenant' }}
                </h2>
                <p class="text-xs mt-1" style="color: var(--text-muted);">Nombre obligatorio, descripción opcional.</p>
              </div>
              <button (click)="closeForm()" class="btn-ghost text-xs">Cerrar</button>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wider mb-1.5" style="color: var(--text-muted);">Nombre</label>
                <input [(ngModel)]="form.nombre" class="input" maxlength="120" placeholder="Nombre del tenant" />
              </div>
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wider mb-1.5" style="color: var(--text-muted);">Descripción</label>
                <input [(ngModel)]="form.descripcion" class="input" maxlength="255" placeholder="Descripción opcional" />
              </div>
            </div>

            @if (editingTenant()) {
              <label class="inline-flex items-center gap-3 mt-4 cursor-pointer select-none">
                <input type="checkbox" [(ngModel)]="formActivo" class="w-4 h-4" />
                <span class="text-sm" style="color: var(--text-primary);">Tenant activo</span>
              </label>
            }

            @if (formError()) {
              <p class="text-xs mt-3" style="color: var(--danger);">{{ formError() }}</p>
            }

            <div class="flex flex-col sm:flex-row gap-2 mt-5">
              <button (click)="save()" [disabled]="saving() || !form.nombre.trim()" class="btn-primary flex-1 sm:flex-none">
                {{ saving() ? 'Guardando...' : (editingTenant() ? 'Actualizar tenant' : 'Crear tenant') }}
              </button>
              <button (click)="closeForm()" class="btn-ghost">Cancelar</button>
            </div>
          </div>
        }

        @if (loading()) {
          <div class="space-y-2">
            @for (_ of [1,2,3,4,5]; track $index) {
              <div class="h-14 shimmer rounded-xl"></div>
            }
          </div>
        } @else if (tenants().length === 0) {
          <div class="surface p-16 text-center">
            <p class="text-sm" style="color: var(--text-muted);">No hay tenants para mostrar</p>
            <button (click)="openCreate()" class="btn-primary mt-4 text-sm">Crear primer tenant</button>
          </div>
        } @else {
          <div class="table-wrap">
            <table class="w-full">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Estado</th>
                  <th>Fecha creación</th>
                  <th class="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                @for (tenant of tenants(); track tenant.id_tenant) {
                  <tr>
                    <td>
                      <div class="flex items-center gap-3">
                        <span class="w-10 h-10 rounded-2xl inline-flex items-center justify-center flex-shrink-0"
                              style="background: var(--accent-soft); color: var(--accent); border: 1px solid var(--border);">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21H5a2 2 0 01-2-2V7a2 2 0 012-2h4l2-3h4l2 3h4a2 2 0 012 2v12a2 2 0 01-2 2z" />
                          </svg>
                        </span>
                        <span class="font-semibold text-sm" style="color: var(--text-primary);">{{ tenant.nombre }}</span>
                      </div>
                    </td>
                    <td class="max-w-md">
                      <span class="text-sm" style="color: var(--text-muted);">{{ tenant.descripcion || 'Sin descripción' }}</span>
                    </td>
                    <td>
                      <span [class]="tenant.activo ? 'badge-green badge' : 'badge-red badge'">
                        {{ tenant.activo ? 'Activo' : 'Inactivo' }}
                      </span>
                    </td>
                    <td class="text-xs numeric" style="color: var(--text-muted);">{{ formatDate(tenant.fecha_creacion) }}</td>
                    <td class="text-right">
                      <div class="flex flex-wrap items-center justify-end gap-2">
                        <button (click)="openEdit(tenant)" class="btn-ghost py-1 px-3 text-xs">Editar</button>
                        <button (click)="confirmToggle(tenant)"
                                [disabled]="actionLoadingId() === tenant.id_tenant"
                                [class]="tenant.activo ? 'btn-danger py-1 px-3 text-xs' : 'btn-success py-1 px-3 text-xs'">
                          {{ actionLoadingId() === tenant.id_tenant ? 'Procesando...' : (tenant.activo ? 'Desactivar' : 'Activar') }}
                        </button>
                      </div>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        }
      </div>
    }
  `,
})
export class TenantsComponent implements OnInit {
  protected auth = inject(AuthService);
  private tenantsService = inject(TenantsService);

  loading = signal(true);
  saving = signal(false);
  tenants = signal<Tenant[]>([]);
  soloActivos = signal(false);
  showForm = signal(false);
  editingTenant = signal<Tenant | null>(null);
  error = signal<string | null>(null);
  formError = signal<string | null>(null);
  actionLoadingId = signal<string | null>(null);
  formActivo = true;

  form: TenantCreate = { nombre: '', descripcion: '' };
  activeCount = computed(() => this.tenants().filter(t => t.activo).length);

  ngOnInit(): void {
    if (this.auth.isAdmin()) this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    this.tenantsService.listar(this.soloActivos()).subscribe({
      next: (items) => {
        this.tenants.set(items);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'No se pudieron cargar los tenants');
        this.loading.set(false);
      },
    });
  }

  setSoloActivos(value: boolean): void {
    this.soloActivos.set(value);
    this.reload();
  }

  openCreate(): void {
    this.editingTenant.set(null);
    this.form = { nombre: '', descripcion: '' };
    this.formActivo = true;
    this.formError.set(null);
    this.showForm.set(true);
  }

  openEdit(tenant: Tenant): void {
    this.editingTenant.set(tenant);
    this.form = { nombre: tenant.nombre, descripcion: tenant.descripcion || '' };
    this.formActivo = tenant.activo;
    this.formError.set(null);
    this.showForm.set(true);
  }

  closeForm(): void {
    this.showForm.set(false);
    this.editingTenant.set(null);
    this.formError.set(null);
  }

  save(): void {
    const nombre = this.form.nombre.trim();
    if (!nombre) {
      this.formError.set('El nombre es obligatorio');
      return;
    }

    this.saving.set(true);
    this.formError.set(null);
    const descripcion = this.form.descripcion?.trim() || undefined;
    const editing = this.editingTenant();

    if (editing) {
      const payload: TenantUpdate = { nombre, descripcion, activo: this.formActivo };
      this.tenantsService.actualizar(editing.id_tenant, payload).subscribe({
        next: (updated) => {
          this.tenants.update(list => list.map(item => item.id_tenant === updated.id_tenant ? updated : item));
          this.closeForm();
          this.saving.set(false);
        },
        error: (err) => {
          this.formError.set(err.error?.detail || 'No se pudo actualizar el tenant');
          this.saving.set(false);
        },
      });
      return;
    }

    this.tenantsService.crear({ nombre, descripcion }).subscribe({
      next: (created) => {
        this.tenants.update(list => [created, ...list]);
        this.closeForm();
        this.saving.set(false);
      },
      error: (err) => {
        this.formError.set(err.error?.detail || 'No se pudo crear el tenant');
        this.saving.set(false);
      },
    });
  }

  confirmToggle(tenant: Tenant): void {
    const action = tenant.activo ? 'desactivar' : 'activar';
    if (!confirm(`¿Confirmas ${action} el tenant "${tenant.nombre}"?`)) return;

    this.actionLoadingId.set(tenant.id_tenant);
    this.tenantsService.toggleActivo(tenant.id_tenant).subscribe({
      next: (updated) => {
        if (this.soloActivos() && !updated.activo) {
          this.tenants.update(list => list.filter(item => item.id_tenant !== updated.id_tenant));
        } else {
          this.tenants.update(list => list.map(item => item.id_tenant === updated.id_tenant ? updated : item));
        }
        this.actionLoadingId.set(null);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'No se pudo cambiar el estado del tenant');
        this.actionLoadingId.set(null);
      },
    });
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', year: 'numeric' });
  }
}
