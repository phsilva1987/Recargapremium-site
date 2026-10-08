# Publicação automática — Recarga Premium

Este projeto é um site estático hospedado no **S3** e distribuído via **CloudFront**. O workflow `.github/workflows/deploy-s3-cloudfront.yml` faz upload apenas dos cinco arquivos de produção (`index.html`, `robots.txt`, `sitemap.xml` e as duas imagens) e solicita a invalidação do cache. Não usa `s3 sync --delete`, não envia README, nem remove arquivos adicionais existentes no bucket.

## 1. Criar provedor OIDC (uma vez, caso não exista)

AWS IAM → Identity providers → Add provider → OpenID Connect:
- Provider URL: `https://token.actions.githubusercontent.com`
- Audience: `sts.amazonaws.com`

## 2. Criar role para o GitHub Actions

No IAM, crie uma role com Web identity para o GitHub Actions, com a trust policy específica para esta conta (arquivo [aws-oidc-trust-policy.json](./aws-oidc-trust-policy.json)):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::316356488279:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:phsilva1987/Recargapremium-site:environment:production"
        }
      }
    }
  ]
}
```

**Atenção:** como o workflow usa o GitHub Environment `production`, o subject OIDC se refere ao **environment**, não à branch. Em Settings → Environments → production, configure **Deployment branches: Selected branches → main**. Recomenda-se também aprovação obrigatória para produção, se a modalidade do GitHub oferecer essa proteção. Não reutilize essa role para outros repositórios.

## 3. Permissões mínimas de publicação

Anexe à role esta policy de menor privilégio (arquivo [aws-deploy-permissions.json](./aws-deploy-permissions.json)):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "UploadSiteFiles",
      "Effect": "Allow",
      "Action": ["s3:PutObject"],
      "Resource": [
        "arn:aws:s3:::recargapremium-site/index.html",
        "arn:aws:s3:::recargapremium-site/robots.txt",
        "arn:aws:s3:::recargapremium-site/sitemap.xml",
        "arn:aws:s3:::recargapremium-site/hero-eletroposto.webp",
        "arn:aws:s3:::recargapremium-site/logo-recarga-premium.webp"
      ]
    },
    {
      "Sid": "InvalidateCloudFront",
      "Effect": "Allow",
      "Action": ["cloudfront:CreateInvalidation"],
      "Resource": "arn:aws:cloudfront::316356488279:distribution/E14L95QZL3U5IN"
    }
  ]
}
```

Se houver política adicional no bucket (KMS ou controles específicos), as permissões poderão precisar de adequação.

## 4. Configurar GitHub

No repositório, abra **Settings → Environments → New environment** e crie `production`. Restrinja deployments à branch `main`.

Em **Settings → Secrets and variables → Actions → Variables** (ou environment variables de production), configure:

| Nome | Valor |
| --- | --- |
| `AWS_ROLE_ARN` | ARN da role criada, ex.: `arn:aws:iam::316356488279:role/RecargaPremiumGithubDeploy` |
| `AWS_REGION` | `us-east-1` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `E14L95QZL3U5IN` |

O nome do bucket está fixado no workflow como `recargapremium-site`. Não são necessárias AWS Access Keys em Secrets.

**Nunca** salve Access Key ID, Secret Access Key ou credenciais AWS no repositório.

## Dados confirmados do projeto

- AWS Account ID: `316356488279`
- S3 Bucket: `recargapremium-site`
- Região S3: `us-east-1`
- CloudFront Distribution ID: `E14L95QZL3U5IN`
- Role proposta: `RecargaPremiumGithubDeploy`

> Os identificadores foram informados pelo proprietário. Ainda é necessário confirmar que o bucket e a distribuição pertencem à conta e estão associados ao domínio correto na AWS.

## Configuração via AWS CLI (alternativa ao Console)

Execute os comandos abaixo **somente com um perfil AWS administrativo autorizado**, após revisar os dois arquivos JSON e configurar o provedor OIDC na conta. Baixe o repositório localmente antes da execução.

```bash
aws sts get-caller-identity
aws iam get-open-id-connect-provider --open-id-connect-provider-arn arn:aws:iam::316356488279:oidc-provider/token.actions.githubusercontent.com
aws iam create-role --role-name RecargaPremiumGithubDeploy --assume-role-policy-document file://docs/aws-oidc-trust-policy.json
aws iam put-role-policy --role-name RecargaPremiumGithubDeploy --policy-name RecargaPremiumWebsiteDeploy --policy-document file://docs/aws-deploy-permissions.json
aws iam get-role --role-name RecargaPremiumGithubDeploy --query 'Role.Arn' --output text
```

Se o OIDC provider não existir, crie-o no Console. Se a role já existir, não execute `create-role`; revise a configuração existente. Os comandos acima **criam IAM**, mas não publicam conteúdo no S3 nem invalidam o CloudFront.

## 5. Teste e operação

1. Depois de configurar a AWS/GitHub, faça merge do PR que adiciona o workflow.
2. Abra **Actions → Publicar site Recarga Premium (S3 + CloudFront)** → Run workflow para testar. Se faltarem variables, o job falhará **antes** de autenticar ou alterar a AWS.
3. Verifique S3, invalidação no CloudFront e a página publicada.
4. Depois disso, alterações em `index.html` ou imagens na branch `main` acionam deploy automaticamente. Alterações em PRs/branches de teste **não** publicam.
5. O workflow solicita a invalidação; a propagação do cache no CloudFront é assíncrona.
6. Para rollback, reverta o commit ou restaure uma versão conhecida do `index.html` na `main` e rode novamente o workflow.

**Cuidado:** o primeiro deploy depois de ativado substituirá o `index.html` no S3 pela versão da `main`. Não faça merge até confirmar o Environment, a role e o fluxo de homologação.

## 6. Headers de segurança no CloudFront

O arquivo [cloudfront-security-headers.json](./cloudfront-security-headers.json) define uma Response Headers Policy (HSTS, nosniff, referrer, frame, CSP e Permissions-Policy). Aplicação (perfil administrativo, uma única vez):

```bash
aws cloudfront create-response-headers-policy --response-headers-policy-config file://docs/cloudfront-security-headers.json
aws cloudfront get-distribution-config --id E14L95QZL3U5IN > dist.json   # anote o ETag
# edite DefaultCacheBehavior.ResponseHeadersPolicyId em dist.json com o Id criado e então:
aws cloudfront update-distribution --id E14L95QZL3U5IN --if-match <ETag> --distribution-config file://dist-config.json
```

Teste a CSP no navegador (console sem violações) antes de manter em produção. A CSP usa `'unsafe-inline'` porque o site tem CSS/JS inline.
