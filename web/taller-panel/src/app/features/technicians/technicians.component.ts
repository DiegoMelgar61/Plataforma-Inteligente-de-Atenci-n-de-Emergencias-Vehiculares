import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TechniciansService } from '../../core/services/technicians.service';
import { Tecnico, TecnicoCreate } from '../../models';

@Component({
  selector: 'app-technicians',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-5 fade-in">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="page-title">Gestión de técnicos</h1>
          <p class="page-subtitle">{{ tecnicos().length }} técnicos · {{ disponibles() }} disponibles ahora</p>
        </div>
        <button (click)="openForm()" class="btn-primary text-sm">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo técnico
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="stat-card">
          <div class="stat-icon">T</div>
          <div>
            <p class="stat-label">Total</p>
            <p class="stat-value">{{ tecnicos().length }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">D</div>
          <div>
            <p class="stat-label">Disponibles</p>
            <p class="stat-value" style="color:var(--success);">{{ disponibles() }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">O</div>
          <div>
            <p class="stat-label">Ocupados</p>
            <p class="stat-value" style="color:var(--text-muted);">{{ ocupados() }}</p>
          </div>
        </div>
      </div>

      <!-- List -->
      @if (loading()) {
        <div class="space-y-2">
          @for (_ of [1,2,3]; track $index) {
            <div class="h-20 shimmer rounded-xl"></div>
          }
        </div>
      } @else if (tecnicos().length === 0) {
        <div class="surface p-16 text-center">
          <p class="text-sm font-medium" style="color: var(--text-secondary);">Sin técnicos registrados</p>
          <p class="text-xs mt-1 mb-4" style="color: var(--text-muted);">Agrega técnicos para asignarlos a emergencias</p>
          <button (click)="openForm()" class="btn-primary text-sm">Agregar primer técnico</button>
        </div>
      } @else {
        <div class="table-wrap">
          <table class="w-full">
            <thead>
              <tr>
                <th>Técnico</th>
                <th>Teléfono</th>
                <th>Estado</th>
                <th>Registrado</th>
                <th class="text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              @for (t of tecnicos(); track t.id_tecnico) {
                <tr>
                  <td>
                    <div class="flex items-center gap-2.5">
                      <div class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
                           [style.background]="t.disponible ? 'var(--success)' : 'var(--text-muted)'">
                        {{ t.nombre_completo[0].toUpperCase() }}
                      </div>
                      <span class="font-medium text-sm" style="color: var(--text-primary);">{{ t.nombre_completo }}</span>
                    </div>
                  </td>
                  <td class="font-mono text-xs">{{ t.telefono || '—' }}</td>
                  <td>
                    <span [class]="t.disponible ? 'badge-green badge' : 'badge-gray badge'">
                      {{ t.disponible ? '● Disponible' : '○ Ocupado' }}
                    </span>
                  </td>
                  <td class="text-xs" style="color: var(--text-muted);">{{ formatDate(t.fecha_creacion) }}</td>
                  <td class="text-right">
                    <div class="flex items-center justify-end gap-2">
                      <button (click)="toggleDisponible(t)"
                              [class]="t.disponible ? 'btn-ghost py-1 px-3 text-xs' : 'btn-success py-1 px-3 text-xs'">
                        {{ t.disponible ? 'Marcar ocupado' : 'Marcar libre' }}
                      </button>
                      <button (click)="openForm(t)" class="btn-ghost py-1 px-3 text-xs">Editar</button>
                      <button (click)="confirmDelete(t)" class="btn-danger py-1 px-3 text-xs">Eliminar</button>
                    </div>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </div>

    <!-- Form Modal -->
    @if (showForm()) {
      <div class="modal-overlay" (click)="cancelForm()">
        <div class="modal fade-in" (click)="$event.stopPropagation()">
          <h2 class="text-base font-semibold mb-5" style="color: var(--text-primary);">
            {{ editingId() ? 'Editar técnico' : 'Nuevo técnico' }}
          </h2>
          @if (formError()) {
            <div class="text-xs rounded-lg px-3 py-2.5 mb-4"
                 style="background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.2);">
              {{ formError() }}
            </div>
          }
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-medium mb-1.5" style="color: var(--text-secondary);">Nombre completo *</label>
              <input type="text" [(ngModel)]="form.nombre_completo" class="input" placeholder="Juan Pérez García" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1.5" style="color: var(--text-secondary);">Teléfono</label>
              <input type="tel" [(ngModel)]="form.telefono" class="input" placeholder="+591 76543210" />
            </div>
            <div class="flex items-center gap-3 p-3 rounded-lg" style="background: var(--bg-base); border: 1px solid var(--border);">
              <input type="checkbox" [(ngModel)]="form.disponible" id="disp" class="w-4 h-4 rounded" />
              <label for="disp" class="text-sm cursor-pointer" style="color: var(--text-secondary);">Disponible para atender emergencias</label>
            </div>
          </div>
          <div class="flex gap-2 mt-5">
            <button (click)="saveForm()" [disabled]="formLoading() || !form.nombre_completo" class="btn-primary flex-1">
              {{ formLoading() ? 'Guardando...' : (editingId() ? 'Actualizar' : 'Agregar técnico') }}
            </button>
            <button (click)="cancelForm()" class="btn-ghost">Cancelar</button>
          </div>
        </div>
      </div>
    }

    <!-- Delete confirm -->
    @if (deletingTecnico()) {
      <div class="modal-overlay" (click)="deletingTecnico.set(null)">
        <div class="modal fade-in" (click)="$event.stopPropagation()" style="max-width: 380px;">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mx-auto mb-4"
               style="background: rgba(239,68,68,0.1); color: var(--danger);">!</div>
          <h3 class="text-base font-semibold text-center mb-2" style="color: var(--text-primary);">Eliminar técnico</h3>
          <p class="text-sm text-center mb-5" style="color: var(--text-muted);">
            ¿Eliminar a <strong style="color: var(--text-secondary);">{{ deletingTecnico()!.nombre_completo }}</strong>? Esta acción no puede deshacerse.
          </p>
          <div class="flex gap-2">
            <button (click)="deleteTecnico()" [disabled]="formLoading()" class="btn-danger flex-1">
              {{ formLoading() ? 'Eliminando...' : 'Sí, eliminar' }}
            </button>
            <button (click)="deletingTecnico.set(null)" class="btn-ghost flex-1">Cancelar</button>
          </div>
        </div>
      </div>
    }
  `,
})
export class TechniciansComponent implements OnInit {
  private svc = inject(TechniciansService);

  loading = signal(true);
  tecnicos = signal<Tecnico[]>([]);
  showForm = signal(false);
  editingId = signal<string | null>(null);
  formLoading = signal(false);
  formError = signal<string | null>(null);
  deletingTecnico = signal<Tecnico | null>(null);

  form: TecnicoCreate & { disponible: boolean } = { nombre_completo: '', telefono: '', disponible: true };

  disponibles = computed(() => this.tecnicos().filter(t => t.disponible).length);
  ocupados = computed(() => this.tecnicos().filter(t => !t.disponible).length);

  ngOnInit(): void { this.reload(); }

  reload(): void {
    this.loading.set(true);
    this.svc.getAll().subscribe({
      next: (list) => { this.tecnicos.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  openForm(t?: Tecnico): void {
    this.editingId.set(t?.id_tecnico ?? null);
    this.form = t ? { nombre_completo: t.nombre_completo, telefono: t.telefono || '', disponible: t.disponible } : { nombre_completo: '', telefono: '', disponible: true };
    this.formError.set(null);
    this.showForm.set(true);
  }

  cancelForm(): void { this.showForm.set(false); this.formError.set(null); }

  saveForm(): void {
    if (!this.form.nombre_completo) return;
    this.formLoading.set(true);
    const payload: TecnicoCreate = { nombre_completo: this.form.nombre_completo, telefono: this.form.telefono || undefined, disponible: this.form.disponible };
    const id = this.editingId();
    const obs = id ? this.svc.update(id, payload) : this.svc.create(payload);
    obs.subscribe({
      next: () => { this.formLoading.set(false); this.cancelForm(); this.reload(); },
      error: (err) => { this.formError.set(err.error?.detail || 'Error al guardar'); this.formLoading.set(false); },
    });
  }

  toggleDisponible(t: Tecnico): void {
    this.svc.toggleDisponible(t.id_tecnico, !t.disponible).subscribe({ next: () => this.reload() });
  }

  confirmDelete(t: Tecnico): void { this.deletingTecnico.set(t); }

  deleteTecnico(): void {
    const t = this.deletingTecnico();
    if (!t) return;
    this.formLoading.set(true);
    this.svc.delete(t.id_tecnico).subscribe({
      next: () => { this.deletingTecnico.set(null); this.formLoading.set(false); this.reload(); },
      error: () => this.formLoading.set(false),
    });
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', year: '2-digit' });
  }
}
