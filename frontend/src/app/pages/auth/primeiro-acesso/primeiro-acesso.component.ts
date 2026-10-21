import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { IAuthService } from '../../../core/interfaces/auth.service';
import { ButtonComponent } from '../../../shared/components/button/button.component';
import { isAmbienteTeste } from '../../../core/config/ambiente';

@Component({
  selector: 'app-primeiro-acesso',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonComponent],
  templateUrl: './primeiro-acesso.component.html',
  styleUrls: ['../login/login.component.scss', './primeiro-acesso.component.scss']
})
export class PrimeiroAcessoComponent implements OnInit {
  private authService = inject(IAuthService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  readonly isAmbienteTeste = isAmbienteTeste;

  token = '';
  carregando = true;
  linkInvalido = '';
  nome = '';
  email = '';

  senha = '';
  confirmacao = '';
  mostrarSenha = false;
  salvando = false;
  erro = '';

  ngOnInit() {
    this.token = this.route.snapshot.queryParams['token'] || '';
    if (!this.token) {
      this.carregando = false;
      this.linkInvalido = 'Link de primeiro acesso incompleto. Abra o link exatamente como recebido no e-mail.';
      return;
    }
    this.authService.consultarConvite(this.token).subscribe({
      next: (info) => {
        this.nome = info.name;
        this.email = info.email;
        this.carregando = false;
      },
      error: (err) => {
        this.carregando = false;
        this.linkInvalido = err?.error?.detail
          || 'Este link de primeiro acesso é inválido ou expirou. Solicite um novo convite ao departamento de T.I.';
      }
    });
  }

  // Regras exibidas em tempo real (a API valida as mesmas)
  get regras() {
    return [
      { texto: 'Pelo menos 8 caracteres', ok: this.senha.length >= 8 },
      { texto: 'Um número', ok: /\d/.test(this.senha) },
      { texto: 'Uma letra maiúscula', ok: /[A-Z]/.test(this.senha) },
      { texto: 'Um caractere especial (ex.: ! @ # $ %)', ok: /[^A-Za-z0-9]/.test(this.senha) },
    ];
  }

  get senhaValida(): boolean {
    return this.regras.every(r => r.ok);
  }

  get confirmacaoConfere(): boolean {
    return this.confirmacao.length > 0 && this.confirmacao === this.senha;
  }

  salvar() {
    if (!this.senhaValida || !this.confirmacaoConfere || this.salvando) return;
    this.salvando = true;
    this.erro = '';
    this.authService.concluirConvite(this.token, this.senha).subscribe({
      next: () => {
        this.salvando = false;
        // A home redireciona para a única página que o nível do usuário acessa
        this.router.navigateByUrl('/home');
      },
      error: (err) => {
        this.salvando = false;
        this.erro = err?.error?.detail || 'Não foi possível criar a senha. Tente novamente.';
      }
    });
  }
}
