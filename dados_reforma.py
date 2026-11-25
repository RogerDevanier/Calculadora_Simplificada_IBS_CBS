import os
import sys
import json
import gzip


def _caminho_recurso(nome_arquivo: str) -> str:
    """Resolve o caminho tanto em desenvolvimento quanto dentro do .exe do PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, nome_arquivo)


def _carregar_base_oficial():
    caminho = _caminho_recurso("base_oficial_reforma.json.gz")
    if os.path.exists(caminho):
        with gzip.open(caminho, "rt", encoding="utf-8") as f:
            return json.load(f)
    return {"ncm": [], "nbs": [], "municipios": []}


_BASE = _carregar_base_oficial()

NCM_LISTA = _BASE.get("ncm", [])
NBS_LISTA = _BASE.get("nbs", [])
MUNICIPIOS_LISTA = _BASE.get("municipios", [])

CST_LISTA = [
    "Todos os CST",
    "000 - Tributação Integral",
    "200 - Alíquota Reduzida",
    "400 - Isenção",
    "410 - Imunidade e Não Incidência",
    "510 - Diferimento",
]

CLASSIFICACOES_TRIBUTARIAS = [
    {"codigo": "000001", "cst": "000", "nome": "Tributação integral padrão (Regra Geral)", "reducao_cbs": 0.0, "reducao_ibs": 0.0, "base_legal": "LC 214/2025, Art. 14", "padrao": True},
    {"codigo": "000002", "cst": "000", "nome": "Tributação integral + sujeição ao Imposto Seletivo (IS)", "reducao_cbs": 0.0, "reducao_ibs": 0.0, "base_legal": "LC 214/2025, Art. 409", "padrao": False},
    {"codigo": "200003", "cst": "200", "nome": "Cesta Básica Nacional de Alimentos (Alíquota Zero)", "reducao_cbs": 100.0, "reducao_ibs": 100.0, "base_legal": "LC 214/2025, Art. 125 / Anexo I", "padrao": False},
    {"codigo": "200009", "cst": "200", "nome": "Medicamentos e dispositivos médicos (Redução 60%)", "reducao_cbs": 60.0, "reducao_ibs": 60.0, "base_legal": "LC 214/2025, Art. 130 / Anexo IV", "padrao": False},
    {"codigo": "200015", "cst": "200", "nome": "Transporte público coletivo urbano (Redução 100% CBS / 60% IBS)", "reducao_cbs": 100.0, "reducao_ibs": 60.0, "base_legal": "LC 214/2025, Art. 157 / Anexo IX", "padrao": False},
    {"codigo": "200028", "cst": "200", "nome": "Serviços de Educação (Redução de 60%)", "reducao_cbs": 60.0, "reducao_ibs": 60.0, "base_legal": "LC 214/2025, Art. 129 / Anexo II", "padrao": False},
    {"codigo": "200029", "cst": "200", "nome": "Serviços de Saúde (Redução de 60%)", "reducao_cbs": 60.0, "reducao_ibs": 60.0, "base_legal": "LC 214/2025, Art. 128 / Anexo III", "padrao": False},
    {"codigo": "200035", "cst": "200", "nome": "Profissões Intelectuais Regulamentadas (Redução de 30%)", "reducao_cbs": 30.0, "reducao_ibs": 30.0, "base_legal": "LC 214/2025, Art. 127", "padrao": False},
    {"codigo": "400001", "cst": "400", "nome": "Isenção legal específica (LC 214/2025)", "reducao_cbs": 100.0, "reducao_ibs": 100.0, "base_legal": "LC 214/2025, Arts. 142-156", "padrao": False},
    {"codigo": "410001", "cst": "410", "nome": "Imunidade Constitucional (Livros, Exportação, Entes)", "reducao_cbs": 100.0, "reducao_ibs": 100.0, "base_legal": "CF/88 Art. 150, VI e LC 214/2025 Art. 8º", "padrao": False},
    {"codigo": "510001", "cst": "510", "nome": "Diferimento na cadeia produtiva (Insumos Agropecuários)", "reducao_cbs": 100.0, "reducao_ibs": 100.0, "base_legal": "LC 214/2025, Art. 138", "padrao": False},
]

CRONOGRAMA_TRANSICAO = {
    2026: {"cbs": 0.90, "ibs_est": 0.05, "ibs_mun": 0.05, "icms_iss_fator": 1.0, "nota": "2026 (Teste): CBS 0,9% e IBS 0,1% compensáveis com PIS/Cofins."},
    2027: {"cbs": 11.30, "ibs_est": 0.05, "ibs_mun": 0.05, "icms_iss_fator": 1.0, "nota": "2027: Extinção PIS/Cofins, entrada da CBS cheia (est. TCU 11,3%) e IBS simbólico 0,1%."},
    2028: {"cbs": 11.30, "ibs_est": 0.05, "ibs_mun": 0.05, "icms_iss_fator": 1.0, "nota": "2028: Mesma regra de 2027 antes da redução gradual de ICMS/ISS."},
    2029: {"cbs": 11.30, "ibs_est": 1.06, "ibs_mun": 0.71, "icms_iss_fator": 0.9, "nota": "2029: ICMS/ISS caem para 90%; IBS sobe para 10% da alíquota cheia."},
    2030: {"cbs": 11.30, "ibs_est": 2.12, "ibs_mun": 1.42, "icms_iss_fator": 0.8, "nota": "2030: ICMS/ISS caem para 80%; IBS sobe para 20% da alíquota cheia."},
    2031: {"cbs": 11.30, "ibs_est": 3.19, "ibs_mun": 2.12, "icms_iss_fator": 0.7, "nota": "2031: ICMS/ISS caem para 70%; IBS sobe para 30% da alíquota cheia."},
    2032: {"cbs": 11.30, "ibs_est": 4.25, "ibs_mun": 2.83, "icms_iss_fator": 0.6, "nota": "2032: ICMS/ISS caem para 60%; IBS sobe para 40% da alíquota cheia."},
    2033: {"cbs": 11.30, "ibs_est": 10.62, "ibs_mun": 7.08, "icms_iss_fator": 0.0, "nota": "2033: Sistema novo completo (IVA Dual). Extinção total de ICMS e ISS."},
}