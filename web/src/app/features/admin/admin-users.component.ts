import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService } from '../../core/services/admin.service';
import { User, UserRole } from '../../models';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-5 fade-in">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">Gestión de usuarios</h1>
          <p class="page-subtitle">{{ filtered().length }} usuarios · Edita roles y permisos</p>
        </div>
        <button (click)="reload()" class="btn-ghost text-xs">Actualizar</button>
      </div>

      <!-- Filters bar -->
      <div class="surface p-3 flex flex-wrap items-center gap-3">
        <div class="relative flex-1 min-w-48">
          <input [(ngModel)]="search" class="input pl-8 py-2 text-sm" placeholder="Buscar por nombre o correo..." />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style="color: var(--text-muted);">/</span>
        </div>
        <div class="flex gap-1.5">
          @for (f of roleFilters; track f.value) {
            <button (click)="filterRol.set(f.value)"
                    [class]="'filter-tab ' + (filterRol() === f.value ? 'active' : '')">
              {{ f.label }}
            </button>
          }
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

      <!-- Table -->
      @if (loading()) {
        <div class="space-y-2">
          @for (_ of [1,2,3,4,5]; track $index) {
            <div class="h-14 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (filtered().length === 0) {
        <div class="surface p-16 text-center">
          <p class="text-sm" style="color: var(--text-muted);">Sin usuarios con estos filtros</p>
        </div>
      } @else {
        <div class="table-wrap" style="overflow-x: auto; -webkit-overflow-scrolling: touch;">
          <table class="w-full" style="min-width: 640px;">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Correo</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Registrado</th>
                <th class="text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              @for (u of filtered(); track u.id_usuario) {
                <tr>
                  <td>
                    <div class="flex items-center gap-2.5">
                      <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                           [style.background]="roleColor(u.rol)">
                        {{ u.nombre_completo[0].toUpperCase() }}
                      </div>
                      <span class="font-medium text-sm" style="color: var(--text-primary);">{{ u.nombre_completo }}</span>
                    </div>
                  </td>
                  <td class="font-mono text-xs">{{ u.correo_electronico }}</td>
                  <td>
                    <span [class]="'badge ' + roleBadge(u.rol)">{{ u.rol }}</span>
                  </td>
                  <td>
                    <span [class]="u.activo ? 'badge-green badge' : 'badge-red badge'">
                      {{ u.activo ? '● Activo' : '○ Inactivo' }}
                    </span>
                  </td>
                  <td class="text-xs" style="color: var(--text-muted);">
                    {{ u.fecha_creacion ? formatDate(u.fecha_creacion) : '—' }}
                  </td>
                  <td class="text-right">
                    <div class="flex items-center justify-end gap-2">
                      <button (click)="openEditRole(u)" class="btn-ghost py-1 px-3 text-xs">
                        Cambiar rol
                      </button>
                      <button (click)="toggleActive(u)"
                              [class]="u.activo ? 'btn-danger py-1 px-3 text-xs' : 'btn-success py-1 px-3 text-xs'">
                        {{ u.activo ? 'Desactivar' : 'Activar' }}
                      </button>
                    </div>
                  </td>
                </tr>
              }
            </tbody>
          </table>
          <div class="px-4 py-3" style="border-top: 1px solid var(--border);">
            <p class="text-xs" style="color: var(--text-muted);">
              Mostrando {{ filtered().length }} de {{ users().length }} usuarios
            </p>
          </div>
        </div>
      }
    </div>

    <!-- Edit Role Modal -->
    @if (editingUser()) {
      <div class="modal-overlay" (click)="editingUser.set(null)">
        <div class="modal fade-in" (click)="$event.stopPropagation()">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white"
                 [style.background]="roleColor(editingUser()!.rol)">
              {{ editingUser()!.nombre_completo[0].toUpperCase() }}
            </div>
            <div>
              <p class="font-semibold text-sm" style="color: var(--text-primary);">{{ editingUser()!.nombre_completo }}</p>
              <p class="text-xs" style="color: var(--text-muted);">{{ editingUser()!.correo_electronico }}</p>
            </div>
          </div>

          <p class="text-xs font-semibold uppercase tracking-wider mb-3" style="color: var(--text-muted);">Selecciona el nuevo rol</p>

          <div class="space-y-2 mb-5">
            @for (r of roles; track r.value) {
              <button (click)="selectedRole = r.value"
                      class="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-left"
                      [style.background]="selectedRole === r.value ? 'rgba(59,130,246,0.12)' : 'var(--bg-base)'"
                      [style.borderColor]="selectedRole === r.value ? 'rgba(59,130,246,0.3)' : 'var(--border)'"
                      style="border: 1px solid var(--border);">
                <span class="text-xl">{{ r.icon }}</span>
                <div class="flex-1">
                  <p class="text-sm font-medium" style="color: var(--text-primary);">{{ r.label }}</p>
                  <p class="text-xs" style="color: var(--text-muted);">{{ r.desc }}</p>
                </div>
                @if (selectedRole === r.value) {
                  <span style="color: var(--accent);">Seleccionado</span>
                }
              </button>
            }
          </div>

          @if (actionError()) {
            <p class="text-xs mb-3" style="color: var(--danger);">{{ actionError() }}</p>
          }

          <div class="flex gap-2">
            <button (click)="confirmRole()" [disabled]="actionLoading() || selectedRole === editingUser()!.rol"
                    class="btn-primary flex-1">
              {{ actionLoading() ? 'Guardando...' : 'Confirmar cambio' }}
            </button>
            <button (click)="editingUser.set(null)" class="btn-ghost">Cancelar</button>
          </div>
        </div>
      </div>
    }
  `,
})
export class AdminUsersComponent implements OnInit {
  private adminService = inject(AdminService);

  loading = signal(true);
  users = signal<User[]>([]);
  editingUser = signal<User | null>(null);
  actionLoading = signal(false);
  actionError = signal<string | null>(null);
  filterRol = signal('');
  filterActivo = signal('');
  search = '';
  selectedRole: UserRole = 'CLIENTE';

  roleFilters = [
    { label: 'Todos', value: '' },
    { label: 'Clientes', value: 'CLIENTE' },
    { label: 'Talleres', value: 'TALLER' },
    { label: 'Admins', value: 'ADMIN' },
  ];

  statusFilters = [
    { label: 'Cualquier estado', value: '' },
    { label: 'Activos', value: 'true' },
    { label: 'Inactivos', value: 'false' },
  ];

  roles = [
    { value: 'CLIENTE' as UserRole, label: 'Cliente', icon: 'CL', desc: 'Puede reportar incidentes desde la app móvil' },
    { value: 'TALLER' as UserRole, label: 'Taller', icon: 'TA', desc: 'Accede al panel web y gestiona incidentes' },
    { value: 'ADMIN' as UserRole, label: 'Administrador', icon: 'AD', desc: 'Acceso total al sistema y gestión de usuarios' },
  ];

  filtered = computed(() => {
    let list = this.users();
    const s = this.search.toLowerCase();
    if (s) list = list.filter(u => u.nombre_completo.toLowerCase().includes(s) || u.correo_electronico.toLowerCase().includes(s));
    if (this.filterRol()) list = list.filter(u => u.rol === this.filterRol());
    if (this.filterActivo()) list = list.filter(u => String(u.activo) === this.filterActivo());
    return list;
  });

  ngOnInit(): void { this.reload(); }

  reload(): void {
    this.loading.set(true);
    this.adminService.getUsers().subscribe({
      next: (u) => { this.users.set(u); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  openEditRole(u: User): void {
    this.editingUser.set(u);
    this.selectedRole = u.rol;
    this.actionError.set(null);
  }

  confirmRole(): void {
    const u = this.editingUser();
    if (!u || this.selectedRole === u.rol) return;
    this.actionLoading.set(true);
    this.adminService.changeRole(u.id_usuario, this.selectedRole).subscribe({
      next: (updated) => {
        this.users.update(list => list.map(x => x.id_usuario === updated.id_usuario ? updated : x));
        this.editingUser.set(null);
        this.actionLoading.set(false);
      },
      error: (err) => {
        this.actionError.set(err.error?.detail || 'Error al cambiar rol');
        this.actionLoading.set(false);
      },
    });
  }

  toggleActive(u: User): void {
    this.adminService.toggleActive(u.id_usuario, !u.activo).subscribe({
      next: (updated) => this.users.update(list => list.map(x => x.id_usuario === updated.id_usuario ? updated : x)),
    });
  }

  roleColor(rol: string): string {
    return { ADMIN: 'var(--purple)', TALLER: 'var(--accent)', CLIENTE: 'var(--text-muted)' }[rol] || 'var(--text-muted)';
  }

  roleBadge(rol: string): string {
    return { ADMIN: 'badge-purple', TALLER: 'badge-blue', CLIENTE: 'badge-gray' }[rol] || 'badge-gray';
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', year: '2-digit' });
  }
}
