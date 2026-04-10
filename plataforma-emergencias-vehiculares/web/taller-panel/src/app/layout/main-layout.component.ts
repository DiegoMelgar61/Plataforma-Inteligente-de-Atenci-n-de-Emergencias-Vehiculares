import { Component, inject, computed } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './sidebar.component';
import { NavbarComponent } from './navbar.component';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent, NavbarComponent],
  template: `
    <div class="flex h-screen overflow-hidden" style="background: var(--bg-base);">
      <app-sidebar />
      <div class="flex flex-col flex-1 min-w-0 transition-all duration-250"
           style="margin-left: 240px;">
        <app-navbar />
        <main class="flex-1 overflow-y-auto p-6 lg:p-8">
          <div class="max-w-7xl mx-auto fade-in">
            <router-outlet />
          </div>
        </main>
      </div>
    </div>
  `,
})
export class MainLayoutComponent {}
