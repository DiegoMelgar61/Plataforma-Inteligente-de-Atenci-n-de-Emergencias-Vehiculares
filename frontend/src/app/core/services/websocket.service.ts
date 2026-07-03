import { Injectable, signal } from '@angular/core';
import { Subject } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface WsMessage {
  type?: string;
  tipo?: string;
  data?: any;
  clasificacion?: string;
  prioridad?: string;
  mensaje?: string;
  nuevo_estado?: string;
  incidente_id?: string;
  [key: string]: any;
}

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectTimer: any;

  readonly messages$ = new Subject<WsMessage>();
  readonly connected = signal(false);

  connect(incidentId: number): void {
    this.disconnect();
    const wsUrl = environment.wsUrl;
    const token = this.getTokenParam();
    this.socket = new WebSocket(`${wsUrl}/notifications/ws/incidents/${incidentId}${token}`);

    this.socket.onopen = () => this.connected.set(true);
    this.socket.onclose = () => {
      if (!this.connected()) return;
      this.connected.set(false);
      this.reconnectTimer = setTimeout(() => this.connect(incidentId), 5000);
    };
    this.socket.onerror = () => this.connected.set(false);
    this.socket.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data);
        this.messages$.next(msg);
      } catch { /* ignore parse errors */ }
    };
  }

  connectGlobal(): void {
    if (
      this.socket &&
      (this.socket.readyState === WebSocket.OPEN ||
        this.socket.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }
    this.disconnect();
    const wsUrl = environment.wsUrl;
    const token = this.getTokenParam();
    this.socket = new WebSocket(`${wsUrl}/notifications/ws${token}`);

    this.socket.onopen = () => this.connected.set(true);
    this.socket.onclose = () => {
      if (!this.connected()) return;
      this.connected.set(false);
      this.reconnectTimer = setTimeout(() => this.connectGlobal(), 5000);
    };
    this.socket.onerror = () => this.connected.set(false);
    this.socket.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data);
        this.messages$.next(msg);
      } catch { /* ignore */ }
    };
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.connected.set(false);
  }

  send(data: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }

  private getTokenParam(): string {
    const token = localStorage.getItem('token');
    return token ? `?token=${encodeURIComponent(token)}` : '';
  }
}
