import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { IAuthService } from '../interfaces/auth.service';

// Página única do nível Comercial - Vendas
export const ROTA_CARTEIRA = '/minha-carteira';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(IAuthService);
  const router = inject(Router);

  // Verifica se há token e se a sessão está ativa
  if (!(authService.isAuthenticated() && authService.getToken())) {
    // Redireciona para o login guardando URL de retorno
    return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
  }

  // Comercial - Vendas só acessa a própria carteira; os demais níveis não acessam essa página.
  // (A API aplica a mesma regra: isto só evita telas que não carregariam.)
  const comercial = authService.currentUser()?.role === 'comercial_vendas';
  const naCarteira = state.url === ROTA_CARTEIRA || state.url.startsWith(ROTA_CARTEIRA + '?');
  if (comercial && !naCarteira) {
    return router.createUrlTree([ROTA_CARTEIRA]);
  }
  if (!comercial && naCarteira) {
    return router.createUrlTree(['/home']);
  }
  return true;
};
