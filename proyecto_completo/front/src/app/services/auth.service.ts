// auth.service.ts
import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = environment.apiUrl; 
  private readonly tokenKey = 'access_token';
  user = signal<any | null>(null);

  constructor(private http: HttpClient) {

  }

  login(dto: { username: string; password: string }): Observable<any> {
    return this.http.post<any>(`${this.api}/login/`, dto).pipe(
      tap((res) => {
        localStorage.setItem(this.tokenKey, res.token);
        this.user.set(res.user);
      })
    );
  }

  logout(): Observable<any> {
    const token = localStorage.getItem(this.tokenKey);
    const headers = new HttpHeaders().set('Authorization', `Token ${token}`);
    
    return this.http.post(`${this.api}/logout/`, {}, { headers }).pipe(
      tap(() => {
        localStorage.removeItem(this.tokenKey);
        this.user.set(null);
      })
    );
  }

  getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem(this.tokenKey);
    return new HttpHeaders().set('Authorization', `Token ${token}`);
  }

  estaLogueado(): boolean {
    return !!localStorage.getItem(this.tokenKey);
  }
}