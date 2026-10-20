export interface User {
  id: string;
  iduser?: number;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'manager' | 'comercial_vendas';
  convitePendente?: boolean;
  avatarUrl?: string;
  active?: 'S' | 'N';
  createdAt?: string;
}
