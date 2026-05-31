import { Component, inject, Input, Output, EventEmitter } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../core/services/auth.service';

interface NavItem {
  label: string;
  icon: 'dashboard' | 'requests' | 'assignments' | 'technicians' | 'map' | 'payments' | 'history' | 'users' | 'workshops' | 'tenants';
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
      display: flex; align-items: center; gap: 12px; padding: 10px 12px;
      border-radius: 12px; font-size: 13px; font-weight: 600;
      color: rgba(255,255,255,0.62); transition: all 250ms ease;
      text-decoration: none; cursor: pointer; white-space: nowrap;
    }
    .nav-link:hover { color: #fff; background: rgba(255,255,255,0.06); }
    .nav-link.active {
      color: #fff !important;
      background: var(--accent-gradient);
      box-shadow: var(--neon-glow);
    }
    .nav-link:hover .icon-wrap, .nav-link.active .icon-wrap { color: #fff; opacity: 1; }
    .icon-wrap { width: 20px; height: 20px; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; opacity: 0.84; transition: color 250ms ease, opacity 250ms ease; }
    .icon-wrap svg { width: 18px; height: 18px; }
    .sidebar { transition: width 250ms ease, opacity 250ms ease; overflow: hidden; }
    .sidebar-header, .brand, .user-card, .logout-link {
      transition: all 250ms ease;
    }
    .logo-text, .nav-label, .section-label, .user-info {
      transition: opacity 250ms ease, max-width 250ms ease;
      overflow: hidden; white-space: nowrap;
    }
    .nav-label { max-width: 160px; }
    .collapsed .logo-text,
    .collapsed .nav-label,
    .collapsed .section-label,
    .collapsed .user-info {
      opacity: 0; max-width: 0; pointer-events: none;
    }
    .collapsed .nav-link {
      justify-content: center;
      gap: 0;
      padding: 10px;
    }
    .collapsed .sidebar-header {
      justify-content: center;
    }
    .collapsed .brand {
      opacity: 0;
      max-width: 0;
      overflow: hidden;
      pointer-events: none;
    }
    .collapsed .user-card {
      justify-content: center;
      padding: 10px;
    }
    .collapsed .logout-link {
      justify-content: center;
      gap: 0;
      padding: 10px;
    }
  `],
  template: `
    <aside class="sidebar fixed left-3 top-3 bottom-3 flex flex-col z-40"
           [class.collapsed]="collapsed"
           [style.width]="sidebarWidth"
           [style.opacity]="collapsed && isMobile ? '0' : '1'"
           [style.pointer-events]="collapsed && isMobile ? 'none' : 'auto'"
           style="background: var(--sidebar-bg); border-radius: 24px; box-shadow: 0 22px 60px rgba(22,18,31,0.24); overflow: hidden;">

      <!-- Header -->
      <div class="sidebar-header flex items-center h-16 px-3 flex-shrink-0" style="border-bottom: 1px solid rgba(255,255,255,0.08);">
        <div class="brand flex items-center gap-3 flex-1 min-w-0">
          <div class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 text-white"
               style="background: var(--accent-gradient); box-shadow: var(--neon-glow);">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17l5-10 5 10M9 13h6"/>
            </svg>
          </div>
          <span class="logo-text text-sm font-bold tracking-tight" style="color: #fff;">EmergVehicular</span>
        </div>
        <button (click)="toggleSidebar.emit()"
                class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
                style="color: rgba(255,255,255,0.62); background: rgba(255,255,255,0.05);">
          <svg class="w-4 h-4 transition-transform" [class.rotate-180]="collapsed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
          </svg>
        </button>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto p-3 space-y-1">

        <!-- Common nav -->
        @for (item of commonNav; track item.route) {
          <a [routerLink]="item.route"
             routerLinkActive="active"
             [routerLinkActiveOptions]="{exact: item.route === '/dashboard'}"
             class="nav-link"
             [title]="collapsed ? item.label : ''">
            <span class="icon-wrap" [innerHTML]="navIcon(item.icon)"></span>
            <span class="nav-label">{{ item.label }}</span>
          </a>
        }

        <!-- Admin section -->
        @if (isAdmin()) {
          <div class="pt-3 pb-1">
            <p class="section-label text-xs font-semibold uppercase tracking-widest px-3 mb-1"
               style="color: rgba(255,255,255,0.42);">Administración</p>
          </div>
          @for (item of adminNav; track item.route) {
            <a [routerLink]="item.route"
               routerLinkActive="active"
               class="nav-link"
               [title]="collapsed ? item.label : ''">
              <span class="icon-wrap" [innerHTML]="navIcon(item.icon)"></span>
              <span class="nav-label">{{ item.label }}</span>
            </a>
          }
        }
      </nav>

      <!-- User footer -->
      <div class="p-3 flex-shrink-0" style="border-top: 1px solid rgba(255,255,255,0.08);">
        <div class="user-card flex items-center gap-3 px-3 py-3 rounded-2xl mb-2"
             style="background: rgba(255,255,255,0.06);">
          <div class="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
               style="background: var(--accent-gradient); color: #fff;">
            {{ initials() }}
          </div>
          <div class="user-info flex-1 min-w-0">
            <p class="text-xs font-semibold truncate" style="color: #fff;">{{ userName() }}</p>
            <p class="text-xs truncate" style="color: rgba(255,255,255,0.48);">{{ userEmail() }}</p>
          </div>
        </div>
        <button (click)="logout()"
                class="logout-link nav-link w-full text-left"
                style="color: var(--danger);">
          <span class="icon-wrap">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12H3m12 0l-4-4m4 4l-4 4m7-10v12"/></svg>
          </span>
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
    return '224px';
  }

  commonNav: NavItem[] = [
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Solicitudes', icon: 'requests', route: '/requests' },
    { label: 'Asignaciones', icon: 'assignments', route: '/assignments' },
    { label: 'Técnicos', icon: 'technicians', route: '/technicians' },
    { label: 'Mapa en vivo', icon: 'map', route: '/map' },
    { label: 'Pagos', icon: 'payments', route: '/payments' },
    { label: 'Historial', icon: 'history', route: '/history' },
  ];

  adminNav: NavItem[] = [
    { label: 'Usuarios', icon: 'users', route: '/admin/users' },
    { label: 'Talleres', icon: 'workshops', route: '/admin/workshops' },
    { label: 'Tenants', icon: 'tenants', route: '/tenants' },
  ];

  navIcon(icon: NavItem['icon']): string {
    const icons: Record<NavItem['icon'], string> = {
      dashboard: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 13h6V4H4v9zm10 7h6V4h-6v16zM4 20h6v-4H4v4z"/></svg>',
      requests: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v4m0 4h.01M10.3 4.4L2.8 18a2 2 0 001.7 3h15a2 2 0 001.7-3L13.7 4.4a2 2 0 00-3.4 0z"/></svg>',
      assignments: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5h6m-8 4h10M7 13h6m-6 4h4M5 3h14v18H5V3z"/></svg>',
      technicians: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 12a4 4 0 100-8 4 4 0 000 8zm-7 9a7 7 0 0114 0"/></svg>',
      map: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 18l-6 3V6l6-3 6 3 6-3v15l-6 3-6-3zm0 0V3m6 18V6"/></svg>',
      payments: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7h18v10H3V7zm3 3h4m7 4h1"/></svg>',
      history: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v5l3 2m5-3a8 8 0 11-2.3-5.7L20 8"/></svg>',
      users: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2m8-10a4 4 0 100-8 4 4 0 000 8m14 10v-2a4 4 0 00-3-3.87m-4-11.26a4 4 0 010 7.75"/></svg>',
      workshops: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21h18M5 21V8l7-4 7 4v13M9 21v-6h6v6"/></svg>',
      tenants: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21H5a2 2 0 01-2-2V7a2 2 0 012-2h4l2-3h4l2 3h4a2 2 0 012 2v12a2 2 0 01-2 2zM12 11a3 3 0 100 6 3 3 0 000-6z"/></svg>',
    };
    return icons[icon];
  }

  userName = () => this.auth.user()?.nombre_completo || 'Usuario';
  userEmail = () => this.auth.user()?.correo_electronico || '';
  initials = () => {
    const n = this.auth.user()?.nombre_completo || 'U';
    return n.split(' ').map((w: string) => w[0]).slice(0, 2).join('').toUpperCase();
  };

  logout() { this.auth.logout(); }
}
