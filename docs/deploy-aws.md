# Publicação automática — Recarga Premium

Este projeto é um site estático hospedado no **S3** e distribuído via **CloudFront**. O workflow `.github/workflows/deploy-s3-cloudfront.yml` faz upload apenas dos três arquivos de produção e solicita a invalidação do cache. Não usa `s3 sync --delete`, não envia README, nem remove arquivos adicionais existentes no bucket.

## 1. Criar provedor OIDC (uma vez, caso não exista)

AWS IAM → Identity providers → Add provider → OpenID Connect:
- Provider URL: `https://token.actions.githubusercontent.com`
- Audience: `sts.amazonaws.com`

## 2. Criar role para o GitHub Actions

No IAM, crie uma role com Web identity para o GitHub Actions, com trust policy semelhante à seguinte (substitua **ACCOUNT_ID**):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
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

Anexe à role esta policy, substituindo **ACCOUNT_ID** e **DISTRIBUTION_ID**:

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
        "arn:aws:s3:::recargapremium-site/hero-eletroposto.webp",
        "arn:aws:s3:::recargapremium-site/logo-recarga-premium.webp"
      ]
    },
    {
      "Sid": "InvalidateCloudFront",
      "Effect": "Allow",
      "Action": ["cloudfront:CreateInvalidation"],
      "Resource": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
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
| `AWS_ROLE_ARN` | ARN da role criada, ex.: `arn:aws:iam::ACCOUNT_ID:role/RecargaPremiumGithubDeploy` |
| `AWS_REGION` | Região **real** do bucket S3 (ex.: `us-east-1`) |
| `CLOUDFRONT_DISTRIBUTION_ID` | ID **real** da distribuição do domínio recargapremium.com |

O nome do bucket está fixado no workflow como `recargapremium-site`. Não são necessárias AWS Access Keys em Secrets.

**Nunca** salve Access Key ID, Secret Access Key ou credenciais AWS no repositório.

## 5. Teste e operação

1. Depois de configurar a AWS/GitHub, faça merge do PR que adiciona o workflow.
2. Abra **Actions → Publicar site Recarga Premium (S3 + CloudFront)** → Run workflow para testar. Se faltarem variables, o job falhará **antes** de autenticar ou alterar a AWS.
3. Verifique S3, invalidação no CloudFront e a página publicada.
4. Depois disso, alterações em `index.html` ou imagens na branch `main` acionam deploy automaticamente. Alterações em PRs/branches de teste **não** publicam.
5. O workflow solicita a invalidação; a propagação do cache no CloudFront é assíncrona.
6. Para rollback, reverta o commit ou restaure uma versão conhecida do `index.html` na `main` e rode novamente o workflow.

**Cuidado:** o primeiro deploy depois de ativado substituirá o `index.html` no S3 pela versão da `main`. Não faça merge até confirmar o Environment, a role e o fluxo de homologação.
