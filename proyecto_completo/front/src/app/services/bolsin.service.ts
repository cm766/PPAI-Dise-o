//PATRÓN GRASP APLICADO: alta cohesión
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { InfoNotificacion } from '../models/notificacion.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class BolsinService {
  private http = inject(HttpClient);
  private auth = inject(AuthService);

  consultarUbicaciones() {
    return this.http.get(`${environment.apiUrl}/consultarb/`, {
      headers: this.auth.getAuthHeaders()
    });
  } 

  notificarGerentes(data: any): Observable<InfoNotificacion> {
    return this.http.post<InfoNotificacion>(`${environment.apiUrl}/buscarEmailGCM/`, data, {
      headers: this.auth.getAuthHeaders()
    });
  }
}
