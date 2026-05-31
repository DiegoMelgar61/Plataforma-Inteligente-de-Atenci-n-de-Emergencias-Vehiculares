import { Component, signal, HostListener, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './sidebar.component';
import { NavbarComponent } from './navbar.component';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent, NavbarComponent],
  styles: [`
    .mobile-overlay {
      position: fixed; inset: 0; z-index: 30;
      background: rgba(26,22,37,0.32);
      backdrop-filter: blur(8px);
      animation: fadeIn 0.2s ease-out;
    }
  `],
  template: `
    <div class="flex h-screen overflow-hidden" style="background: var(--bg-base);">

      @if (isMobile() && !sidebarCollapsed()) {
        <div class="mobile-overlay" (click)="sidebarCollapsed.set(true)"></div>
      }

      <app-sidebar
        [collapsed]="sidebarCollapsed()"
        [isMobile]="isMobile()"
        (toggleSidebar)="sidebarCollapsed.set(!sidebarCollapsed())" />

      <div class="flex flex-col flex-1 min-w-0"
           style="transition: margin-left 0.25s ease;"
           [style.margin-left]="mainMarginLeft()">
        <app-navbar
          [isMobile]="isMobile()"
          (toggleSidebar)="sidebarCollapsed.set(!sidebarCollapsed())" />
        <main class="flex-1 overflow-y-auto p-4 pt-2 lg:p-8 lg:pt-4">
          <div class="max-w-7xl mx-auto fade-in">
            <router-outlet />
          </div>
        </main>
      </div>
    </div>
  `,
})
export class MainLayoutComponent implements OnInit {
  sidebarCollapsed = signal(false);
  isMobile = signal(false);

  ngOnInit(): void {
    this.checkViewport();
  }

  @HostListener('window:resize')
  checkViewport(): void {
    const mobile = window.innerWidth < 768;
    this.isMobile.set(mobile);
    if (mobile) {
      this.sidebarCollapsed.set(true);
    }
  }

  mainMarginLeft(): string {
    if (this.isMobile()) return '0px';
    return this.sidebarCollapsed() ? '80px' : '248px';
  }
}
