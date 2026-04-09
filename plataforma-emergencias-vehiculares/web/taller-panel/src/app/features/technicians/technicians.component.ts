import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TechniciansService } from '../../core/services/technicians.service';
import { Tecnico, TecnicoCreate } from '../../models';

@Component({
  selector: 'app-technicians',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div>
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Gestión de técnicos</h1>
          <p class="text-gray-500 text-sm">Administra el equipo de tu taller</p>
        </div>
        <button (click)="showForm.set(true)" class="btn-primary flex items-center gap-2">
          <span>+</span> Nuevo técnico
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="card text-center">
          <p class="text-3xl font-bold text-blue-600">{{ tecnicos().length }}</p>
          <p class="text-xs text-gray-500 mt-1">Total</p>
        </div>
        <div class="card text-center">
          <p class="text-3xl font-bold text-green-600">{{ disponibles() }}</p>
          <p class="text-xs text-gray-500 mt-1">Disponibles</p>
        </div>
        <div class="card text-center">
          <p class="text-3xl font-bold text-gray-400">{{ ocupados() }}</p>
          <p class="text-xs text-gray-500 mt-1">Ocupados</p>
        </div>
      </div>

      <!-- Add form -->
      @if (showForm()) {
        <div class="card mb-6 border-2 border-blue-100">
          <h2 class="font-semibold text-gray-900 mb-4">{{ editingId() ? 'Editar técnico' : 'Nuevo técnico' }}</h2>
          @if (formError()) {
            <div class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 mb-4 text-sm">{{ formError() }}</div>
          }
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre completo *</label>
              <input type="text" [(ngModel)]="form.nombre_completo" class="input-field" placeholder="Juan Pérez" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
              <input type="tel" [(ngModel)]="form.telefono" class="input-field" placeholder="+591 7..." />
            </div>
          </div>
          <div class="flex items-center gap-3">
            <input type="checkbox" [(ngModel)]="form.disponible" id="disponible" class="w-4 h-4 rounded" />
            <label for="disponible" class="text-sm text-gray-700">Disponible para atender</label>
          </div>
          <div class="flex gap-3 mt-4">
            <button (click)="saveForm()" [disabled]="formLoading() || !form.nombre_completo" class="btn-primary">
              {{ formLoading() ? 'Guardando...' : (editingId() ? 'Actualizar' : 'Agregar') }}
            </button>
            <button (click)="cancelForm()" class="btn-secondary">Cancelar</button>
          </div>
        </div>
      }

      <!-- List -->
      @if (loading()) {
        <div class="space-y-3">
          @for (_ of [1,2,3]; track $index) {
            <div class="h-20 bg-gray-100 rounded-xl animate-pulse"></div>
          }
        </div>
      } @else if (tecnicos().length === 0) {
        <div class="card text-center py-16">
          <div class="text-5xl mb-4">👷</div>
          <p class="text-gray-500 font-medium">Sin técnicos registrados</p>
          <p class="text-gray-400 text-sm mt-1">Agrega técnicos para asignarlos a incidentes</p>
          <button (click)="showForm.set(true)" class="btn-primary mt-4">Agregar técnico</button>
        </div>
      } @else {
        <div class="space-y-3">
          @for (t of tecnicos(); track t.id_tecnico) {
            <div class="card flex items-center gap-4">
              <!-- Avatar -->
              <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-lg flex-shrink-0">
                {{ t.nombre_completo[0].toUpperCase() }}
              </div>

              <!-- Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-gray-900">{{ t.nombre_completo }}</h3>
                  <span [class]="t.disponible ? 'badge bg-green-100 text-green-700' : 'badge bg-gray-100 text-gray-500'">
                    {{ t.disponible ? 'Disponible' : 'Ocupado' }}
                  </span>
                </div>
                @if (t.telefono) {
                  <p class="text-sm text-gray-500">📞 {{ t.telefono }}</p>
                }
                <p class="text-xs text-gray-400">Desde {{ formatDate(t.fecha_creacion) }}</p>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-2 flex-shrink-0">
                <button
                  (click)="toggleDisponible(t)"
                  [class]="t.disponible ? 'btn-secondary text-sm' : 'btn-success text-sm'">
                  {{ t.disponible ? 'Marcar ocupado' : 'Marcar disponible' }}
                </button>
                <button (click)="edit(t)" class="btn-secondary text-sm">✏️</button>
                <button (click)="confirmDelete(t)" class="btn-danger text-sm">🗑️</button>
              </div>
            </div>
          }
        </div>
      }
    </div>

    <!-- Delete confirm modal -->
    @if (deletingTecnico()) {
      <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" (click)="deletingTecnico.set(null)">
        <div class="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl" (click)="$event.stopPropagation()">
          <h3 class="font-bold text-gray-900 text-lg mb-2">Eliminar técnico</h3>
          <p class="text-gray-500 text-sm mb-6">
            ¿Eliminar a <strong>{{ deletingTecnico()!.nombre_completo }}</strong>? Esta acción no se puede deshacer.
          </p>
          <div class="flex gap-3">
            <button (click)="deleteTecnico()" [disabled]="formLoading()" class="btn-danger flex-1">
              {{ formLoading() ? 'Eliminando...' : 'Eliminar' }}
            </button>
            <button (click)="deletingTecnico.set(null)" class="btn-secondary flex-1">Cancelar</button>
          </div>
        </div>
      </div>
    }
  `,
})
export class TechniciansComponent implements OnInit {
  private techniciansService = inject(TechniciansService);

  loading = signal(true);
  tecnicos = signal<Tecnico[]>([]);
  showForm = signal(false);
  editingId = signal<string | null>(null);
  formLoading = signal(false);
  formError = signal<string | null>(null);
  deletingTecnico = signal<Tecnico | null>(null);

  form: TecnicoCreate & { disponible: boolean } = {
    nombre_completo: '',
    telefono: '',
    disponible: true,
  };

  disponibles = () => this.tecnicos().filter(t => t.disponible).length;
  ocupados = () => this.tecnicos().filter(t => !t.disponible).length;

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.techniciansService.getAll().subscribe({
      next: (list) => { this.tecnicos.set(list); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  edit(t: Tecnico): void {
    this.editingId.set(t.id_tecnico);
    this.form = { nombre_completo: t.nombre_completo, telefono: t.telefono || '', disponible: t.disponible };
    this.showForm.set(true);
  }

  cancelForm(): void {
    this.showForm.set(false);
    this.editingId.set(null);
    this.form = { nombre_completo: '', telefono: '', disponible: true };
    this.formError.set(null);
  }

  saveForm(): void {
    if (!this.form.nombre_completo) return;
    this.formLoading.set(true);
    this.formError.set(null);
    const payload: TecnicoCreate = {
      nombre_completo: this.form.nombre_completo,
      telefono: this.form.telefono || undefined,
      disponible: this.form.disponible,
    };
    const id = this.editingId();
    const obs = id
      ? this.techniciansService.update(id, payload)
      : this.techniciansService.create(payload);

    obs.subscribe({
      next: () => {
        this.formLoading.set(false);
        this.cancelForm();
        this.reload();
      },
      error: (err) => {
        this.formError.set(err.error?.detail || 'Error al guardar');
        this.formLoading.set(false);
      },
    });
  }

  toggleDisponible(t: Tecnico): void {
    this.techniciansService.toggleDisponible(t.id_tecnico, !t.disponible).subscribe({
      next: () => this.reload(),
    });
  }

  confirmDelete(t: Tecnico): void {
    this.deletingTecnico.set(t);
  }

  deleteTecnico(): void {
    const t = this.deletingTecnico();
    if (!t) return;
    this.formLoading.set(true);
    this.techniciansService.delete(t.id_tecnico).subscribe({
      next: () => {
        this.deletingTecnico.set(null);
        this.formLoading.set(false);
        this.reload();
      },
      error: () => this.formLoading.set(false),
    });
  }

  formatDate(d: string): string {
    return new Date(d).toLocaleDateString('es-BO', { day: 'numeric', month: 'short', year: 'numeric' });
  }
}
