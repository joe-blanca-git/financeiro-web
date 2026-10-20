import { User } from './user.model';

export interface AuthTokens {
  accessToken: string;
  expiresIn?: number;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export interface LoginCredentials {
  email: string;
  password?: string; // Optional if using magic link
}

export interface RegisterCredentials {
  name: string;
  email: string;
  password: string;
}

export interface ConviteInfo {
  name: string;
  email: string;
  regrasSenha: string;
}
