# Recarga Premium — Site Oficial

> **PROJECT SOURCE OF TRUTH**
>
> Este documento registra o contexto aprovado do projeto. Antes de mudanças significativas, inspecione a implementação existente. Preserve funcionalidades, identidade visual e conteúdo aprovado. O código funcional é a fonte técnica de verdade.

## 1. Produto

Site institucional e comercial da **Recarga Premium**, empresa de soluções em eletromobilidade e implantação de eletropostos.

## 2. Objetivo de negócio

Gerar autoridade, apresentar soluções, captar leads e apoiar o processo comercial de projetos de carregamento para condomínios, estabelecimentos e outros locais com demanda por infraestrutura para veículos elétricos.

## 3. Posicionamento

A comunicação deve transmitir experiência técnica, segurança, profissionalismo e capacidade de execução. O negócio trabalha com soluções de carregamento e projetos que podem envolver engenharia elétrica, obras civis e arquitetura conforme necessidade.

## 4. Branding

Usar sempre o logotipo oficial aprovado da Recarga Premium:

- símbolo verde de carro elétrico com plugue à esquerda;
- texto **RECARGA PREMIUM**;
- subtítulo **SOLUÇÕES EM ELETROMOBILIDADE**.

Não redesenhar, substituir ou aproximar o logo sem solicitação explícita.

## 5. Direção do site

- Visual corporativo, tecnológico e moderno.
- Responsivo para desktop, tablet e mobile.
- Hierarquia clara de serviços, benefícios e CTA.
- WhatsApp como canal comercial quando configurado.
- Navegação simples e objetiva.
- Evitar excesso de seções institucionais ou informação duplicada.

## 6. Conteúdo e conversão

Priorizar:

- proposta de valor clara;
- soluções de carregamento;
- benefícios para o local/cliente;
- processo de implantação quando aplicável;
- CTA para contato/proposta;
- credibilidade técnica sem inventar números, clientes ou certificações.

## 7. Arquitetura técnica

Site estático de página única, sem framework nem backend:

- `index.html` (HTML, CSS e JS inline), `hero-eletroposto.webp`, `logo-recarga-premium.webp`;
- `robots.txt` e `sitemap.xml` para SEO;
- hospedagem em **S3 + CloudFront**, publicação automática via GitHub Actions + AWS OIDC (ver [docs/deploy-aws.md](docs/deploy-aws.md));
- `scripts/validate.py` valida âncoras, arquivos locais, `alt` das imagens, JSON-LD e sitemap; roda em PRs/branches (`ci.yml`) e antes de cada deploy;
- formulário de contato monta a mensagem no navegador e abre o WhatsApp (sem servidor); CEP via ViaCEP;
- GA4 e Meta Pixel estão **desativados** de propósito (coerência com o texto de LGPD); ver `LEIA-ME.txt`.

## 8. Segurança

- Nunca expor secrets, tokens ou credenciais no frontend.
- Usar variáveis de ambiente quando aplicável.
- Formulários devem validar entrada e tratar erros.
- Não publicar dados privados de leads.

## 9. Restrições críticas

**DO NOT:**

- alterar o logo oficial sem aprovação;
- inventar clientes, números ou resultados;
- adicionar serviços não aprovados;
- criar dependências ou backend sem necessidade;
- redesenhar áreas aprovadas sem solicitação;
- quebrar responsividade ou CTA comercial.

## 10. Status atual

Site implementado e publicado. Pendências conhecidas:

- fotos reais dos projetos na seção de aplicações (hoje cenários ilustrativos);
- aplicar a Response Headers Policy de segurança no CloudFront (`docs/cloudfront-security-headers.json`);
- decidir sobre analytics/pixel (exige atualizar o texto de LGPD e banner de consentimento).

---

**Princípio de desenvolvimento:** `PATCH > REWRITE` · `REUSE > RECREATE` · `SIMPLE > COMPLEX` · `WORKING CODE > UNNECESSARY REFACTOR`
