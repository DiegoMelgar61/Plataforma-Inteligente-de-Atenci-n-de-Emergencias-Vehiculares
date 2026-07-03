import { Component, inject, signal, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../core/services/auth.service';
import { NotificationStore } from '../features/notifications/notification-store.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  styles: [`
    :host { display: block; }
    .notif-panel {
      position: absolute; right: 0; top: calc(100% + 12px); width: 340px;
      background: var(--bg-surface); border: 1px solid var(--border-strong);
      border-radius: 22px; box-shadow: 0 18px 48px rgba(80,60,160,0.14);
      z-index: 100; overflow: hidden;
      animation: fadeIn 0.15s ease-out;
    }
  `],
  template: `
    <header class="h-20 flex items-center justify-between px-4 sm:px-6 flex-shrink-0"
            style="background: transparent;">

      <div class="flex items-center gap-3 min-w-0 flex-1">
        <!-- Mobile hamburger -->
        @if (isMobile) {
          <button (click)="toggleSidebar.emit()"
                  class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 transition-colors"
                  style="color: var(--text-secondary); background: var(--bg-surface); box-shadow: var(--shadow-card);">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
        }
        <div class="hidden md:flex items-center gap-3 h-12 max-w-xl flex-1 rounded-full px-4"
             style="background: var(--bg-surface); border: 1px solid var(--border); box-shadow: var(--shadow-card); color: var(--text-muted);">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35m1.1-5.4a6.5 6.5 0 11-13 0 6.5 6.5 0 0113 0z"/>
          </svg>
          <span class="text-sm truncate">Buscar solicitudes, técnicos o pagos</span>
          <span class="ml-auto text-[11px] font-semibold px-2 py-1 rounded-full" style="background: var(--bg-elevated); color: var(--text-muted);">Visual</span>
        </div>
      </div>

      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Status indicator -->
        <div class="hidden sm:flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold"
             style="background: var(--bg-surface); border: 1px solid var(--border); color: var(--text-secondary); box-shadow: var(--shadow-card);">
          <span class="rounded-full" style="width: 8px; height: 8px; background: var(--success); box-shadow: 0 0 0 4px rgba(52,211,153,0.16);"></span>
          Tiempo real
        </div>

        <!-- Notifications -->
        <div class="relative">
          <button (click)="notifOpen.set(!notifOpen())"
                  class="relative w-11 h-11 rounded-full flex items-center justify-center transition-all"
                  style="color: var(--text-muted);"
                  [style.background]="notifOpen() ? 'var(--accent-soft)' : 'var(--bg-surface)'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
            @if (notifStore.unreadCount() > 0) {
              <span class="absolute top-2 right-2 min-w-4 h-4 px-1 rounded-full text-[10px] leading-4 text-white font-bold"
                    style="background: var(--danger); box-shadow: 0 6px 14px rgba(251,113,133,0.28);">{{ notifStore.unreadCount() }}</span>
            }
          </button>

          @if (notifOpen()) {
            <div class="notif-panel">
              <div class="flex items-center justify-between px-4 py-3"
                   style="border-bottom: 1px solid var(--border);">
                <p class="text-sm font-semibold" style="color: var(--text-primary);">Notificaciones</p>
                @if (notifStore.unreadCount() > 0) {
                  <button (click)="notifStore.markAllRead()" class="text-xs" style="color: var(--accent);">
                    Marcar todas leídas
                  </button>
                }
              </div>
              <div class="max-h-72 overflow-y-auto">
                @if (notifStore.notifications().length === 0) {
                  <div class="flex flex-col items-center justify-center py-10 text-center">
                    <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--text-dim);">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.4-1.4A2 2 0 0118 14.2V11a6 6 0 00-4-5.7V5a2 2 0 10-4 0v.3A6 6 0 006 11v3.2a2 2 0 01-.6 1.4L4 17h11zm0 0v1a3 3 0 11-6 0v-1"/>
                    </svg>
                    <p class="text-sm" style="color: var(--text-muted);">Sin notificaciones</p>
                  </div>
                } @else {
                  @for (n of notifStore.notifications(); track n.id) {
                    <div class="px-4 py-3 transition-colors"
                          [style.background]="n.read ? 'transparent' : 'var(--accent-soft)'"
                         style="border-bottom: 1px solid var(--border);">
                      <p class="text-sm" style="color: var(--text-primary);">{{ n.message }}</p>
                      <p class="text-xs mt-0.5" style="color: var(--text-muted);">
                        {{ n.timestamp | date:'HH:mm · dd/MM' }}
                      </p>
                    </div>
                  }
                }
              </div>
            </div>
            <div class="fixed inset-0 z-90" (click)="notifOpen.set(false)"></div>
          }
        </div>

        <!-- Avatar -->
        <div class="flex items-center gap-2.5 pl-1 sm:pl-2">
          <div class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-bold text-white"
               style="background: var(--accent-gradient); box-shadow: 0 12px 28px rgba(124,92,255,0.20);">
            {{ initials() }}
          </div>
          <div class="hidden sm:block">
            <p class="text-xs font-medium leading-none" style="color: var(--text-primary);">{{ auth.user()?.nombre_completo }}</p>
            <p class="text-xs mt-0.5" style="color: var(--text-muted);">{{ auth.user()?.rol }}</p>
          </div>
        </div>
      </div>
    </header>
  `,
})
export class NavbarComponent {
  protected auth = inject(AuthService);
  protected notifStore = inject(NotificationStore);
  notifOpen = signal(false);

  @Input() isMobile = false;
  @Output() toggleSidebar = new EventEmitter<void>();

  initials = () => {
    const n = this.auth.user()?.nombre_completo || 'U';
    return n.split(' ').map((w: string) => w[0]).slice(0, 2).join('').toUpperCase();
  };
}
