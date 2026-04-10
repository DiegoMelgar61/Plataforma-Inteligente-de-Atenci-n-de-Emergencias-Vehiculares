import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../core/services/auth.service';
import { NotificationStore } from '../core/services/notification-store.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  styles: [`
    :host { display: block; }
    .notif-panel {
      position: absolute; right: 0; top: calc(100% + 8px); width: 340px;
      background: var(--bg-elevated); border: 1px solid var(--border-strong);
      border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.4);
      z-index: 100; overflow: hidden;
      animation: fadeIn 0.15s ease-out;
    }
  `],
  template: `
    <header class="h-14 flex items-center justify-between px-6 flex-shrink-0"
            style="background: var(--bg-surface); border-bottom: 1px solid var(--border);">

      <!-- Breadcrumb area (dynamic via title service ideally) -->
      <div class="flex items-center gap-2 text-sm" style="color: var(--text-muted);">
        <span>Panel</span>
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
        <span style="color: var(--text-secondary);" class="font-medium">{{ auth.isAdmin() ? 'Administrador' : 'Taller' }}</span>
      </div>

      <div class="flex items-center gap-2">
        <!-- Status indicator -->
        <div class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs"
             style="background: var(--bg-elevated); color: var(--text-muted);">
          <span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
          Online
        </div>

        <!-- Notifications -->
        <div class="relative">
          <button (click)="notifOpen.set(!notifOpen())"
                  class="relative w-9 h-9 rounded-lg flex items-center justify-center transition-colors"
                  style="color: var(--text-muted);"
                  [style.background]="notifOpen() ? 'var(--bg-elevated)' : 'transparent'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
            @if (notifStore.unreadCount() > 0) {
              <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full"
                    style="background: var(--accent); box-shadow: 0 0 8px var(--accent-glow);"></span>
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
                    <span class="text-3xl mb-2">🔔</span>
                    <p class="text-sm" style="color: var(--text-muted);">Sin notificaciones</p>
                  </div>
                } @else {
                  @for (n of notifStore.notifications(); track n.id) {
                    <div class="px-4 py-3 transition-colors"
                         [style.background]="n.read ? 'transparent' : 'rgba(59,130,246,0.05)'"
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
        <div class="flex items-center gap-2.5 pl-2">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
               [style.background]="auth.isAdmin() ? 'var(--purple)' : 'var(--accent)'">
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

  initials = () => {
    const n = this.auth.user()?.nombre_completo || 'U';
    return n.split(' ').map((w: string) => w[0]).slice(0, 2).join('').toUpperCase();
  };
}
