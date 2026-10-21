import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ComercialService, MinhaCarteira, CarteiraTitulo } from '../../core/services/comercial.service';
import { MensagemThreadApi } from '../../core/services/importacoes.service';
import { ModalComponent } from '../../shared/components/modal/modal.component';
import { ButtonComponent } from '../../shared/components/button/button.component';
import { SkeletonComponent } from '../../shared/components/skeleton/skeleton.component';
import { AvatarComponent } from '../../shared/components/avatar/avatar.component';

interface MensagemChat {
  id: number;
  autor: string;
  iniciais: string;
  minhaMensagem: boolean;
  data: Date;
  assunto: string;
  corpo: string;
  anexos: string[];
}

@Component({
  selector: 'app-minha-carteira',
  standalone: true,
  imports: [CommonModule, FormsModule, ModalComponent, ButtonComponent, SkeletonComponent, AvatarComponent],
  templateUrl: './minha-carteira.component.html',
  styleUrl: './minha-carteira.component.scss'
})
export class MinhaCarteiraComponent implements OnInit {
  private comercialService = inject(ComercialService);

  carteira: MinhaCarteira | null = null;
  carregando = true;
  erro = '';

  idRepresentante: number | null = null;
  busca = '';
  pagina = 1;
  readonly porPagina = 10;

  ngOnInit() {
    this.carregar();
  }

  carregar() {
    this.carregando = true;
    this.erro = '';
    // O gerente vem do login (a API usa o token); aqui só escolhe um representante da própria equipe
    this.comercialService.minhaCarteira(this.idRepresentante).subscribe({
      next: (dados) => {
        this.carteira = dados;
        this.carregando = false;
        this.pagina = 1;
      },
      error: (err) => {
        this.carregando = false;
        this.carteira = null;
        this.erro = err?.error?.detail || 'Não foi possível carregar a sua carteira.';
      }
    });
  }

  onRepresentanteChange() {
    this.carregar();
  }

  get titulosFiltrados(): CarteiraTitulo[] {
    const termo = this.busca.trim().toLowerCase();
    const titulos = this.carteira?.titulos || [];
    if (!termo) return titulos;
    return titulos.filter(t =>
      t.titulo.toLowerCase().includes(termo) ||
      (t.cliente || '').toLowerCase().includes(termo) ||
      (t.representante || '').toLowerCase().includes(termo)
    );
  }

  get titulosPagina(): CarteiraTitulo[] {
    const inicio = (this.pagina - 1) * this.porPagina;
    return this.titulosFiltrados.slice(inicio, inicio + this.porPagina);
  }

  get totalPaginas(): number {
    return Math.max(1, Math.ceil(this.titulosFiltrados.length / this.porPagina));
  }

  // Mesmas cores de status da grade do painel
  corStatus(status: string): string {
    const mapa: Record<string, string> = {
      'ATRASADO': 'warning',
      'PROTESTADO': 'danger',
      'PRORROGADO': 'info',
      'OK': 'success',
      'ACORDO': 'primary',
      'DEVOLUCAO': 'warning',
      'SEM DATA DE ENTREGA': 'warning',
    };
    return mapa[status] || 'secondary';
  }

  getBadgeClass(fase: string | null | undefined): string {
    if (!fase) return 'bg-light text-secondary border border-secondary-subtle';
    const f = fase.toUpperCase();
    if (f === 'ACORDO') return 'bg-success bg-opacity-10 text-success border border-success-subtle';
    if (f === 'PROTESTADO' || f === 'DEVOLUCAO' || f === 'ATRASADO') return 'bg-danger bg-opacity-10 text-danger border border-danger-subtle';
    if (f === 'SEM DATA DE ENTREGA') return 'bg-warning bg-opacity-10 text-warning border border-warning-subtle';
    return 'bg-primary bg-opacity-10 text-primary border border-primary-subtle';
  }

  // ================= Modal Tratativas =================
  isTratativasModalOpen = false;
  tituloTratativas: CarteiraTitulo | null = null;
  tratativas: { data: Date; autor: string; conteudo: string }[] = [];
  isLoadingTratativas = false;

  abrirTratativas(t: CarteiraTitulo) {
    this.tituloTratativas = t;
    this.tratativas = [];
    this.isTratativasModalOpen = true;
    this.isLoadingTratativas = true;
    this.comercialService.tratativasTitulo(t.id).subscribe({
      next: (itens) => {
        this.tratativas = itens.map((x: any) => ({
          data: x.createdAt ? new Date(x.createdAt) : new Date(),
          autor: x.autor || 'Usuário',
          conteudo: x.conteudo
        }));
        this.isLoadingTratativas = false;
      },
      error: () => this.isLoadingTratativas = false
    });
  }

  fecharTratativas() {
    this.isTratativasModalOpen = false;
    this.tituloTratativas = null;
  }

  // ================= Modal Mensagens =================
  isMensagensModalOpen = false;
  tituloMensagens: CarteiraTitulo | null = null;
  mensagens: MensagemChat[] = [];
  isLoadingMensagens = false;

  abrirMensagens(t: CarteiraTitulo) {
    this.tituloMensagens = t;
    this.mensagens = [];
    this.isMensagensModalOpen = true;
    this.isLoadingMensagens = true;
    this.comercialService.mensagensTitulo(t.id).subscribe({
      next: (itens) => {
        this.mensagens = itens.map(m => this.mapearMensagem(m));
        this.isLoadingMensagens = false;
      },
      error: () => this.isLoadingMensagens = false
    });
  }

  fecharMensagens() {
    this.isMensagensModalOpen = false;
    this.tituloMensagens = null;
    this.mensagens = [];
  }

  private mapearMensagem(m: MensagemThreadApi): MensagemChat {
    const autor = this.extrairNomeEmail(m.de);
    return {
      id: m.internal_date,
      autor,
      iniciais: this.obterIniciais(autor),
      minhaMensagem: m.minha_mensagem,
      data: new Date(m.internal_date * 1000),
      assunto: m.assunto,
      corpo: m.corpo_html || m.corpo_texto.replace(/\n/g, '<br>'),
      anexos: m.anexos ? m.anexos.map((a: any) => a.nome) : []
    };
  }

  private extrairNomeEmail(de: string): string {
    if (!de) return 'Desconhecido';
    const match = de.match(/^(.*?)\s*</);
    if (match && match[1]) return match[1].replace(/["']/g, '').trim();
    return de.trim();
  }

  private obterIniciais(nome: string): string {
    if (!nome) return '?';
    const partes = nome.split(' ').filter(p => p.length > 0);
    if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase();
    return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
  }

  // ================= Modal Histórico =================
  isHistoricoModalOpen = false;
  tituloHistorico: CarteiraTitulo | null = null;
  historico: { data: Date; tipo: string; observacao: string; icone: string; cor: string }[] = [];
  isLoadingHistorico = false;

  abrirHistorico(t: CarteiraTitulo) {
    this.tituloHistorico = t;
    this.historico = [];
    this.isLoadingHistorico = true;
    this.isHistoricoModalOpen = true;
    this.comercialService.historicoTitulo(t.id).subscribe({
      next: (itens) => {
        this.historico = (itens || []).map((h: any) => {
          const { icone, cor } = this.iconeCorPorTipo(h.tipo);
          return {
            data: h.createdAt ? new Date(h.createdAt) : new Date(),
            tipo: h.tipo || 'Evento',
            observacao: h.observacao || '',
            icone,
            cor
          };
        });
        this.isLoadingHistorico = false;
      },
      error: () => this.isLoadingHistorico = false
    });
  }

  fecharHistorico() {
    this.isHistoricoModalOpen = false;
    this.tituloHistorico = null;
  }

  private iconeCorPorTipo(tipo: string | null): { icone: string; cor: string } {
    const t = (tipo || '').toLowerCase();
    if (t.includes('finaliza') || t.includes('resolu')) return { icone: 'fa-solid fa-check-circle', cor: 'success' };
    if (t.includes('email') || t.includes('e-mail') || t.includes('mensagem')) return { icone: 'fa-solid fa-envelope', cor: 'primary' };
    if (t.includes('prorrogad')) return { icone: 'fa-regular fa-calendar-plus', cor: 'warning' };
    if (t.includes('importada')) return { icone: 'fa-solid fa-file-circle-plus', cor: 'primary' };
    if (t.includes('fase') || t.includes('classifica')) return { icone: 'fa-solid fa-shuffle', cor: 'info' };
    if (t.includes('status')) return { icone: 'fa-solid fa-flag', cor: 'warning' };
    if (t.includes('tratativa')) return { icone: 'fa-solid fa-headset', cor: 'success' };
    return { icone: 'fa-solid fa-circle-info', cor: 'secondary' };
  }
}
