import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="bg-dark text-light py-4 mt-5">
      <div class="container text-center">
        <small>© 2026 Gestión de Bolsines</small>
      </div>
    </footer>
  `,
})
export class Footer {}
