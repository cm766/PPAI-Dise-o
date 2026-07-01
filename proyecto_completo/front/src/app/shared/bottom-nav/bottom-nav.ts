import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-bottom-nav',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <nav class="navbar fixed-bottom navbar-light bg-light border-top">
      <div class="container justify-content-center">
        <a class="nav-link px-3" routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Inicio</a>
        <a class="nav-link px-3" routerLink="/seguimiento" routerLinkActive="active">Seguimiento</a>
      </div>
    </nav>
  `,
})
export class BottomNav {}
