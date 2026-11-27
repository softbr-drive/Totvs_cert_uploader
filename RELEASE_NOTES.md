# TOTVS Cert Uploader v1.4.0

- O Portal TEC usa o CNPJ pontuado do certificado e continua quando o banco local falha.
- O Chef Web Cloud continua após falha do TEC quando encontra uma única loja com o nome fantasia exato.
- O resumo apresenta o resultado de cada destino e oferece a reinicialização ao final.
- Na versão de testes, os navegadores ficam visíveis durante a automação.
- O GitHub Actions compila o executável para Windows e disponibiliza o resultado como artefato.

## Histórico

### 🚀 TOTVS Cert Uploader - Versão 4.0.0

Lançamento oficial da versão **v4.0.0** do **TOTVS Cert Uploader**, trazendo a nova arquitetura de pipeline otimizado, instalação prévia no repositório de certificados do Windows e localização dinâmica de lojas por correspondência exata de CNPJ no SQL Server local.

---

### 📦 Principais Novidades e Funcionalidades da v4.0.0:

1. **Nova Ordem de Pipeline Otimizada**:
   * **Instalação Antecipada no Windows Store (Passo 2)**: O certificado digital agora é instalado no repositório pessoal do Windows (`Cert:\CurrentUser\My`) com chave privada marcada como exportável (`-Exportable`) logo após a validação inicial do arquivo PFX. Isso assegura que o sistema operacional e os serviços fiscais locais já tenham o certificado ativo antes de qualquer sincronização externa.

2. **Seleção e Localização Dinâmica de Loja por CNPJ (Passo 3)**:
   * Não fixa mais na "Loja 1". O aplicativo agora pesquisa e compara os dígitos do CNPJ extraído do certificado com todas as lojas cadastradas na tabela `[MISTERCHEFNET].[dbo].[Lojas]`.
   * Seleciona dinamicamente a filial correspondente e atualiza o campo `[NomeCertificado]` com a string canônica do Subject DN no padrão Totvs Chef.
   * Utiliza o **Nome Fantasia** e **CNPJ** da loja identificada em todos os passos subsequentes.

3. **Automação no Portal TEC / Totvs Hospitalidade (Passo 4)**:
   * Upload automatizado do certificado digital via Playwright em segundo plano utilizando as credenciais seguras do `.env` e o CNPJ da loja selecionada.

4. **Automação no Chef Web Cloud (Passo 5)**:
   * Localização automática da filial pelo Nome Fantasia da loja identificada e upload nas configurações de recepção fiscal da retaguarda em nuvem.

5. **Lembrete Fiscal Manual para a Plataforma Fiscal TPF**:
   * Emissão inteligente de alerta com link direto no log e na tela de finalização para que lojas com emissão ativa de NF-e atualizem manualmente no portal da Plataforma Fiscal TOTVS (TPF).

6. **Telemetria de Logs e Notificações**:
   * Registro detalhado em tempo real e despacho de auditoria por e-mail via Webhook seguro do Google Apps Script (`gas_webhook.js`).

7. **Blindagem de Segurança e Variáveis de Ambiente**:
   * Arquitetura desacoplada via `.env` local (protegido contra commits pelo `.gitignore`).
   * Utilitário CLI interativo para manutenção de credenciais mascaradas (`secrets_manager.py`).
   * Hook de pré-commit ativo impedindo vazamento acidental de chaves, senhas ou arquivos `.pfx`.

8. **Resiliência de Telemetria e Logs de Emergência**:
   * Suporte nativo ao executável Windows (`sys.frozen`) para leitura automática do `.env` na pasta do `.exe`.
   * Gravação redundante do relatório completo em arquivo local de emergência (`LOG_ERRO_ATUALIZACAO.txt`).
   * Captura técnica de traceback detalhado de banco e automação para diagnóstico ágil.

---

### 💻 Executável Incluso:
* **`TOTVS-Cert-Uploader.exe`**: Executável único compilado nativamente para Windows 64-bit, pronto para uso do cliente final sem necessidade de instalar Python ou dependências adicionais.
