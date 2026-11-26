# Política de Segurança

## Versões Suportadas

Atualmente, apenas a versão principal mais recente recebe atualizações de segurança e correções de bugs.

| Versão | Suportada          |
| :-----: | :----------------: |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

---

## Relatando uma Vulnerabilidade

A segurança dos dados fiscais e credenciais é de extrema importância para o projeto **TOTVS Cert Uploader**.

Se você descobrir uma vulnerabilidade de segurança, siga as diretrizes abaixo:

1. **Não abra uma Issue pública** para relatar problemas de segurança ou credenciais expostas.
2. Envie um e-mail diretamente com os detalhes técnicos para: **fausto.softbr@gmail.com**
3. Descreva detalhadamente o comportamento observado, passos para reproduzir e o impacto potencial.

### Diretrizes de Segurança do Repositório:
- O arquivo `.env` e quaisquer certificados digitais (`.pfx`, `.p12`, `.key`, `.cer`, `.pem`) **nunca** devem ser commitados no repositório.
- O hook de segurança pré-commit está disponível via [`instalar_hook_seguranca.bat`](instalar_hook_seguranca.bat) para bloquear automaticamente o envio de arquivos sensíveis ou credenciais ao GitHub.
