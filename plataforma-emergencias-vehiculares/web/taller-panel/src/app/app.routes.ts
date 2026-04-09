import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { LoginComponent } from './features/auth/login.component';
import { MainLayoutComponent } from './layout/main-layout.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { RequestsListComponent } from './features/requests/requests-list.component';
import { RequestDetailComponent } from './features/requests/request-detail.component';
import { AssignmentsComponent } from './features/assignments/assignments.component';
import { TechniciansComponent } from './features/technicians/technicians.component';
import { MapComponent } from './features/map/map.component';
import { HistoryComponent } from './features/history/history.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'requests', component: RequestsListComponent },
      { path: 'requests/:id', component: RequestDetailComponent },
      { path: 'assignments', component: AssignmentsComponent },
      { path: 'technicians', component: TechniciansComponent },
      { path: 'map', component: MapComponent },
      { path: 'history', component: HistoryComponent },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
