import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class LoginPage {
  private auth = inject(AuthService);
  private router = inject(Router);

  username = '';
  password = '';
  error = '';
  loading = signal(false);

  async submit(): Promise<void> {
    this.error = '';
    this.loading.set(true);
    try {
      console.log('Enviando credenciales...');
      const res = await firstValueFrom(this.auth.login({ username: this.username, password: this.password }));
      
      console.log('Login exitoso, datos guardados. Intentando redirección...', res);
      
      // Forzamos la navegación y evaluamos si Angular la rechaza (por ejemplo, por un Guard)
      const navegacionExitosa = await this.router.navigate(['/home']);
      if (!navegacionExitosa) {
        console.warn('La redirección fue rechazada. ¿Tienes un AuthGuard bloqueando /home?');
      }
    } catch (err: any) {
      console.error('Error capturado en el login:', err);
      this.error = err.error?.message || 'Error al iniciar sesión';
    } finally {
      this.loading.set(false);
    }
  }
}