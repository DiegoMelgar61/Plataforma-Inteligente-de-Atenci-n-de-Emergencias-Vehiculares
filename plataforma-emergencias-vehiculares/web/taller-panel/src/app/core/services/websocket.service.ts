import { Injectable, signal } from '@angular/core';
import { Subject } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface WsMessage {
  type: string;
  data: any;
}

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectTimer: any;

  readonly messages$ = new Subject<WsMessage>();
  readonly connected = signal(false);

  connect(incidentId: string): void {
    this.disconnect();
    const wsUrl = environment.wsUrl;
    this.socket = new WebSocket(`${wsUrl}/notifications/ws/incidents/${incidentId}`);

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
    this.disconnect();
    const wsUrl = environment.wsUrl;
    this.socket = new WebSocket(`${wsUrl}/notifications/ws`);

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
}
