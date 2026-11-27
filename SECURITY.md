# Política de Segurança

## Versões Suportadas

Atualmente, apenas a versão principal mais recente recebe atualizações de segurança e correções de bugs.

| Versão | Suportada          |
| :-----: | :----------------: |
| 1.4.x   | :white_check_mark: |
| Versões anteriores | :x:                |

---

## Relatando uma Vulnerabilidade

A segurança dos dados fiscais e credenciais é de extrema importância para o projeto **TOTVS Cert Uploader**.

Se você descobrir uma vulnerabilidade de segurança, siga as diretrizes abaixo:

1. **Não abra uma Issue pública** para relatar problemas de segurança ou credenciais expostas.
2. Envie um e-mail diretamente com os detalhes técnicos para: **fausto.softbr@gmail.com**
3. Descreva detalhadamente o comportamento observado, passos para reproduzir e o impacto potencial.

### Diretrizes de Segurança do Repositório:
- O arquivo `.env` e quaisquer certificados digitais (`.pfx`, `.p12`, `.key`, `.cer`, `.pem`) **nunca** devem ser commitados no repositório.
- O hook de segurança pré-commit está disponível via [`instalar_hook_seguranca.bat`](instalar_hook_seguranca.bat) para verificar arquivos preparados para commit e valores configurados no ambiente local. O hook é instalado por cópia ou pode ser usado com o diretório .githooks.

- Revogue ou troque imediatamente credenciais que tenham sido versionadas. Remover o valor do código atual preserva as cópias no histórico; coordene com os administradores qualquer limpeza de commits já publicados.
