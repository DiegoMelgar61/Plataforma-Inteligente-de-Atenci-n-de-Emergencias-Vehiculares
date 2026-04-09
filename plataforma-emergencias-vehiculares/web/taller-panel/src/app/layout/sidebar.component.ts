import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../core/services/auth.service';

interface NavItem {
  label: string;
  icon: string;
  route: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  template: `
    <aside class="h-screen w-64 bg-gray-900 text-white flex flex-col fixed left-0 top-0 z-30">
      <!-- Logo -->
      <div class="p-6 border-b border-gray-700">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <div>
            <p class="font-bold text-sm leading-tight">Panel Taller</p>
            <p class="text-gray-400 text-xs">Gestión de emergencias</p>
          </div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
        @for (item of navItems; track item.route) {
          <a [routerLink]="item.route"
             routerLinkActive="bg-blue-600 text-white"
             [routerLinkActiveOptions]="{exact: item.route === '/dashboard'}"
             class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition-colors text-sm font-medium">
            <span class="text-lg">{{ item.icon }}</span>
            {{ item.label }}
          </a>
        }
      </nav>

      <!-- User info + logout -->
      <div class="p-4 border-t border-gray-700">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
            {{ initials() }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate">{{ userName() }}</p>
            <p class="text-xs text-gray-400">Taller</p>
          </div>
        </div>
        <button (click)="logout()"
          class="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-gray-800 rounded-lg transition-colors">
          <span>🚪</span> Cerrar sesión
        </button>
      </div>
    </aside>
  `,
})
export class SidebarComponent {
  private auth = inject(AuthService);

  navItems: NavItem[] = [
    { label: 'Dashboard', icon: '📊', route: '/dashboard' },
    { label: 'Solicitudes', icon: '🚨', route: '/requests' },
    { label: 'Mis Asignaciones', icon: '📋', route: '/assignments' },
    { label: 'Técnicos', icon: '👷', route: '/technicians' },
    { label: 'Mapa en vivo', icon: '🗺️', route: '/map' },
    { label: 'Historial', icon: '📜', route: '/history' },
  ];

  userName = () => this.auth.user()?.nombre_completo || 'Taller';
  initials = () => {
    const name = this.auth.user()?.nombre_completo || 'T';
    return name.split(' ').map((n: string) => n[0]).slice(0, 2).join('').toUpperCase();
  };

  logout() {
    this.auth.logout();
  }
}
