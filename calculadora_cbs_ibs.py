import customtkinter as ctk
from tkinter import messagebox
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from dados_reforma import (
    NCM_LISTA,
    NBS_LISTA,
    CST_LISTA,
    CLASSIFICACOES_TRIBUTARIAS,
    MUNICIPIOS_LISTA,
    CRONOGRAMA_TRANSICAO,
)

# Configuração visual inspirada em aplicação web moderna
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

COR_FUNDO = "#F3F4F6"
COR_CARD = "#FFFFFF"
COR_BORDA = "#E5E7EB"
COR_PRIMARIA = "#1D4ED8"
COR_PRIMARIA_HOVER = "#1E40AF"
COR_TEXTO = "#111827"
COR_SUBTEXTO = "#4B5563"
COR_DESTAQUE_BG = "#EFF6FF"


def formatar_moeda(valor: Decimal) -> str:
    val = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_pct(valor: Decimal) -> str:
    val = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{val:.2f}%".replace(".", ",")


class ModalBusca(ctk.CTkToplevel):
    """Janela modal de busca dinâmica (NCM/NBS, Município ou Classificação Tributária)."""

    def __init__(self, parent, titulo, placeholder, itens, formatador_item, callback_selecao):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("620x460")
        self.configure(fg_color=COR_FUNDO)
        self.transient(parent)
        self.grab_set()

        self.itens = itens
        self.formatador_item = formatador_item
        self.callback_selecao = callback_selecao

        ctk.CTkLabel(
            self, text=titulo, font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ctk.CTkLabel(
            self, text=placeholder, font=("Segoe UI", 12), text_color=COR_SUBTEXTO
        ).pack(anchor="w", padx=20, pady=(0, 12))

        self.entry_busca = ctk.CTkEntry(
            self, placeholder_text="Digite para filtrar...", height=38, font=("Segoe UI", 13)
        )
        self.entry_busca.pack(fill="x", padx=20, pady=(0, 12))
        self.entry_busca.bind("<KeyRelease>", self.filtrar)
        self.entry_busca.focus()

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COR_CARD, border_width=1, border_color=COR_BORDA)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.renderizar_lista(self.itens)

    def filtrar(self, event=None):
        termo = self.entry_busca.get().strip().lower()
        if not termo:
            self.renderizar_lista(self.itens)
            return

        palavras = termo.split()
        filtrados = []
        for item in self.itens:
            texto_completo = self.formatador_item(item).lower()
            if all(p in texto_completo for p in palavras):
                filtrados.append(item)
        self.renderizar_lista(filtrados)

    def renderizar_lista(self, lista):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not lista:
            ctk.CTkLabel(
                self.scroll_frame, text="Nenhum resultado encontrado.", text_color=COR_SUBTEXTO, font=("Segoe UI", 12)
            ).pack(pady=20)
            return

        for item in lista:
            texto = self.formatador_item(item)
            btn = ctk.CTkButton(
                self.scroll_frame,
                text=texto,
                anchor="w",
                fg_color="transparent",
                text_color=COR_TEXTO,
                hover_color=COR_DESTAQUE_BG,
                font=("Segoe UI", 12),
                height=34,
                command=lambda i=item: self.selecionar(i),
            )
            btn.pack(fill="x", pady=2, padx=4)

    def selecionar(self, item):
        self.callback_selecao(item)
        self.destroy()


class ModalTextoInformativo(ctk.CTkToplevel):
    """Modal explicativo para Convivência entre Impostos, Crédito Tributário e Legislação."""

    def __init__(self, parent, titulo, conteudo):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("720x540")
        self.configure(fg_color=COR_CARD)
        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(
            self, text=titulo, font=("Segoe UI", 18, "bold"), text_color=COR_PRIMARIA
        ).pack(anchor="w", padx=24, pady=(20, 10))

        textbox = ctk.CTkTextbox(
            self, font=("Segoe UI", 13), text_color=COR_TEXTO, fg_color=COR_FUNDO, wrap="word", corner_radius=8
        )
        textbox.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        textbox.insert("1.0", conteudo)
        textbox.configure(state="disabled")

        ctk.CTkButton(
            self, text="Fechar", command=self.destroy, fg_color=COR_PRIMARIA, hover_color=COR_PRIMARIA_HOVER, width=120
        ).pack(pady=(0, 18))


class CalculadoraCBSIBSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora CBS / IBS — Reforma Tributária (EC 132/2023 & LC 214/2025)")
        self.geometry("1160x760")
        self.minsize(1040, 700)
        self.configure(fg_color=COR_FUNDO)

        self.tipo_operacao = "NCM"  # "NCM" ou "NBS"
        self.item_selecionado = None
        self.classificacao_atual = CLASSIFICACOES_TRIBUTARIAS[0]

        self._construir_cabecalho()
        self._construir_corpo_principal()
        self._construir_rodape()

        # Inicializa alíquotas pela data padrão
        self.atualizar_aliquotas_por_data()
        self.atualizar_combo_classificacao()

    def _construir_cabecalho(self):
        header = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=0, border_width=1, border_color=COR_BORDA)
        header.pack(fill="x")

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=14)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(
            left, text="Calculadora CBS / IBS", font=("Segoe UI", 22, "bold"), text_color=COR_TEXTO
        ).pack(anchor="w")
        ctk.CTkLabel(
            left,
            text="Simulador oficial baseado nas regras da Receita Federal, EC 132/2023 e LC 214/2025.",
            font=("Segoe UI", 12),
            text_color=COR_SUBTEXTO,
        ).pack(anchor="w")

        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")

        ctk.CTkButton(
            right,
            text="? Convivência (2026–2033)",
            fg_color=COR_DESTAQUE_BG,
            text_color=COR_PRIMARIA,
            hover_color="#DBEAFE",
            font=("Segoe UI", 12, "bold"),
            command=self.abrir_ajuda_transicao,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            right,
            text="? Como funciona o Crédito",
            fg_color=COR_DESTAQUE_BG,
            text_color=COR_PRIMARIA,
            hover_color="#DBEAFE",
            font=("Segoe UI", 12, "bold"),
            command=self.abrir_ajuda_credito,
        ).pack(side="left", padx=6)

    def _construir_corpo_principal(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=18)

        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=2)
        container.grid_rowconfigure(0, weight=1)

        # ================= COLUNA ESQUERDA: FORMULÁRIO =================
        form_scroll = ctk.CTkScrollableFrame(
            container, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA
        )
        form_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # 1. Tipo de Operação (Produtos NCM vs Serviços NBS)
        ctk.CTkLabel(
            form_scroll, text="1. O que está sendo vendido?", font=("Segoe UI", 14, "bold"), text_color=COR_TEXTO
        ).pack(anchor="w", padx=18, pady=(16, 6))

        self.seg_tipo = ctk.CTkSegmentedButton(
            form_scroll,
            values=["Produtos - NCM", "Serviços - NBS"],
            command=self.ao_mudar_tipo_operacao,
            font=("Segoe UI", 13, "bold"),
            height=36,
        )
        self.seg_tipo.set("Produtos - NCM")
        self.seg_tipo.pack(fill="x", padx=18, pady=(0, 10))

        frame_cod = ctk.CTkFrame(form_scroll, fg_color="transparent")
        frame_cod.pack(fill="x", padx=18, pady=(0, 4))

        self.lbl_cod_titulo = ctk.CTkLabel(
            frame_cod, text="Código NCM (8 dígitos):", font=("Segoe UI", 12, "bold"), text_color=COR_SUBTEXTO
        )
        self.lbl_cod_titulo.pack(anchor="w")

        row_cod = ctk.CTkFrame(frame_cod, fg_color="transparent")
        row_cod.pack(fill="x", pady=4)

        self.entry_codigo = ctk.CTkEntry(row_cod, placeholder_text="Ex: 10063021", height=36, font=("Segoe UI", 13))
        self.entry_codigo.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_codigo.bind("<KeyRelease>", self.ao_digitar_codigo)

        ctk.CTkButton(
            row_cod,
            text="🔍 Busca por nome",
            width=145,
            height=36,
            fg_color=COR_PRIMARIA,
            hover_color=COR_PRIMARIA_HOVER,
            font=("Segoe UI", 12, "bold"),
            command=self.abrir_busca_item,
        ).pack(side="right")

        self.lbl_item_desc = ctk.CTkLabel(
            form_scroll,
            text="Nenhum item selecionado (digite o código ou busque pelo nome).",
            font=("Segoe UI", 11, "italic"),
            text_color=COR_SUBTEXTO,
        )
        self.lbl_item_desc.pack(anchor="w", padx=18, pady=(0, 12))

        # 2. Classificação Tributária (CST + cClassTrib)
        ctk.CTkLabel(
            form_scroll, text="2. Classificação Tributária (LC 214/2025)", font=("Segoe UI", 14, "bold"), text_color=COR_TEXTO
        ).pack(anchor="w", padx=18, pady=(6, 6))

        row_cst_switch = ctk.CTkFrame(form_scroll, fg_color="transparent")
        row_cst_switch.pack(fill="x", padx=18, pady=(0, 6))

        self.switch_so_validas = ctk.CTkSwitch(
            row_cst_switch,
            text="Mostrar só as que valem para este código (★)",
            font=("Segoe UI", 12),
            command=self.atualizar_combo_classificacao,
        )
        self.switch_so_validas.pack(side="left")

        ctk.CTkButton(
            row_cst_switch,
            text="🔍 Busca por nome",
            width=145,
            height=30,
            fg_color=COR_DESTAQUE_BG,
            text_color=COR_PRIMARIA,
            hover_color="#DBEAFE",
            font=("Segoe UI", 12, "bold"),
            command=self.abrir_busca_classificacao,
        ).pack(side="right")

        ctk.CTkLabel(
            form_scroll, text="Situação Tributária (CST):", font=("Segoe UI", 12), text_color=COR_SUBTEXTO
        ).pack(anchor="w", padx=18)

        self.combo_cst = ctk.CTkComboBox(
            form_scroll,
            values=CST_LISTA,
            state="readonly",
            height=34,
            font=("Segoe UI", 12),
            command=lambda _: self.atualizar_combo_classificacao(),
        )
        self.combo_cst.set("Todos os CST")
        self.combo_cst.pack(fill="x", padx=18, pady=(2, 8))

        ctk.CTkLabel(
            form_scroll, text="Classificação (6 dígitos):", font=("Segoe UI", 12), text_color=COR_SUBTEXTO
        ).pack(anchor="w", padx=18)

        self.combo_class = ctk.CTkComboBox(
            form_scroll,
            values=[],
            state="readonly",
            height=34,
            font=("Segoe UI", 12),
            command=self.ao_selecionar_classificacao_combo,
        )
        self.combo_class.pack(fill="x", padx=18, pady=(2, 12))

        # 3. Valor, Data e Local da Operação
        ctk.CTkLabel(
            form_scroll, text="3. Dados da Operação e Destino", font=("Segoe UI", 14, "bold"), text_color=COR_TEXTO
        ).pack(anchor="w", padx=18, pady=(6, 6))

        grid_val_data = ctk.CTkFrame(form_scroll, fg_color="transparent")
        grid_val_data.pack(fill="x", padx=18, pady=(0, 8))
        grid_val_data.grid_columnconfigure(0, weight=1)
        grid_val_data.grid_columnconfigure(1, weight=1)

        # Valor
        f_val = ctk.CTkFrame(grid_val_data, fg_color="transparent")
        f_val.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(f_val, text="Valor do item (R$):", font=("Segoe UI", 12), text_color=COR_SUBTEXTO).pack(anchor="w")
        self.entry_valor = ctk.CTkEntry(f_val, height=36, font=("Segoe UI", 13))
        self.entry_valor.insert(0, "1000,00")
        self.entry_valor.pack(fill="x", pady=2)

        # Data
        f_data = ctk.CTkFrame(grid_val_data, fg_color="transparent")
        f_data.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(f_data, text="Data da operação (AAAA-MM-DD):", font=("Segoe UI", 12), text_color=COR_SUBTEXTO).pack(anchor="w")
        self.entry_data = ctk.CTkEntry(f_data, height=36, font=("Segoe UI", 13))
        self.entry_data.insert(0, "2027-01-15")
        self.entry_data.pack(fill="x", pady=2)
        self.entry_data.bind("<FocusOut>", lambda _: self.atualizar_aliquotas_por_data())
        self.entry_data.bind("<Return>", lambda _: self.atualizar_aliquotas_por_data())

        # Local (UF + Município)
        row_local = ctk.CTkFrame(form_scroll, fg_color="transparent")
        row_local.pack(fill="x", padx=18, pady=(4, 10))

        self.entry_uf = ctk.CTkEntry(row_local, width=65, height=36, font=("Segoe UI", 13))
        self.entry_uf.insert(0, "BA")
        self.entry_uf.pack(side="left", padx=(0, 8))

        self.entry_municipio = ctk.CTkEntry(row_local, height=36, font=("Segoe UI", 13))
        self.entry_municipio.insert(0, "Salvador")
        self.entry_municipio.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            row_local,
            text="🔍 Município",
            width=125,
            height=36,
            fg_color=COR_DESTAQUE_BG,
            text_color=COR_PRIMARIA,
            hover_color="#DBEAFE",
            font=("Segoe UI", 12, "bold"),
            command=self.abrir_busca_municipio,
        ).pack(side="right")

        # 4. Alíquotas de Referência (CBS, IBS Estadual, IBS Municipal)
        box_aliq = ctk.CTkFrame(form_scroll, fg_color=COR_DESTAQUE_BG, corner_radius=8)
        box_aliq.pack(fill="x", padx=18, pady=(6, 14))

        self.lbl_aviso_transicao = ctk.CTkLabel(
            box_aliq,
            text="",
            font=("Segoe UI", 11),
            text_color=COR_PRIMARIA_HOVER,
            wraplength=540,
            justify="left",
        )
        self.lbl_aviso_transicao.pack(anchor="w", padx=12, pady=(10, 8))

        grid_aliq = ctk.CTkFrame(box_aliq, fg_color="transparent")
        grid_aliq.pack(fill="x", padx=12, pady=(0, 12))
        grid_aliq.grid_columnconfigure((0, 1, 2), weight=1)

        # CBS
        f_cbs = ctk.CTkFrame(grid_aliq, fg_color="transparent")
        f_cbs.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f_cbs, text="CBS Federal (%):", font=("Segoe UI", 11, "bold"), text_color=COR_TEXTO).pack(anchor="w")
        self.entry_aliq_cbs = ctk.CTkEntry(f_cbs, height=32, font=("Segoe UI", 12))
        self.entry_aliq_cbs.pack(fill="x")

        # IBS Estadual
        f_ibs_e = ctk.CTkFrame(grid_aliq, fg_color="transparent")
        f_ibs_e.grid(row=0, column=1, sticky="ew", padx=3)
        ctk.CTkLabel(f_ibs_e, text="IBS Estadual (%):", font=("Segoe UI", 11, "bold"), text_color=COR_TEXTO).pack(anchor="w")
        self.entry_aliq_ibs_est = ctk.CTkEntry(f_ibs_e, height=32, font=("Segoe UI", 12))
        self.entry_aliq_ibs_est.pack(fill="x")

        # IBS Municipal
        f_ibs_m = ctk.CTkFrame(grid_aliq, fg_color="transparent")
        f_ibs_m.grid(row=0, column=2, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f_ibs_m, text="IBS Municipal (%):", font=("Segoe UI", 11, "bold"), text_color=COR_TEXTO).pack(anchor="w")
        self.entry_aliq_ibs_mun = ctk.CTkEntry(f_ibs_m, height=32, font=("Segoe UI", 12))
        self.entry_aliq_ibs_mun.pack(fill="x")

        # Botão Calcular
        ctk.CTkButton(
            form_scroll,
            text="Calcular Tributos (CBS / IBS)",
            height=44,
            font=("Segoe UI", 15, "bold"),
            fg_color=COR_PRIMARIA,
            hover_color=COR_PRIMARIA_HOVER,
            command=self.calcular,
        ).pack(fill="x", padx=18, pady=(4, 18))

        # ================= COLUNA DIREITA: RESULTADOS =================
        self.painel_resultado = ctk.CTkFrame(
            container, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA
        )
        self.painel_resultado.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            self.painel_resultado,
            text="Demonstrativo da Nota Fiscal",
            font=("Segoe UI", 17, "bold"),
            text_color=COR_TEXTO,
        ).pack(anchor="w", padx=20, pady=(18, 2))

        self.lbl_res_subtitulo = ctk.CTkLabel(
            self.painel_resultado,
            text="Preencha os dados e clique em Calcular.",
            font=("Segoe UI", 12),
            text_color=COR_SUBTEXTO,
        )
        self.lbl_res_subtitulo.pack(anchor="w", padx=20, pady=(0, 14))

        # Cards de destaque
        self.card_total = ctk.CTkFrame(self.painel_resultado, fg_color=COR_DESTAQUE_BG, corner_radius=10)
        self.card_total.pack(fill="x", padx=20, pady=(0, 14))

        ctk.CTkLabel(
            self.card_total, text="VALOR TOTAL DA OPERAÇÃO (COM TRIBUTOS POR FORA)", font=("Segoe UI", 10, "bold"), text_color=COR_PRIMARIA
        ).pack(anchor="w", padx=16, pady=(12, 2))

        self.lbl_res_total_nota = ctk.CTkLabel(
            self.card_total, text="R$ 0,00", font=("Segoe UI", 26, "bold"), text_color=COR_TEXTO
        )
        self.lbl_res_total_nota.pack(anchor="w", padx=16, pady=(0, 12))

        # Tabela detalhada dos tributos
        self.frame_linhas = ctk.CTkFrame(self.painel_resultado, fg_color=COR_FUNDO, corner_radius=8)
        self.frame_linhas.pack(fill="x", padx=20, pady=(0, 14))

        self.lbl_v_base = self._criar_linha_res(self.frame_linhas, "Base de Cálculo (Valor Líquido):")
        self.lbl_v_cbs = self._criar_linha_res(self.frame_linhas, "CBS Federal (Alíquota Efetiva):")
        self.lbl_v_ibs_est = self._criar_linha_res(self.frame_linhas, "IBS Estadual (Alíquota Efetiva):")
        self.lbl_v_ibs_mun = self._criar_linha_res(self.frame_linhas, "IBS Municipal (Alíquota Efetiva):")
        self.lbl_v_total_trib = self._criar_linha_res(self.frame_linhas, "Total CBS + IBS:", negrito=True)

        # Quadro Comparativo: Crédito / Simples Nacional / Base Legal
        self.box_comparativo = ctk.CTkTextbox(
            self.painel_resultado,
            font=("Segoe UI", 12),
            fg_color=COR_FUNDO,
            text_color=COR_TEXTO,
            corner_radius=8,
            wrap="word",
        )
        self.box_comparativo.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.box_comparativo.insert(
            "1.0",
            "Resumo Legal e Crédito:\n• Cálculo efetuado 'por fora' (não incide sobre si mesmo).\n• Selecione um item e clique em Calcular para ver o crédito gerado na não cumulatividade.",
        )
        self.box_comparativo.configure(state="disabled")

    def _criar_linha_res(self, parent, titulo, negrito=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=6)
        fonte = ("Segoe UI", 13, "bold") if negrito else ("Segoe UI", 12)
        ctk.CTkLabel(row, text=titulo, font=fonte, text_color=COR_TEXTO).pack(side="left")
        lbl = ctk.CTkLabel(row, text="R$ 0,00", font=fonte, text_color=COR_TEXTO)
        lbl.pack(side="right")
        return lbl

    def _construir_rodape(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkLabel(
            footer,
            text="Base legal: EC 132/2023 e Lei Complementar 214/2025. Ferramenta de simulação educacional/gerencial — não substitui orientação contábil.",
            font=("Segoe UI", 11),
            text_color=COR_SUBTEXTO,
        ).pack(side="left")

    # ================= EVENTOS E LÓGICA DE NEGÓCIO =================

    def ao_mudar_tipo_operacao(self, valor):
        if "NCM" in valor:
            self.tipo_operacao = "NCM"
            self.lbl_cod_titulo.configure(text="Código NCM (8 dígitos):")
            self.entry_codigo.configure(placeholder_text="Ex: 10063021")
        else:
            self.tipo_operacao = "NBS"
            self.lbl_cod_titulo.configure(text="Código NBS (9 dígitos):")
            self.entry_codigo.configure(placeholder_text="Ex: 122011200")

        self.entry_codigo.delete(0, "end")
        self.item_selecionado = None
        self.lbl_item_desc.configure(text="Nenhum item selecionado.")
        self.atualizar_combo_classificacao()

    def ao_digitar_codigo(self, event=None):
        cod = "".join(filter(str.isdigit, self.entry_codigo.get()))
        lista = NCM_LISTA if self.tipo_operacao == "NCM" else NBS_LISTA
        encontrado = next((x for x in lista if x["codigo"] == cod), None)

        if encontrado:
            self.item_selecionado = encontrado
            self.lbl_item_desc.configure(
                text=f"✔ {encontrado['descricao']} ({encontrado['anexo']})", text_color="#047857"
            )
            # Sugere automaticamente a classificação do anexo
            sugerida = next(
                (c for c in CLASSIFICACOES_TRIBUTARIAS if c["codigo"] == encontrado["cclass_sugerida"]), None
            )
            if sugerida:
                self.classificacao_atual = sugerida
                self.combo_cst.set("Todos os CST")
        else:
            self.item_selecionado = None
            if len(cod) >= 8:
                self.lbl_item_desc.configure(
                    text="Código não consta nos anexos específicos — aplicada Regra Geral (000001).",
                    text_color=COR_SUBTEXTO,
                )
            else:
                self.lbl_item_desc.configure(text="Digite o código completo ou busque por nome.", text_color=COR_SUBTEXTO)

        self.atualizar_combo_classificacao()

    def atualizar_combo_classificacao(self):
        cst_filtro = self.combo_cst.get()[:3]
        so_validas = self.switch_so_validas.get() == 1
        cod_sugerido = self.item_selecionado["cclass_sugerida"] if self.item_selecionado else "000001"

        opcoes_formatadas = []
        mapa_opcoes = {}

        # Ordena colocando benefícios do item e padrão no topo
        ordenadas = sorted(
            CLASSIFICACOES_TRIBUTARIAS,
            key=lambda c: (0 if c["codigo"] == cod_sugerido else (1 if c["padrao"] else 2), c["codigo"]),
        )

        for c in ordenadas:
            if cst_filtro != "Tod" and c["cst"] != cst_filtro:
                continue

            eh_sugerida = c["codigo"] == cod_sugerido
            eh_padrao = c["padrao"]

            if so_validas and self.item_selecionado and not (eh_sugerida or eh_padrao):
                continue

            prefixo = ""
            if eh_sugerida and not eh_padrao:
                prefixo = "★ [Benefício da Lei] "
            elif eh_padrao:
                prefixo = "★ [Padrão] "

            label = f"{prefixo}{c['codigo']} - {c['nome']}"
            opcoes_formatadas.append(label)
            mapa_opcoes[label] = c

        if not opcoes_formatadas:
            opcoes_formatadas = ["000001 - Tributação integral padrão (Regra Geral)"]
            mapa_opcoes[opcoes_formatadas[0]] = CLASSIFICACOES_TRIBUTARIAS[0]

        self.mapa_classificacoes = mapa_opcoes
        self.combo_class.configure(values=opcoes_formatadas)

        # Seleciona a classificação atual se estiver na lista
        selecionada_label = next(
            (lbl for lbl, obj in mapa_opcoes.items() if obj["codigo"] == self.classificacao_atual["codigo"]),
            opcoes_formatadas[0],
        )
        self.combo_class.set(selecionada_label)
        self.classificacao_atual = mapa_opcoes[selecionada_label]

    def ao_selecionar_classificacao_combo(self, escolha):
        if escolha in self.mapa_classificacoes:
            self.classificacao_atual = self.mapa_classificacoes[escolha]

    def atualizar_aliquotas_por_data(self):
        data_txt = self.entry_data.get().strip()
        try:
            ano = datetime.strptime(data_txt, "%Y-%m-%d").year
        except ValueError:
            ano = 2027

        if ano < 2026:
            ano = 2026
        elif ano > 2033:
            ano = 2033

        regra = CRONOGRAMA_TRANSICAO[ano]
        self.entry_aliq_cbs.delete(0, "end")
        self.entry_aliq_cbs.insert(0, str(regra["cbs"]).replace(".", ","))

        self.entry_aliq_ibs_est.delete(0, "end")
        self.entry_aliq_ibs_est.insert(0, str(regra["ibs_est"]).replace(".", ","))

        self.entry_aliq_ibs_mun.delete(0, "end")
        self.entry_aliq_ibs_mun.insert(0, str(regra["ibs_mun"]).replace(".", ","))

        self.lbl_aviso_transicao.configure(text=f"Regra {regra['nota']} Ajuste abaixo se quiser simular:")

    # ================= MODAIS DE BUSCA =================

    def abrir_busca_item(self):
        if self.tipo_operacao == "NCM":
            ModalBusca(
                self,
                "Buscar Produto por Nome (NCM)",
                "Digite o nome da mercadoria (ex: arroz, notebook, medicamento):",
                NCM_LISTA,
                lambda x: f"{x['codigo']} — {x['descricao']} [{x['anexo']}]",
                self._selecionar_item_modal,
            )
        else:
            ModalBusca(
                self,
                "Buscar Serviço por Nome (NBS)",
                "Digite o nome do serviço (ex: educação, saúde, software):",
                NBS_LISTA,
                lambda x: f"{x['codigo']} — {x['descricao']} [{x['anexo']}]",
                self._selecionar_item_modal,
            )

    def _selecionar_item_modal(self, item):
        self.entry_codigo.delete(0, "end")
        self.entry_codigo.insert(0, item["codigo"])
        self.ao_digitar_codigo()

    def abrir_busca_classificacao(self):
        ModalBusca(
            self,
            "Buscar Classificação Tributária (LC 214/2025)",
            "Digite o setor ou benefício (ex: cesta básica, saúde, imunidade, redução):",
            CLASSIFICACOES_TRIBUTARIAS,
            lambda c: f"{c['codigo']} (CST {c['cst']}) — {c['nome']} | {c['base_legal']}",
            self._selecionar_classificacao_modal,
        )

    def _selecionar_classificacao_modal(self, c):
        self.classificacao_atual = c
        self.combo_cst.set("Todos os CST")
        self.atualizar_combo_classificacao()

    def abrir_busca_municipio(self):
        ModalBusca(
            self,
            "Buscar Município de Destino (Princípio do Destino)",
            "Digite o nome da cidade ou sigla do estado (ex: Salvador, São Paulo):",
            MUNICIPIOS_LISTA,
            lambda m: f"{m['municipio']} - {m['uf']} (IBGE: {m['ibge']})",
            self._selecionar_municipio_modal,
        )

    def _selecionar_municipio_modal(self, m):
        self.entry_uf.delete(0, "end")
        self.entry_uf.insert(0, m["uf"])
        self.entry_municipio.delete(0, "end")
        self.entry_municipio.insert(0, m["municipio"])

    # ================= CÁLCULO PRINCIPAL =================

    def calcular(self):
        try:
            base = Decimal(self.entry_valor.get().strip().replace(".", "").replace(",", "."))
            aliq_cbs_ref = Decimal(self.entry_aliq_cbs.get().strip().replace(",", "."))
            aliq_ibs_est_ref = Decimal(self.entry_aliq_ibs_est.get().strip().replace(",", "."))
            aliq_ibs_mun_ref = Decimal(self.entry_aliq_ibs_mun.get().strip().replace(",", "."))

            if base < 0 or aliq_cbs_ref < 0 or aliq_ibs_est_ref < 0 or aliq_ibs_mun_ref < 0:
                raise ValueError("Valores negativos não permitidos.")

            red_cbs = Decimal(str(self.classificacao_atual["reducao_cbs"])) / Decimal("100")
            red_ibs = Decimal(str(self.classificacao_atual["reducao_ibs"])) / Decimal("100")

            # Alíquotas efetivas após aplicar redução da Classificação Tributária
            aliq_cbs_efetiva = aliq_cbs_ref * (Decimal("1") - red_cbs)
            aliq_ibs_est_efetiva = aliq_ibs_est_ref * (Decimal("1") - red_ibs)
            aliq_ibs_mun_efetiva = aliq_ibs_mun_ref * (Decimal("1") - red_ibs)

            # Cálculo por fora (Art. 12 da LC 214/2025)
            val_cbs = (base * aliq_cbs_efetiva) / Decimal("100")
            val_ibs_est = (base * aliq_ibs_est_efetiva) / Decimal("100")
            val_ibs_mun = (base * aliq_ibs_mun_efetiva) / Decimal("100")

            total_tributos = val_cbs + val_ibs_est + val_ibs_mun
            total_nota = base + total_tributos
            carga_total_pct = aliq_cbs_efetiva + aliq_ibs_est_efetiva + aliq_ibs_mun_efetiva

            # Atualiza interface
            uf = self.entry_uf.get().strip().upper()
            mun = self.entry_municipio.get().strip()
            self.lbl_res_subtitulo.configure(
                text=f"Destino: {mun}/{uf} • CST {self.classificacao_atual['cst']} ({self.classificacao_atual['codigo']})"
            )

            self.lbl_res_total_nota.configure(text=formatar_moeda(total_nota))
            self.lbl_v_base.configure(text=formatar_moeda(base))
            self.lbl_v_cbs.configure(text=f"{formatar_moeda(val_cbs)} ({formatar_pct(aliq_cbs_efetiva)})")
            self.lbl_v_ibs_est.configure(text=f"{formatar_moeda(val_ibs_est)} ({formatar_pct(aliq_ibs_est_efetiva)})")
            self.lbl_v_ibs_mun.configure(text=f"{formatar_moeda(val_ibs_mun)} ({formatar_pct(aliq_ibs_mun_efetiva)})")
            self.lbl_v_total_trib.configure(text=f"{formatar_moeda(total_tributos)} ({formatar_pct(carga_total_pct)})")

            # Comparativo de Crédito e Enquadramento Legal
            credito_regime_regular = total_tributos
            credito_simples_das = total_tributos * Decimal("0.22")  # Estimativa média de repasse via DAS

            resumo_legal = (
                f"ENQUADRAMENTO LEGAL:\n"
                f"• Classificação: {self.classificacao_atual['codigo']} — {self.classificacao_atual['nome']}\n"
                f"• Fundamentação: {self.classificacao_atual['base_legal']}\n"
                f"• Redução aplicada: CBS -{self.classificacao_atual['reducao_cbs']:.0f}% | IBS -{self.classificacao_atual['reducao_ibs']:.0f}%\n\n"
                f"NÃO CUMULATIVIDADE E CRÉDITO DO COMPRADOR (LC 214/2025):\n"
                f"• Compra no Regime Regular (Lucro Real/Presumido): O adquirente PJ credita {formatar_moeda(credito_regime_regular)} integralmente após o recolhimento (ou via Split Payment).\n"
                f"• Compra do Simples Nacional (dentro do DAS): O adquirente credita apenas a parcela recolhida no DAS (~{formatar_moeda(credito_simples_das)}), salvo se o fornecedor optar pelo recolhimento regular por fora.\n"
                f"• Consumidor Final (PF): Não gera crédito; famílias no CadÚnico têm direito a Cashback conforme a lei."
            )

            self.box_comparativo.configure(state="normal")
            self.box_comparativo.delete("1.0", "end")
            self.box_comparativo.insert("1.0", resumo_legal)
            self.box_comparativo.configure(state="disabled")

        except Exception:
            messagebox.showerror("Erro de Validação", "Verifique se o valor e as alíquotas contêm apenas números válidos.")

    # ================= GUIAS EXPLICATIVAS =================

    def abrir_ajuda_transicao(self):
        texto = (
            "CRONOGRAMA DE TRANSIÇÃO DA REFORMA TRIBUTÁRIA (2026 A 2033)\n"
            "Base: Emenda Constitucional 132/2023 e LC 214/2025 (Arts. 343 a 348)\n\n"
            "• 2026 (Ano de Teste): CBS de 0,9% e IBS de 0,1% destacados na nota fiscal, compensáveis com PIS/Cofins. Sem aumento de carga para quem cumprir as obrigações acessórias. Simples Nacional fica de fora.\n\n"
            "• 2027: Extinção definitiva de PIS e Cofins. Entrada da CBS cheia (estimada pelo TCU em 11,3%). O IPI é zerado (exceto para produtos concorrentes da Zona Franca de Manaus) e inicia-se o Imposto Seletivo (IS). O IBS permanece em 0,1%.\n\n"
            "• 2028: Mantém as mesmas regras de 2027.\n\n"
            "• 2029 a 2032 (Transição Federativa): Redução gradual de ICMS e ISS (90% em 2029, 80% em 2030, 70% em 2031 e 60% em 2032) com elevação proporcional do IBS Estadual e Municipal.\n\n"
            "• 2033 (Sistema Novo Completo): Extinção total do ICMS e do ISS. Vigência plena do IVA Dual (CBS + IBS) e do Imposto Seletivo, com cobrança integral no destino."
        )
        ModalTextoInformativo(self, "Convivência entre os Impostos (2026–2033)", texto)

    def abrir_ajuda_credito(self):
        texto = (
            "COMO FUNCIONA A NÃO CUMULATIVIDADE E O CRÉDITO (LC 214/2025)\n\n"
            "1. CÁLCULO 'POR FORA':\n"
            "Diferente do ICMS e PIS/Cofins atuais, a CBS e o IBS não integram sua própria base de cálculo, garantindo transparência total no documento fiscal (NF-e, NFC-e e NFS-e).\n\n"
            "2. CRÉDITO FINANCEIRO AMPLO:\n"
            "Toda aquisição de bens e serviços ligada à atividade econômica gera crédito integral (energia, aluguel, software, ativo imobilizado), exceto bens de uso e consumo pessoal (joias, bebidas alcoólicas, armas, etc.).\n\n"
            "3. SPLIT PAYMENT E CRÉDITO CONDICIONADO AO PAGAMENTO:\n"
            "O direito ao crédito depende do efetivo recolhimento do tributo na etapa anterior. Com o Split Payment eletrônico (Pix, cartão, boleto), o valor do imposto é segregado na liquidação financeira e enviado diretamente ao Comitê Gestor e à Receita Federal.\n\n"
            "4. SIMPLES NACIONAL E CASHBACK:\n"
            "• Empresas do Simples podem recolher CBS/IBS dentro do DAS (transferindo crédito menor) ou optar pelo regime regular por fora.\n"
            "• Famílias de baixa renda (CadÚnico) recebem devolução personalizada (Cashback) em contas de energia, água, gás e telecomunicações."
        )
        ModalTextoInformativo(self, "Não Cumulatividade, Split Payment e Crédito", texto)


if __name__ == "__main__":
    app = CalculadoraCBSIBSApp()
    app.mainloop()