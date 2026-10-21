import { Observable } from 'rxjs';
import { Signal } from '@angular/core';
import { AuthResponse, ConviteInfo, LoginCredentials, RegisterCredentials } from '../models/auth.model';
import { User } from '../models/user.model';

export abstract class IAuthService {
  abstract currentUser: Signal<User | null>;
  abstract isAuthenticated: Signal<boolean>;
  abstract getToken(): string | null;

  abstract login(credentials: LoginCredentials): Observable<AuthResponse>;
  abstract register(credentials: RegisterCredentials): Observable<void>;
  abstract logout(): Observable<void>;

  // Primeiro acesso pelo link do convite
  abstract consultarConvite(token: string): Observable<ConviteInfo>;
  abstract concluirConvite(token: string, senha: string): Observable<AuthResponse>;
}
