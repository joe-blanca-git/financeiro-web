import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PaginatedResponse } from './colaboradores.service';

export interface Gerente {
  idGerente: number;
  codigo: number;
  nome: string;
  obs?: string | null;
  qtdRepresentantes: number;
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

  private params(page: number, pageSize: number, search: string): HttpParams {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search) params = params.set('search', search);
    return params;
  }
}
