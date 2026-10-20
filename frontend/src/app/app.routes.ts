import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { noAuthGuard } from './core/guards/no-auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/auth/login/login.component').then(m => m.LoginComponent),
    canActivate: [noAuthGuard]
  },
  {
    path: 'cadastro',
    loadComponent: () => import('./pages/auth/register/register.component').then(m => m.RegisterComponent),
    canActivate: [noAuthGuard]
  },
  {
    // Primeiro acesso pelo link do convite (público: o token do link é a autorização)
    path: 'primeiro-acesso',
    loadComponent: () => import('./pages/auth/primeiro-acesso/primeiro-acesso.component').then(m => m.PrimeiroAcessoComponent)
  },
  {
    path: 'compartilhar/inadimplencia',
    loadComponent: () => import('./pages/inadimplencia-publica/inadimplencia-publica.component').then(m => m.InadimplenciaPublicaComponent)
  },
  {
    path: 'compartilhar/logistica',
    loadComponent: () => import('./pages/inadimplencia-publica/inadimplencia-publica.component').then(m => m.InadimplenciaPublicaComponent)
  },
  {
    path: 'compartilhar/comercial',
    loadComponent: () => import('./pages/inadimplencia-publica/inadimplencia-publica.component').then(m => m.InadimplenciaPublicaComponent)
  },
  {
    path: 'compartilhar/pendencias-acr',
    loadComponent: () => import('./pages/inadimplencia-publica/inadimplencia-publica.component').then(m => m.InadimplenciaPublicaComponent)
  },
  {
    path: '',
    loadComponent: () => import('./layout/main-layout/main-layout.component').then(m => m.MainLayoutComponent),
    canActivate: [authGuard],
    // Também em cada navegação entre páginas internas (o nível Comercial - Vendas só vê a carteira)
    canActivateChild: [authGuard],
    children: [
      {
        path: '',
        loadChildren: () => import('./pages/pages.routes').then(m => m.pagesRoutes)
      }
    ]
  }
];
