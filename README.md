# TOTVS Cert Uploader (NFe / NFCe)

[![Release](https://img.shields.io/github/v/release/faustosoftbr/Totvs_cert_uploader?color=blue&label=Vers%C3%A3o%20Atual)](https://github.com/faustosoftbr/Totvs_cert_uploader/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Plataforma-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Tests](https://img.shields.io/badge/Testes-8%2F8%20Aprovados-success)](#execução-de-testes)
[![License: MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](LICENSE)

Aplicativo Desktop em Python (`CustomTkinter` + `Playwright` + `cryptography` + `pyodbc`) para leitura, validação local, atualização no banco SQL Server local (MISTERCHEFNET), envio aos portais TOTVS (Portal TEC e Chef Web Cloud), instalação no repositório de certificados do Windows e telemetria de logs via Webhook.

---

## Por que um aplicativo executável e não um site na nuvem?

Por regras de segurança (*sandbox* e políticas de segurança dos navegadores modernos), uma página web remota (hospedada em `https://seusite.com.br`) não consegue:

- **Conectar via TCP na porta 1433 do `localhost`** para consultar e atualizar o banco de dados SQL Server local (`localhost\SQLEXPRESS`).
- **Acessar credenciais salvas e sessões de cookies** do navegador padrão do cliente para plataformas fiscais locais.
- **Chamar comandos do sistema operacional** (como `powershell` / `certutil`) para instalar o certificado digital diretamente no repositório de certificados do Windows (`Cert:\CurrentUser\My`) com a chave privada marcada como exportável.

### A Solução Executável:
Em vez de depender de um site remoto limitado, o cliente recebe um executável único e seguro (`TOTVS-Cert-Uploader.exe`). Ele executa com permissões normais de usuário do Windows, acessa a base local do Totvs Chef, realiza as automações necessárias de ponta a ponta e entrega uma interface visual moderna, simples e intuitiva para usuários leigos.

---

## Versões Disponíveis

| Versão | Descrição |
| :--- | :--- |
| **`v1.0.0`** | Versão inicial com campos manuais de login e senha do Portal TEC. |
| **`v1.2.0`** | Versão para cliente final com credenciais embutidas e upload exclusivo no Portal TEC. |
| **`v1.3.0`** | Versão inicial do pipeline integrado com upload automático TEC, Chef Web e TPF. |
| **`v1.4.0`** | **Pipeline Otimizado & Seleção Dinâmica por CNPJ**: <br>1. Validação local do PFX (CNPJ, Razão Social, Validade e Subject DN).<br>2. Instalação prévia do certificado no repositório do Windows (`Cert:\CurrentUser\My`) com chave privada exportável.<br>3. Localização dinâmica da Loja no SQL Server local por correspondência exata do CNPJ do certificado e atualização de `[NomeCertificado]`.<br>4. Upload no Portal TEC (Totvs Hospitalidade) utilizando o CNPJ da loja selecionada.<br>5. Upload no Chef Web Cloud (localizando a loja pelo Nome Fantasia da loja selecionada).<br>6. Lembrete com link direto no log para atualização manual na Plataforma Fiscal TPF (caso utilize módulo NFe).<br>7. Solicitação opcional de reinicialização do Windows.<br>8. Telemetria e envio de logs por e-mail via Google Apps Script Webhook. |

---

## Arquitetura e Módulos do Sistema

- `app.py`: Interface gráfica CustomTkinter e orquestração do pipeline em thread desacoplada.
- `cert_manager.py`: Extração e validação de certificados PKCS#12 e rotinas de instalação no Windows Store.
- `db_service.py`: Camada de comunicação com o SQL Server local (localização dinâmica de lojas por CNPJ e detecção de NFe).
- `totvs_tec.py`: Automação Playwright em segundo plano para o Portal TEC.
- `totvs_chef_web.py`: Automação Playwright para o Chef Web Cloud.
- `logger_service.py`: Log em tempo real, persistência em arquivo e despacho via Webhook.
- `secrets_manager.py`: Gerenciamento seguro de credenciais locais via `.env` (ignorado pelo Git) e CLI interativa para consulta/alteração.
- `gas_webhook.js`: Script do Google Apps Script para disparo seguro de e-mails via GmailApp.

---

---

## Execução de Testes

O projeto possui uma bateria de testes automatizados com cobertura completa das regras críticas de negócio:

```bash
python test_suite.py
```

Itens validados pelos testes:
1. Persistência e leitura segura de variáveis de ambiente (`.env`).
2. Resolução correta de diretório em executáveis PyInstaller (`sys.frozen`).
3. Leitura, decodificação PKCS#12 e formatação do Subject DN para o padrão Totvs Chef.
4. Formatação e persistência de telemetria local e arquivo de emergência (`LOG_ERRO_ATUALIZACAO.txt`).
5. Busca dinâmica de lojas por correspondência exata de CNPJ.
6. Tratamento de exceção de banco de dados offline.

---

## Segurança e Vulnerabilidades

Consulte a nossa [Política de Segurança](SECURITY.md) para orientações sobre como relatar vulnerabilidades ou contribuir com a integridade do projeto.
