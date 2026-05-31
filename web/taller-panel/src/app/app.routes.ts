import { Routes } from '@angular/router';
import { authGuard, adminGuard } from './core/guards/auth.guard';
import { LoginComponent } from './features/auth/login.component';
import { MainLayoutComponent } from './layout/main-layout.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { RequestsListComponent } from './features/requests/requests-list.component';
import { RequestDetailComponent } from './features/requests/request-detail.component';
import { AssignmentsComponent } from './features/assignments/assignments.component';
import { TechniciansComponent } from './features/technicians/technicians.component';
import { MapComponent } from './features/map/map.component';
import { HistoryComponent } from './features/history/history.component';
import { AdminUsersComponent } from './features/admin/admin-users.component';
import { AdminWorkshopsComponent } from './features/admin/admin-workshops.component';
import { PaymentsListComponent } from './features/payments/payments-list.component';
import { TenantsComponent } from './features/tenants/tenants.component';

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
      { path: 'payments', component: PaymentsListComponent },
      { path: 'history', component: HistoryComponent },
      { path: 'tenants', component: TenantsComponent },
      {
        path: 'admin',
        canActivate: [adminGuard],
        children: [
          { path: 'users', component: AdminUsersComponent },
          { path: 'workshops', component: AdminWorkshopsComponent },
          { path: '', redirectTo: 'users', pathMatch: 'full' },
        ],
      },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
