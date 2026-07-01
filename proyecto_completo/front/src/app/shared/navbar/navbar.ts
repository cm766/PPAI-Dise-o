import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" routerLink="/">Gestión de Bolsines</a>
        <div class="navbar-nav ms-auto">
          <a class="nav-link" routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Inicio</a>
          <a class="nav-link" routerLink="/seguimiento" routerLinkActive="active">Seguimiento</a>
        </div>
      </div>
    </nav>
  `,
})
export class Navbar {}
