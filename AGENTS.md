# AGENTS.md — Recarga Premium (site)

Site institucional e comercial da **Recarga Premium** (soluções em eletromobilidade e eletropostos para condomínios, estabelecimentos e outros locais). Objetivo: autoridade técnica e captação de leads por WhatsApp. Fonte da verdade: `README.md`, `LEIA-ME.txt` e `docs/deploy-aws.md`. **Repositório público e site em produção** (`www.recargapremium.com`).

## Stack
Site estático de página única. Sem framework, build, backend ou dependências.

- `index.html` — HTML, CSS e JS inline
- `logo-recarga-premium.webp`, `hero-eletroposto.webp`, `img/*.webp` — hospedadas no próprio bucket (a CSP não permite imagem externa)
- `robots.txt`, `sitemap.xml`; `scripts/validate.py` — validação sem dependências
- Formulário: monta a mensagem no navegador e abre o WhatsApp (sem servidor); CEP via ViaCEP

## Comandos
- `python3 scripts/validate.py` — confere âncoras, arquivos locais, `alt` das imagens, JSON-LD e sitemap. Rodar antes de concluir qualquer mudança.
- Servir local: `python3 -m http.server 8080`.

## Deploy e produção
- CI (`ci.yml`): roda `validate.py` em PRs e em branches diferentes de `main`.
- Deploy (`deploy-s3-cloudfront.yml`): em push na `main` **só se mudar** `index.html`, `logo-recarga-premium.webp`, `hero-eletroposto.webp`, `robots.txt`, `sitemap.xml`, `img/**`, `scripts/validate.py` ou o próprio workflow; também manual. Usa o Environment `production` (pode haver aprovação pendente no GitHub), roda a validação, autentica por OIDC e envia só esses arquivos (sem `--delete`) e invalida o CloudFront.
- Este arquivo e `docs/` não são publicados e não disparam deploy.
- Limites do deploy: o workflow envia apenas `img/*.webp`, e a policy IAM (`docs/aws-deploy-permissions.json`) só permite esses caminhos. **Imagem nova deve ser `.webp` dentro de `img/`**; arquivo novo na raiz ou em outro formato não será publicado sem ajustar workflow e IAM (precisa de OK).

## Aprovação e merge
- Merge só com OK do PH, exceto "tarefa pequena" no `index.html`: texto/CSS ou bug isolado, ≤50 linhas, com a validação verde. Nesse caso faça o merge e informe como reverter (`git revert`).
- OK explícito para qualquer mudança em workflow, `docs/aws-*.json`, IAM, CloudFront ou bucket.

## Regras do site
- **Logo oficial:** símbolo verde de carro elétrico com plugue à esquerda, texto "RECARGA PREMIUM" e subtítulo "SOLUÇÕES EM ELETROMOBILIDADE". Não redesenhar, substituir ou aproximar sem pedido.
- Não inventar clientes, números, resultados, certificações ou serviços não aprovados. A seção de projetos usa placeholders até haver fotos reais; trocar só com fotos reais fornecidas pelo PH.
- **GA4 e Meta Pixel estão desativados de propósito** (comentados no `<head>`), por coerência com o texto de LGPD (`#privacidade`). Para ativar: IDs reais, remover comentários, atualizar o texto de Cookies e incluir consentimento. A CSP em `docs/cloudfront-security-headers.json` hoje só permite `script-src 'self' 'unsafe-inline'` e `connect-src 'self' https://viacep.com.br`, então analytics exigiria revisar a CSP também.
- Domínio canônico: `https://www.recargapremium.com/` (canonical, `og:url`, `og:image`, `robots.txt`, `sitemap.xml`). O `LEIA-ME.txt` cita `recargapremium.com` sem `www` e está desatualizado nesse ponto. Mudou o domínio: atualizar todos esses lugares.
- Instagram: `@recargapremiumoficial` (rodapé e `sameAs` do JSON-LD; atualizar os dois).
- Não criar backend ou dependência sem necessidade; não quebrar responsividade nem o CTA comercial.

## UI
- Tokens em `:root` do `index.html`: `--green #079b3a`, `--green-2 #20c64d`, `--green-dark #005b2b`, `--green-deep #003b24`, `--ink #0b1720`, `--soft #f4f7f5`, `--line #dce6df`. Reutilizar.
- Breakpoints em uso: 1050, 820, 560 px. Validar em 360, 768 e 1280 px, sem overflow; Esc fecha o menu mobile (preservar).
- Visual corporativo, tecnológico e moderno; menu enxuto (Soluções, Projetos, Carregadores, Contato).

## Pendências conhecidas (do README)
Fotos reais de projetos · aplicar a Response Headers Policy de segurança no CloudFront · decidir sobre analytics/pixel.

## Nunca
- Colocar secret, token ou dado de lead no repositório (ele é público).
- Criar V2/New/Final ou arquivos paralelos, nem refatorar o que funciona sem motivo.
