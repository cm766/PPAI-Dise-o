import { Routes } from '@angular/router';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../app/services/auth.service';


const authGuard = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.estaLogueado()) {
    return true;
  }

  return router.parseUrl('/login');
};

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'login', 
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login').then((m) => m.LoginPage),
  },
  {
    path: 'home',
    canActivate: [authGuard], // 3. Usamos el nuevo guard funcional aquí
    loadComponent: () => import('./pages/home/home').then((m) => m.HomePage),
  },
  {
    path: 'seguimiento',
    canActivate: [authGuard], // 3. Y también aquí
    loadComponent: () =>
      import('./pages/pantalla-buscar-bolsin/pantalla-buscar-bolsin')
        .then((m) => m.PantallaBuscarBolsin),
  },
];