import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './sidebar.component';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent],
  template: `
    <div class="flex min-h-screen bg-gray-50">
      <app-sidebar />
      <main class="flex-1 ml-64 p-8 overflow-y-auto">
        <router-outlet />
      </main>
    </div>
  `,
})
export class MainLayoutComponent {}
