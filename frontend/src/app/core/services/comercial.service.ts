import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PaginatedResponse } from './colaboradores.service';
import { MensagemThreadApi } from './importacoes.service';

export interface Gerente {
  idGerente: number;
  codigo: number;
  nome: string;
  obs?: string | null;
  qtdRepresentantes: number;
  idUser?: number | null;
  usuarioEmail?: string | null;
}

export interface Representante {
  idRepresentante: number;
  codigo: number;
  nome: string;
  obs?: string | null;
  idGerente?: number | null;
  gerenteNome?: string | null;
  qtdClientes: number;
}

export interface CarteiraTitulo {
  id: number;
  titulo: string;
  cliente: string;
  representante: string;
  vencimento: string | null;
  diasAtraso: number | null;
  status: string;
  fase: string;
  qtd: number;
  valor: number;
}

export interface MinhaCarteira {
  gerente: { idGerente: number; nome: string };
  representantes: { idRepresentante: number; nome: string }[];
  idRepresentante: number | null;
  dataPosicao: string;
  totalVencido: number;
  totalProtestado: number;
  qtdTitulos: number;
  titulos: CarteiraTitulo[];
}

@Injectable({
  providedIn: 'root'
})
export class ComercialService {
  private apiUrl = `${environment.apiUrl}/comercial`;

  constructor(private http: HttpClient) { }

  listarGerentes(page = 1, pageSize = 10, search = ''): Observable<PaginatedResponse<Gerente>> {
    return this.http.get<PaginatedResponse<Gerente>>(`${this.apiUrl}/gerentes`, { params: this.params(page, pageSize, search) });
  }

  listarRepresentantes(page = 1, pageSize = 10, search = ''): Observable<PaginatedResponse<Representante>> {
    return this.http.get<PaginatedResponse<Representante>>(`${this.apiUrl}/representantes`, { params: this.params(page, pageSize, search) });
  }

  // Carteira do gerente vinculado ao usuário logado (a API identifica o usuário pelo token)
  minhaCarteira(idRepresentante?: number | null): Observable<MinhaCarteira> {
    let params = new HttpParams();
    if (idRepresentante) params = params.set('id_representante', idRepresentante);
    return this.http.get<MinhaCarteira>(`${this.apiUrl}/minha-carteira`, { params });
  }

  // Detalhes do título da própria carteira (a API confere se o título é da carteira do usuário)
  tratativasTitulo(idNf: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/minha-carteira/titulos/${idNf}/tratativas`);
  }

  historicoTitulo(idNf: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/minha-carteira/titulos/${idNf}/historico`);
  }

  mensagensTitulo(idNf: number): Observable<MensagemThreadApi[]> {
    return this.http.get<MensagemThreadApi[]>(`${this.apiUrl}/minha-carteira/titulos/${idNf}/mensagens`);
  }

  emailUsuarioGerente(idGerente: number): Observable<{ email: string | null }> {
    return this.http.get<{ email: string | null }>(`${this.apiUrl}/gerentes/${idGerente}/usuario`);
  }

  vincularUsuario(idGerente: number, email: string): Observable<{ idUser: number; usuarioEmail: string; aviso: string | null }> {
    return this.http.put<{ idUser: number; usuarioEmail: string; aviso: string | null }>(`${this.apiUrl}/gerentes/${idGerente}/usuario`, { email });
  }

  desvincularUsuario(idGerente: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/gerentes/${idGerente}/usuario`);
  }

  private params(page: number, pageSize: number, search: string): HttpParams {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search) params = params.set('search', search);
    return params;
  }
}
