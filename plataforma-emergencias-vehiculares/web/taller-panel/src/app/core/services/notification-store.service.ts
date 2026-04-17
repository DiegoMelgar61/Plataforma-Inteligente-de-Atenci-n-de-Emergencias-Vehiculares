import { Injectable, signal, computed } from '@angular/core';
import { Notification } from '../../models';

@Injectable({ providedIn: 'root' })
export class NotificationStore {
  private _notifications = signal<Notification[]>([]);
  readonly notifications = this._notifications.asReadonly();
  readonly unreadCount = computed(
    () => this._notifications().filter((n) => !n.read).length
  );

  push(message: string, type: Notification['type'] = 'info'): void {
    const n: Notification = {
      id: crypto.randomUUID(),
      message,
      type,
      read: false,
      timestamp: new Date(),
    };
    this._notifications.update((list) => [n, ...list].slice(0, 20));
  }

  markAllRead(): void {
    this._notifications.update((list) =>
      list.map((n) => ({ ...n, read: true }))
    );
  }

  clear(): void {
    this._notifications.set([]);
  }
}
