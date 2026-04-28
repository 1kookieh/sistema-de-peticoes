"""Interface desktop local para geração supervisionada de petições.

A interface usa Tkinter, disponível na biblioteca padrão, para manter o
projeto simples e sem dependências de UI. Ela não substitui a revisão humana:
apenas aciona o mesmo pipeline validado usado pela CLI e pela API.
"""
from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from uuid import uuid4

from config import OUTPUT_DIR, REPORTS_DIR
from src.adapters.inbox.gmail_reader import Email
from src.orchestration.pipeline import processar_email
from src.core.profiles import get_profile, list_profile_ids
from src.orchestration.reporting import build_run_report, write_html_report, write_json_report
from src.orchestration.setup import setup_runtime


class DesktopApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema de Petições")
        self.geometry("900x680")
        self.minsize(760, 560)
        self._build_ui()
        setup_runtime()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=16)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Perfil de validação").grid(row=0, column=0, sticky="w")
        self.profile_var = tk.StringVar(value="judicial-inicial-jef")
        self.profile = ttk.Combobox(
            header,
            textvariable=self.profile_var,
            values=list(list_profile_ids()),
            state="readonly",
        )
        self.profile.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ttk.Label(header, text="Modo").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.output_mode_var = tk.StringVar(value="minuta")
        self.output_mode = ttk.Combobox(
            header,
            textvariable=self.output_mode_var,
            values=("minuta", "final", "triagem"),
            state="readonly",
        )
        self.output_mode.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))

        body = ttk.Frame(self, padding=(16, 0, 16, 16))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        warning = (
            "Uso supervisionado: o documento gerado exige revisão jurídica humana, "
            "conferência de dados, assinatura, OAB, anexos e regras locais de protocolo."
        )
        ttk.Label(body, text=warning, wraplength=820).grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.text = tk.Text(body, wrap="word", undo=True, height=18)
        self.text.grid(row=1, column=0, sticky="nsew")

        actions = ttk.Frame(body)
        actions.grid(row=2, column=0, sticky="ew", pady=12)
        ttk.Button(actions, text="Carregar .txt", command=self._load_txt).pack(side="left")
        ttk.Button(actions, text="Limpar", command=self._clear).pack(side="left", padx=8)
        self.generate_button = ttk.Button(actions, text="Gerar e validar .docx", command=self._generate)
        self.generate_button.pack(side="right")

        self.status_var = tk.StringVar(value="Pronto.")
        ttk.Label(body, textvariable=self.status_var).grid(row=3, column=0, sticky="ew")

        self.result = tk.Text(body, wrap="word", height=8, state="disabled")
        self.result.grid(row=4, column=0, sticky="ew", pady=(8, 0))

    def _load_txt(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecionar texto da petição",
            filetypes=(("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")),
        )
        if not path:
            return
        try:
            content = Path(path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = Path(path).read_text(encoding="latin-1")
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)

    def _clear(self) -> None:
        self.text.delete("1.0", tk.END)
        self._set_result("")
        self.status_var.set("Pronto.")

    def _set_result(self, value: str) -> None:
        self.result.configure(state="normal")
        self.result.delete("1.0", tk.END)
        self.result.insert("1.0", value)
        self.result.configure(state="disabled")

    def _generate(self) -> None:
        texto = self.text.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Texto obrigatório", "Cole ou carregue o texto da peça antes de gerar.")
            return
        self.generate_button.configure(state="disabled")
        self.status_var.set("Gerando e validando...")
        threading.Thread(target=self._generate_worker, args=(texto,), daemon=True).start()

    def _generate_worker(self, texto: str) -> None:
        try:
            profile = get_profile(self.profile_var.get())
            token = uuid4().hex[:12]
            email = Email(
                thread_id=f"desktop-{token}",
                message_id=f"desktop-{token}",
                remetente="desktop@example.com",
                assunto="Geração desktop local",
                peticao_texto=texto,
            )
            result = processar_email(
                email,
                profile_id=profile.id,
                no_outbox=True,
                output_mode=self.output_mode_var.get(),
            )
            summary = {
                "total": 1,
                "enfileirados": 0,
                "bloqueados": 1 if result.problemas else 0,
                "falhas": 0,
                "violacoes": len(result.problemas),
                "ignorados": 0,
                "validos": 1 if result.status == "ok_no_outbox" else 0,
            }
            report = build_run_report(
                profile=profile,
                strict=True,
                no_outbox=True,
                summary=summary,
                items=[result.to_report_item()],
            )
            report_base = REPORTS_DIR / f"desktop_{token}"
            write_json_report(report_base.with_suffix(".json"), report)
            write_html_report(report_base.with_suffix(".html"), report)

            lines = [f"Status: {result.status}"]
            if result.destino:
                lines.append(f"Documento: {OUTPUT_DIR / result.destino.name}")
            lines.append(f"Relatório JSON: {report_base.with_suffix('.json')}")
            lines.append(f"Relatório HTML: {report_base.with_suffix('.html')}")
            if result.problemas:
                lines.append("")
                lines.append("Problemas formais encontrados:")
                lines.extend(f"- {problem}" for problem in result.problemas)
            self.after(0, self._finish_generation, "\n".join(lines), "Concluído.")
        except Exception as exc:
            self.after(0, self._finish_generation, f"Falha: {exc}", "Falha na geração.")

    def _finish_generation(self, result_text: str, status: str) -> None:
        self._set_result(result_text)
        self.status_var.set(status)
        self.generate_button.configure(state="normal")


def main() -> None:
    app = DesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()


