# Base de dados estruturada conforme LC 214/2025 e tabelas da Receita Federal

NCM_LISTA = [
    {"codigo": "10063021", "descricao": "Arroz semibranqueado ou branqueado (polido)", "anexo": "Anexo I - Cesta Básica Nacional", "cclass_sugerida": "200003"},
    {"codigo": "07133319", "descricao": "Feijão comum preto", "anexo": "Anexo I - Cesta Básica Nacional", "cclass_sugerida": "200003"},
    {"codigo": "04012010", "descricao": "Leite UHT (longa vida)", "anexo": "Anexo I - Cesta Básica Nacional", "cclass_sugerida": "200003"},
    {"codigo": "02013000", "descricao": "Carnes desossadas de bovino, frescas ou refrigeradas", "anexo": "Anexo I - Cesta Básica Nacional", "cclass_sugerida": "200003"},
    {"codigo": "19059090", "descricao": "Pão francês comum", "anexo": "Anexo I - Cesta Básica Nacional", "cclass_sugerida": "200003"},
    {"codigo": "30049099", "descricao": "Medicamentos de uso humano (lista regulada)", "anexo": "Anexo IV - Medicamentos", "cclass_sugerida": "200009"},
    {"codigo": "84713012", "descricao": "Notebook / Computador portátil", "anexo": "Regra Geral", "cclass_sugerida": "000001"},
    {"codigo": "85171300", "descricao": "Smartphones / Telefones celulares", "anexo": "Regra Geral", "cclass_sugerida": "000001"},
    {"codigo": "22030000", "descricao": "Cervejas de malte (Sujeito a Imposto Seletivo)", "anexo": "Art. 409 - Imposto Seletivo", "cclass_sugerida": "000002"},
    {"codigo": "87032210", "descricao": "Automóvel de passageiros", "anexo": "Art. 409 - Imposto Seletivo", "cclass_sugerida": "000002"},
    {"codigo": "49019900", "descricao": "Livros, jornais e periódicos", "anexo": "Imunidade Constitucional (Art. 150, VI, d)", "cclass_sugerida": "410001"},
]

NBS_LISTA = [
    {"codigo": "122011200", "descricao": "Serviços de educação infantil (pré-escola)", "anexo": "Anexo II - Educação", "cclass_sugerida": "200028"},
    {"codigo": "122031000", "descricao": "Serviços de ensino superior (graduação)", "anexo": "Anexo II - Educação", "cclass_sugerida": "200028"},
    {"codigo": "123011100", "descricao": "Serviços médicos e hospitalares", "anexo": "Anexo III - Saúde", "cclass_sugerida": "200029"},
    {"codigo": "123012100", "descricao": "Serviços odontológicos", "anexo": "Anexo III - Saúde", "cclass_sugerida": "200029"},
    {"codigo": "115011000", "descricao": "Desenvolvimento de software sob encomenda", "anexo": "Regra Geral", "cclass_sugerida": "000001"},
    {"codigo": "114011100", "descricao": "Consultoria em gestão empresarial", "anexo": "Regra Geral", "cclass_sugerida": "000001"},
    {"codigo": "114031100", "descricao": "Serviços advocatícios (Profissão Regulamentada)", "anexo": "Art. 127 - Profissões Intelectuais", "cclass_sugerida": "200035"},
    {"codigo": "114021100", "descricao": "Serviços de contabilidade e auditoria", "anexo": "Art. 127 - Profissões Intelectuais", "cclass_sugerida": "200035"},
    {"codigo": "104011100", "descricao": "Transporte público coletivo urbano de passageiros", "anexo": "Anexo IX - Transporte Coletivo", "cclass_sugerida": "200015"},
]

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

MUNICIPIOS_LISTA = [
    {"uf": "BA", "municipio": "Salvador", "ibge": "2927408"},
    {"uf": "BA", "municipio": "Feira de Santana", "ibge": "2910800"},
    {"uf": "BA", "municipio": "Camaçari", "ibge": "2905701"},
    {"uf": "SP", "municipio": "São Paulo", "ibge": "3550308"},
    {"uf": "SP", "municipio": "Campinas", "ibge": "3509502"},
    {"uf": "RJ", "municipio": "Rio de Janeiro", "ibge": "3304557"},
    {"uf": "MG", "municipio": "Belo Horizonte", "ibge": "3106200"},
    {"uf": "PR", "municipio": "Curitiba", "ibge": "4106902"},
    {"uf": "RS", "municipio": "Porto Alegre", "ibge": "4314902"},
    {"uf": "DF", "municipio": "Brasília", "ibge": "5300108"},
    {"uf": "PE", "municipio": "Recife", "ibge": "2611606"},
    {"uf": "CE", "municipio": "Fortaleza", "ibge": "2304400"},
    {"uf": "AM", "municipio": "Manaus (Zona Franca)", "ibge": "1302603"},
]

# Cronograma oficial de transição (EC 132/2023 e LC 214/2025 Arts. 343-348)
# Estimativa TCU para CBS cheia: 11,30% | Estimativa IBS cheio: 17,70% (10,62% Est + 7,08% Mun)
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