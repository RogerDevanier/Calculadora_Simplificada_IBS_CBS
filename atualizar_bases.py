import urllib.request
import json
import csv
import gzip
import io
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def baixar_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def classificar_ncm_lc214(codigo: str, descricao: str) -> tuple[str, str]:
    """Cruza o código NCM de 8 dígitos com as regras da LC 214/2025."""
    desc_low = descricao.lower()

    # Anexo I - Cesta Básica Nacional (Alíquota Zero - cClassTrib 200003)
    prefixos_cesta = (
        "100630", "100640", "071333", "040110", "040120", "040210", "040221",
        "0201", "0202", "0203", "0207", "0302", "0303", "0304", "040721",
        "19059090", "110220", "110620", "15079011", "170114", "090111", "090121",
        "040510", "040610", "190211", "190219", "25010020", "0701", "0702",
        "0703", "0704", "0705", "0706", "0707", "0708", "0709", "0803", "0804",
        "0805", "0806", "0807", "0808", "0809", "0810"
    )
    if codigo.startswith(prefixos_cesta):
        return "Anexo I - Cesta Básica Nacional (LC 214/2025)", "200003"

    # Anexo IV - Medicamentos e Dispositivos Médicos (Redução 60% - cClassTrib 200009)
    if codigo.startswith(("3003", "3004", "3002", "9018", "9019", "9021")):
        return "Anexo IV - Medicamentos/Saúde (LC 214/2025)", "200009"

    # Imunidade Constitucional - Livros, Jornais e Papel Imune (cClassTrib 410001)
    if codigo.startswith(("4901", "4902", "4903", "480100")):
        return "Imunidade Constitucional (CF/88 Art. 150, VI, d)", "410001"

    # Imposto Seletivo (Art. 409 LC 214/2025 - Cigarros, Bebidas Alcoólicas/Açucaradas, Veículos, Minérios)
    if codigo.startswith(("2402", "2203", "2204", "2205", "2206", "2208", "220210", "8703", "2601", "2709")):
        return "Art. 409 - Sujeito ao Imposto Seletivo (IS)", "000002"

    return "Regra Geral (Tributação Integral)", "000001"


def classificar_nbs_lc214(codigo: str, descricao: str) -> tuple[str, str]:
    """Cruza o código NBS de 9 dígitos com os anexos de serviços da LC 214/2025."""
    # Anexo II - Serviços de Educação (Redução 60% - cClassTrib 200028)
    if codigo.startswith("122"):
        return "Anexo II - Serviços de Educação (LC 214/2025)", "200028"

    # Anexo III - Serviços de Saúde (Redução 60% - cClassTrib 200029)
    if codigo.startswith("123"):
        return "Anexo III - Serviços de Saúde (LC 214/2025)", "200029"

    # Anexo IX - Transporte Coletivo de Passageiros (cClassTrib 200015)
    if codigo.startswith(("1040111", "1040112")):
        return "Anexo IX - Transporte Coletivo Urbano (LC 214/2025)", "200015"

    # Art. 127 - Profissões Intelectuais Regulamentadas (Redução 30% - cClassTrib 200035)
    if codigo.startswith(("11402", "11403", "11404", "11405")):
        return "Art. 127 - Profissões Regulamentadas (Redução 30%)", "200035"

    return "Regra Geral (Tributação Integral)", "000001"


def carregar_ncms():
    print("1/3 Baixando tabela completa de NCMs (BrasilAPI / Siscomex)...")
    raw = baixar_bytes("https://brasilapi.com.br/api/ncm/v1")
    dados = json.loads(raw.decode("utf-8"))
    ncms = []
    for item in dados:
        cod_limpo = re.sub(r"\D", "", item.get("codigo", ""))
        if len(cod_limpo) == 8:  # Apenas códigos completos de 8 dígitos usados na NF-e
            desc = re.sub(r"^[-–\s]+", "", item.get("descricao", "").strip())
            anexo, cclass = classificar_ncm_lc214(cod_limpo, desc)
            ncms.append({
                "codigo": cod_limpo,
                "descricao": desc,
                "anexo": anexo,
                "cclass_sugerida": cclass,
            })
    print(f"   -> {len(ncms)} NCMs de 8 dígitos carregados.")
    return ncms


def carregar_nbs():
    print("2/3 Baixando tabela oficial completa de NBS 2.0 (Portal Gov.br / MDIC)...")
    raw = baixar_bytes("https://www.gov.br/mdic/pt-br/images/REPOSITORIO/scs/decos/NBS/NBSa_2-0.csv")
    texto = raw.decode("latin-1", errors="replace")
    leitor = csv.reader(io.StringIO(texto), delimiter=";")
    nbs_lista = []
    for linha in leitor:
        if len(linha) < 2:
            continue
        cod_limpo = re.sub(r"\D", "", linha[0])
        if len(cod_limpo) == 9:  # Apenas códigos completos de 9 dígitos da NBS
            desc = linha[1].strip()
            anexo, cclass = classificar_nbs_lc214(cod_limpo, desc)
            nbs_lista.append({
                "codigo": cod_limpo,
                "descricao": desc,
                "anexo": anexo,
                "cclass_sugerida": cclass,
            })
    print(f"   -> {len(nbs_lista)} códigos NBS de 9 dígitos carregados.")
    return nbs_lista


def carregar_municipios():
    print("3/3 Baixando todos os municípios do Brasil (API Oficial IBGE)...")
    raw = baixar_bytes("https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado")
    dados = json.loads(raw.decode("utf-8"))
    municipios = []
    for m in dados:
        municipios.append({
            "uf": m["UF-sigla"],
            "municipio": m["municipio-nome"],
            "ibge": str(m["municipio-id"]),
        })
    municipios.sort(key=lambda x: (x["uf"], x["municipio"]))
    print(f"   -> {len(municipios)} municípios brasileiros carregados.")
    return municipios


if __name__ == "__main__":
    base_completa = {
        "ncm": carregar_ncms(),
        "nbs": carregar_nbs(),
        "municipios": carregar_municipios(),
    }
    arquivo_saida = "base_oficial_reforma.json.gz"
    with gzip.open(arquivo_saida, "wt", encoding="utf-8") as f:
        json.dump(base_completa, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\nConcluído! Arquivo '{arquivo_saida}' gerado com sucesso.")