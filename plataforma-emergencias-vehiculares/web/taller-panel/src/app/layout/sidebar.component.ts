import { Component, inject, Input, Output, EventEmitter } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../core/services/auth.service';

interface NavItem {
  label: string;
  icon: string;
  route: string;
  adminOnly?: boolean;
  badge?: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  styles: [`
    :host { display: contents; }
    .nav-link {
      display: flex; align-items: center; gap: 10px; padding: 8px 12px;
      border-radius: 8px; font-size: 13.5px; font-weight: 500;
      color: var(--text-muted); transition: all 0.15s ease;
      text-decoration: none; cursor: pointer; white-space: nowrap;
      border: 1px solid transparent;
    }
    .nav-link:hover { color: var(--text-primary); background: var(--bg-elevated); border-color: var(--border); }
    .nav-link.active {
      color: var(--accent) !important;
      background: var(--accent-glow);
      border-color: rgba(59,130,246,0.2);
    }
    .nav-link.active .icon-wrap { color: var(--accent); }
    .icon-wrap { width: 20px; text-align: center; font-size: 15px; flex-shrink: 0; }
    .sidebar { transition: width 0.25s ease; overflow: hidden; }
    .logo-text, .nav-label, .section-label, .user-info {
      transition: opacity 0.2s ease, max-width 0.2s ease;
      overflow: hidden; white-space: nowrap;
    }
    .collapsed .logo-text,
    .collapsed .nav-label,
    .collapsed .section-label,
    .collapsed .user-info {
      opacity: 0; max-width: 0; pointer-events: none;
    }
  `],
  template: `
    <aside class="sidebar fixed left-0 top-0 h-screen flex flex-col z-40"
           [class.collapsed]="collapsed"
           [style.width]="sidebarWidth"
           style="background: var(--bg-surface); border-right: 1px solid var(--border);">

      <!-- Header -->
      <div class="flex items-center h-14 px-3 flex-shrink-0" style="border-bottom: 1px solid var(--border);">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-white text-sm font-bold"
               style="background: var(--accent); box-shadow: 0 0 16px var(--accent-glow);">⚡</div>
          <span class="logo-text text-sm font-semibold" style="color: var(--text-primary);">EmergVehicular</span>
        </div>
        <button (click)="toggleSidebar.emit()"
                class="w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 transition-colors hover:bg-gray-700"
                style="color: var(--text-muted);">
          <svg class="w-4 h-4 transition-transform" [class.rotate-180]="collapsed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
          </svg>
        </button>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto p-2 space-y-0.5">

        <!-- Role badge -->
        @if (!collapsed) {
          <div class="px-3 py-2 mb-1">
            <span [class]="'badge text-xs ' + (isAdmin() ? 'badge-purple' : 'badge-blue')">
              {{ isAdmin() ? '👑 Administrador' : '🔧 Taller' }}
            </span>
          </div>
        }

        <!-- Common nav -->
        @for (item of commonNav; track item.route) {
          <a [routerLink]="item.route"
             routerLinkActive="active"
             [routerLinkActiveOptions]="{exact: item.route === '/dashboard'}"
             class="nav-link"
             [title]="collapsed ? item.label : ''">
            <span class="icon-wrap">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </a>
        }

        <!-- Admin section -->
        @if (isAdmin()) {
          <div class="pt-3 pb-1">
            <p class="section-label text-xs font-semibold uppercase tracking-widest px-3 mb-1"
               style="color: var(--text-muted);">Administración</p>
          </div>
          @for (item of adminNav; track item.route) {
            <a [routerLink]="item.route"
               routerLinkActive="active"
               class="nav-link"
               [title]="collapsed ? item.label : ''">
              <span class="icon-wrap">{{ item.icon }}</span>
              <span class="nav-label">{{ item.label }}</span>
            </a>
          }
        }
      </nav>

      <!-- User footer -->
      <div class="p-2 flex-shrink-0" style="border-top: 1px solid var(--border);">
        <div class="flex items-center gap-2.5 px-2 py-2 rounded-lg mb-1"
             style="background: var(--bg-elevated);">
          <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 text-white"
               [style.background]="isAdmin() ? 'var(--purple)' : 'var(--accent)'">
            {{ initials() }}
          </div>
          <div class="user-info flex-1 min-w-0">
            <p class="text-xs font-semibold truncate" style="color: var(--text-primary);">{{ userName() }}</p>
            <p class="text-xs truncate" style="color: var(--text-muted);">{{ userEmail() }}</p>
          </div>
        </div>
        <button (click)="logout()"
                class="nav-link w-full text-left"
                style="color: var(--danger);">
          <span class="icon-wrap">→</span>
          <span class="nav-label">Salir</span>
        </button>
      </div>
    </aside>
  `,
})
export class SidebarComponent {
  private auth = inject(AuthService);

  @Input() collapsed = false;
  @Input() isMobile = false;
  @Output() toggleSidebar = new EventEmitter<void>();

  isAdmin = this.auth.isAdmin;

  get sidebarWidth(): string {
    if (this.collapsed) return this.isMobile ? '0px' : '64px';
    return '240px';
  }

  commonNav: NavItem[] = [
    { label: 'Dashboard', icon: '◈', route: '/dashboard' },
    { label: 'Solicitudes', icon: '🚨', route: '/requests' },
    { label: 'Asignaciones', icon: '📋', route: '/assignments' },
    { label: 'Técnicos', icon: '👷', route: '/technicians' },
    { label: 'Mapa en vivo', icon: '🗺', route: '/map' },
    { label: 'Pagos', icon: '💰', route: '/payments' },
    { label: 'Historial', icon: '📜', route: '/history' },
  ];

  adminNav: NavItem[] = [
    { label: 'Usuarios', icon: '👥', route: '/admin/users' },
    { label: 'Talleres', icon: '🏪', route: '/admin/workshops' },
  ];

  userName = () => this.auth.user()?.nombre_completo || 'Usuario';
  userEmail = () => this.auth.user()?.correo_electronico || '';
  initials = () => {
    const n = this.auth.user()?.nombre_completo || 'U';
    return n.split(' ').map((w: string) => w[0]).slice(0, 2).join('').toUpperCase();
  };

  logout() { this.auth.logout(); }
}
