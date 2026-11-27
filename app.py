"""
Aplicativo Desktop para Atualização de Certificado Digital - Softbr (v1.4.0).
Interface gráfica nativa intuitiva em CustomTkinter com execução automatizada do pipeline em segundo plano.
"""

import re
import sys
import threading
import tkinter.messagebox as msgbox
import traceback
from datetime import datetime
from tkinter import filedialog
from typing import Optional

import customtkinter as ctk

from cert_manager import CertificateInfo, format_cnpj, format_subject_dn_totvs_order, install_certificate_in_windows, read_pfx_certificate
from db_service import DatabaseError, DatabaseService
from logger_service import LoggerService
from reboot_service import reiniciar_computador_windows
from totvs_chef_web import TotvsChefWebStoreUnavailable, TotvsChefWebUploader
from totvs_tec import TotvsTecConfigurationError, TotvsTecError, TotvsTecUploader

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_VERSION = "1.4.0"


class CertUploaderApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"Atualizador de Certificado Digital - Softbr v{APP_VERSION}")
        self.geometry("860x680")
        self.minsize(780, 600)

        self.cert_info: Optional[CertificateInfo] = None
        self.is_running: bool = False
        self.logger = LoggerService(gui_callback=self._append_log)
        self._install_global_exception_handlers()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_cert_card()
        self._build_details_card()
        self._build_status_and_actions()

    def _install_global_exception_handlers(self) -> None:
        def _handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.log(f"[FATAL UNHANDLED ERROR] {exc_value}\n{tb_str}")
            try:
                self.logger.dispatch_email("Crash da Aplicação")
            except Exception:
                pass
            self._set_banner(f"Erro Fatal: {exc_value}", "error")

        sys.excepthook = _handle_exception
        if hasattr(threading, "excepthook"):
            def _thread_hook(args):
                _handle_exception(args.exc_type, args.exc_value, args.exc_traceback)
            threading.excepthook = _thread_hook

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(16, 6), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text=f"Atualizador de Certificado Digital Softbr (v{APP_VERSION})",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Selecione o arquivo do certificado (.pfx ou .p12), informe a senha e clique em 'INICIAR ATUALIZAÇÃO'.",
            font=ctk.CTkFont(size=13),
            text_color="#A0AEC0",
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

    def _build_cert_card(self) -> None:
        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        section_lbl = ctk.CTkLabel(
            card,
            text="1. Arquivo e Senha do Certificado Digital",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        section_lbl.grid(row=0, column=0, columnspan=4, padx=16, pady=(12, 8), sticky="w")

        ctk.CTkLabel(card, text="Arquivo (.pfx/.p12):").grid(row=1, column=0, padx=(16, 8), pady=6, sticky="w")
        self.file_entry = ctk.CTkEntry(card, placeholder_text="Clique em 'Selecionar Arquivo...' para localizar o certificado")
        self.file_entry.grid(row=1, column=1, columnspan=2, padx=4, pady=6, sticky="ew")

        self.browse_btn = ctk.CTkButton(card, text="Selecionar Arquivo...", width=160, command=self._on_browse_file)
        self.browse_btn.grid(row=1, column=3, padx=(8, 16), pady=6)

        ctk.CTkLabel(card, text="Senha do Certificado:").grid(row=2, column=0, padx=(16, 8), pady=(6, 14), sticky="w")
        self.cert_pwd_entry = ctk.CTkEntry(card, placeholder_text="Digite a senha do certificado digital...", show="•")
        self.cert_pwd_entry.grid(row=2, column=1, padx=4, pady=(6, 14), sticky="ew")
        self.cert_pwd_entry.bind("<Return>", lambda _e: self._validate_certificate())
        self.cert_pwd_entry.bind("<FocusOut>", lambda _e: self._auto_validate_if_ready())

        self.show_pwd_var = ctk.BooleanVar(value=False)
        self.show_pwd_cb = ctk.CTkCheckBox(
            card,
            text="Mostrar senha",
            variable=self.show_pwd_var,
            command=self._toggle_cert_password,
            width=110,
        )
        self.show_pwd_cb.grid(row=2, column=2, padx=8, pady=(6, 14))

        self.validate_btn = ctk.CTkButton(
            card,
            text="Validar Certificado",
            width=160,
            fg_color="#2B6CB0",
            hover_color="#2C5282",
            command=self._validate_certificate,
        )
        self.validate_btn.grid(row=2, column=3, padx=(8, 16), pady=(6, 14))

    def _build_details_card(self) -> None:
        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(3, weight=1)

        section_lbl = ctk.CTkLabel(
            card,
            text="2. Dados Identificados no Certificado",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        section_lbl.grid(row=0, column=0, columnspan=4, padx=16, pady=(12, 8), sticky="w")

        ctk.CTkLabel(card, text="Razão Social:").grid(row=1, column=0, padx=(16, 8), pady=4, sticky="w")
        self.razao_lbl = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(weight="bold"), anchor="w")
        self.razao_lbl.grid(row=1, column=1, columnspan=3, padx=4, pady=4, sticky="ew")

        ctk.CTkLabel(card, text="CNPJ da Empresa:").grid(row=2, column=0, padx=(16, 8), pady=4, sticky="w")
        self.cnpj_entry = ctk.CTkEntry(card, placeholder_text="00.000.000/0000-00", state="disabled")
        self.cnpj_entry.grid(row=2, column=1, padx=4, pady=4, sticky="ew")

        ctk.CTkLabel(card, text="Validade:").grid(row=2, column=2, padx=(16, 8), pady=4, sticky="w")
        self.validade_lbl = ctk.CTkLabel(card, text="—", anchor="w")
        self.validade_lbl.grid(row=2, column=3, padx=(4, 16), pady=4, sticky="ew")

    def _build_status_and_actions(self) -> None:
        container = ctk.CTkFrame(self, corner_radius=10)
        container.grid(row=3, column=0, padx=20, pady=(8, 16), sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(3, weight=1)

        # Banner de Aviso de Sucesso / Erro no painel
        self.status_banner = ctk.CTkFrame(container, corner_radius=8, fg_color="#2D3748")
        self.status_banner.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")
        self.status_banner.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_banner,
            text="Status: Aguardando seleção e validação do certificado digital.",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#E2E8F0",
            wraplength=760,
            justify="left",
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, padx=14, pady=10, sticky="ew")

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(container, mode="determinate", height=10)
        self.progress_bar.grid(row=1, column=0, padx=16, pady=(2, 6), sticky="ew")
        self.progress_bar.set(0)

        # Botão principal de Envio
        self.start_btn = ctk.CTkButton(
            container,
            text="INICIAR ATUALIZAÇÃO DO CERTIFICADO",
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2F855A",
            hover_color="#276749",
            command=self._on_start_process,
        )
        self.start_btn.grid(row=2, column=0, padx=16, pady=6, sticky="ew")

        # Histórico de progresso
        self.log_box = ctk.CTkTextbox(container, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.grid(row=3, column=0, padx=16, pady=(6, 14), sticky="nsew")
        self.log_box.configure(state="disabled")
        self._append_log("Pronto. Selecione o arquivo .pfx ou .p12 e informe a senha.")

    def _toggle_cert_password(self) -> None:
        self.cert_pwd_entry.configure(show="" if self.show_pwd_var.get() else "•")

    def _set_cnpj_value(self, value: str) -> None:
        self.cnpj_entry.configure(state="normal")
        self.cnpj_entry.delete(0, "end")
        self.cnpj_entry.insert(0, value)
        self.cnpj_entry.configure(state="disabled")

    def _append_log(self, formatted_line: str) -> None:
        def _update() -> None:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", formatted_line + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        self.after(0, _update)

    def _set_banner(self, text: str, level: str = "info") -> None:
        colors = {
            "info": ("#2D3748", "#E2E8F0"),
            "working": ("#2B6CB0", "#FFFFFF"),
            "success": ("#22543D", "#C6F6D5"),
            "warning": ("#744210", "#FEFCBF"),
            "error": ("#742A2A", "#FED7D7"),
        }
        bg, fg = colors.get(level, colors["info"])

        def _update() -> None:
            self.status_banner.configure(fg_color=bg)
            self.status_label.configure(text=text, text_color=fg)

        self.after(0, _update)

    def _set_progress(self, val: float) -> None:
        self.after(0, lambda: self.progress_bar.set(val))

    def _on_browse_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Selecionar Certificado Digital",
            filetypes=[("Certificado Digital PKCS#12", "*.pfx *.p12"), ("Todos os arquivos", "*.*")],
        )
        if file_path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)
            self.logger.log("Arquivo de certificado selecionado.")
            self._auto_validate_if_ready()

    def _auto_validate_if_ready(self) -> None:
        if self.file_entry.get().strip() and self.cert_pwd_entry.get():
            self._validate_certificate()

    def _validate_certificate(self) -> bool:
        file_path = self.file_entry.get().strip()
        cert_pwd = self.cert_pwd_entry.get()

        if not file_path:
            self._set_banner("Atenção: Selecione o arquivo .pfx ou .p12 do certificado.", "warning")
            return False
        if not cert_pwd:
            self._set_banner("Atenção: Digite a senha do certificado digital.", "warning")
            return False

        try:
            info = read_pfx_certificate(file_path, cert_pwd)
            self.cert_info = info
            self.razao_lbl.configure(text=info.razao_social)

            if info.cnpj_formatado:
                self._set_cnpj_value(info.cnpj_formatado)

            val_str = f"{info.valido_ate.strftime('%d/%m/%Y')} ({info.dias_restantes} dias restantes)"
            if info.expirado:
                self.validade_lbl.configure(text=f"EXPIRADO em {info.valido_ate.strftime('%d/%m/%Y')}", text_color="#FC8181")
                self._set_banner(
                    f"Atenção: O certificado de '{info.razao_social}' está EXPIRADO ({info.valido_ate.strftime('%d/%m/%Y')})!",
                    "error",
                )
            else:
                color = "#68D391" if info.dias_restantes > 30 else "#F6E05E"
                self.validade_lbl.configure(text=val_str, text_color=color)
                self._set_banner(
                    f"Certificado validado: {info.razao_social} | CNPJ: {info.cnpj_formatado or 'Não identificado'}",
                    "success",
                )

            self.logger.log(
                f"Certificado validado: {info.razao_social} | CNPJ: {info.cnpj_formatado} | Válido até: {info.valido_ate.strftime('%d/%m/%Y')}"
            )
            return True
        except Exception as exc:
            self.cert_info = None
            self.razao_lbl.configure(text="—")
            self.validade_lbl.configure(text="—", text_color="#E2E8F0")
            self._set_banner(f"Erro na validação do certificado: {exc}", "error")
            self.logger.log(f"Erro ao validar certificado: {exc}")
            return False

    def _on_start_process(self) -> None:
        if self.is_running:
            return

        if not self._validate_certificate():
            self.logger.log("[INÍCIO ABORTADO] Certificado digital não validado com sucesso.")
            self.logger.dispatch_email("Falha na Validação do Certificado")
            return

        self.is_running = True
        self.start_btn.configure(state="disabled", text="ATUALIZANDO CERTIFICADOS EM SEGUNDO PLANO... AGUARDE")
        self._set_progress(0.05)

        thread = threading.Thread(target=self._worker_pipeline, daemon=True)
        thread.start()

    def _worker_pipeline(self) -> None:
        cert = self.cert_info
        if not cert:
            self.is_running = False
            return

        cert_path = cert.file_path
        cert_pwd = self.cert_pwd_entry.get()
        cnpj = format_cnpj(cert.cnpj_numeros or cert.cnpj_formatado)
        empresa_identificador = cnpj or cert.razao_social
        loja = None
        usa_nfe = None
        resultados = {}

        def registrar(destino: str, estado: str, detalhe: str) -> None:
            resultados[destino] = estado
            self.logger.log(f"[{destino}] {estado}. {detalhe}")

        try:
            self._set_banner("Passo 2/5: Instalando certificado no Windows...", "working")
            try:
                ok, detalhe = install_certificate_in_windows(cert_path, cert_pwd)
                registrar("Windows", "Atualizado" if ok else "Falha", detalhe)
            except Exception:
                registrar("Windows", "Falha", traceback.format_exc())
            self._set_progress(0.20)

            self._set_banner("Passo 3/5: Atualizando o banco local...", "working")
            db_service = None
            try:
                db_service = DatabaseService()
                loja = db_service.buscar_loja_por_cnpj(cnpj)
                empresa_identificador = f"{loja.nome_loja} ({loja.cnpj})"
                subject_dn = format_subject_dn_totvs_order(cert.subject_dn)
                db_service.atualizar_certificado_loja(loja.codigo_loja, subject_dn)
                registrar("Banco local", "Atualizado", empresa_identificador)
            except DatabaseError as exc:
                registrar("Banco local", "Falha", str(exc))
            except Exception:
                registrar("Banco local", "Falha", traceback.format_exc())
            finally:
                if db_service is not None:
                    try:
                        if loja is not None:
                            usa_nfe = db_service.verificar_licenca_nfe()
                    except Exception:
                        self.logger.log(f"[TPF] Falha ao verificar atividade de NF-e. {traceback.format_exc()}")
                    finally:
                        db_service.close()
            self._set_progress(0.40)

            self._set_banner("Passo 4/5: Enviando certificado ao Portal TEC...", "working")
            if re.fullmatch(r"[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}", cnpj):
                try:
                    tec = TotvsTecUploader(log_callback=self.logger.log, headless=False)
                    detalhe = tec.run(cnpj_formatado=cnpj, cert_path=cert_path, cert_password=cert_pwd)
                    registrar("Portal TEC", "Atualizado", detalhe)
                except TotvsTecConfigurationError as exc:
                    registrar("Portal TEC", "Pendente", str(exc))
                except TotvsTecError as exc:
                    registrar("Portal TEC", "Falha", str(exc))
                except Exception:
                    registrar("Portal TEC", "Falha", traceback.format_exc())
            else:
                registrar("Portal TEC", "Pendente", "CNPJ do certificado indisponível ou inválido.")
            self._set_progress(0.65)

            self._set_banner("Passo 5/5: Verificando loja no Chef Web Cloud...", "working")
            nome_loja = (loja.nome_loja or "").strip() if loja is not None else ""
            if nome_loja:
                try:
                    chef = TotvsChefWebUploader(log_callback=self.logger.log, headless=False)
                    detalhe = chef.run(nome_loja=nome_loja, cert_path=cert_path, cert_password=cert_pwd)
                    registrar("Chef Web Cloud", "Envio sem confirmação", detalhe)
                except TotvsChefWebStoreUnavailable as exc:
                    registrar("Chef Web Cloud", "Pendente", str(exc))
                except Exception:
                    registrar("Chef Web Cloud", "Falha", traceback.format_exc())
            else:
                registrar("Chef Web Cloud", "Pendente", "Nome fantasia indisponível no banco local.")

            if usa_nfe:
                aviso_tpf = "Atividade recente de NF-e detectada. Atualize o certificado manualmente na TPF."
            else:
                aviso_tpf = "Se a loja utiliza NF-e, verifique a atualização manual do certificado na TPF."
            aviso_tpf += "\nhttps://plataformafiscal.totvs.com.br/estabelecimento"
            self.logger.log(f"[TPF] {aviso_tpf}")

            resumo = "\n".join(f"{destino} · {estado}" for destino, estado in resultados.items())
            self._set_banner("Execução finalizada. Confira o resultado de cada etapa.", "info")
            self._set_progress(1.0)
            try:
                self.logger.dispatch_email(empresa_identificador)
            except Exception:
                self.logger.log(f"[LOGS] Falha no envio do relatório. {traceback.format_exc()}")
            self.after(500, lambda: self._prompt_reboot(resumo, aviso_tpf))
        finally:
            self.is_running = False
            self.after(0, lambda: self.start_btn.configure(state="normal", text="INICIAR ATUALIZAÇÃO DO CERTIFICADO"))

    def _prompt_reboot(self, resumo: str, aviso_tpf: str) -> None:
        """Exibe o resultado e pergunta se o operador deseja reiniciar o computador."""
        resposta = msgbox.askyesno(
            "Resultado da atualização",
            f"{resumo}\n\n{aviso_tpf}\n\nDeseja reiniciar o computador agora?",
        )
        if resposta:
            self.logger.log("[REINICIALIZAÇÃO] Reinicialização autorizada pelo cliente. Reiniciando Windows em 5 segundos...")
            ok, msg = reiniciar_computador_windows(delay_segundos=5)
            self.logger.log(f"[REINICIALIZAÇÃO] {msg}")
        else:
            self.logger.log("[REINICIALIZAÇÃO] Cliente optou por reiniciar mais tarde. Concluído sem reiniciar.")


if __name__ == "__main__":
    app = CertUploaderApp()
    app.mainloop()
