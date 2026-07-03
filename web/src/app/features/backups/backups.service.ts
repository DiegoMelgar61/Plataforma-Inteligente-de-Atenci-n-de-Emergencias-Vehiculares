import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class BackupsService {
  private http = inject(HttpClient);
  private api = `${environment.apiUrl}/backups`;

  /** Descarga el respaldo SQL manual como Blob. */
  descargarManual(): Observable<Blob> {
    return this.http.get(`${this.api}/manual`, { responseType: 'blob' });
  }

  /** Dispara la descarga de un Blob en el navegador. */
  guardarArchivo(blob: Blob, nombre: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}
