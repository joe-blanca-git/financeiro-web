import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AtualizacaoHistoryItem } from '../../pages/previsao-caixa/previsao-caixa.mock';

export interface ImportacaoApbResult {
  sucesso: boolean;
  mensagem: string;
  idImportacoes: number;
  nomeArquivo: string;
  totalRegistros: number;
  totalValor: number;
}

export type ImportacaoAcrResult = ImportacaoApbResult;
export type ImportacaoTitulosLiquidadosResult = ImportacaoApbResult;

@Injectable({
  providedIn: 'root'
})
export class PrevisaoCaixaService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/previsao-caixa`;

  /**
   * Realiza o upload e processamento do arquivo APB no backend
   */
  importarApb(file: File): Observable<ImportacaoApbResult> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<ImportacaoApbResult>(`${this.apiUrl}/importar-apb`, formData);
  }

  /**
   * Realiza o upload e processamento do arquivo ACR no backend
   */
  importarAcr(file: File): Observable<ImportacaoAcrResult> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<ImportacaoAcrResult>(`${this.apiUrl}/importar-acr`, formData);
  }

  /**
   * Realiza o upload e processamento do arquivo de Títulos Liquidados no backend
   */
  importarTitulosLiquidados(file: File): Observable<ImportacaoTitulosLiquidadosResult> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<ImportacaoTitulosLiquidadosResult>(`${this.apiUrl}/importar-titulos-liquidados`, formData);
  }

  /**
   * Obtém o histórico de importações do tipo Previsão de Caixa / APB
   */
  listarImportacoes(tipo?: string): Observable<AtualizacaoHistoryItem[]> {
    let params = new HttpParams();
    if (tipo) {
      params = params.set('tipo', tipo);
    }
    return this.http.get<AtualizacaoHistoryItem[]>(`${this.apiUrl}/importacoes`, { params });
  }

  /**
   * Exclui uma importação e seus registros associados em cascata
   */
  excluirImportacao(idImportacoes: number): Observable<{ sucesso: boolean; mensagem: string }> {
    return this.http.delete<{ sucesso: boolean; mensagem: string }>(`${this.apiUrl}/importacoes/${idImportacoes}`);
  }
}
