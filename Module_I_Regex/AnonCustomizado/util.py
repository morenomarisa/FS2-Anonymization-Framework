import pandas as pd
import re
import os
import pathlib

BASE_UTIL = os.path.dirname(os.path.abspath(__file__))

def path_base_nome(x):
    return os.path.join(BASE_UTIL, "names_apps_banks", x)

df_base_nomes = pd.read_csv(path_base_nome('base_nomes_atualizada.csv'))
base_nomes = set(list(df_base_nomes['BASE_NOMES']))

def get_columns(local_arquivo, nome_coluna_relatos):
    if local_arquivo.endswith('.xlsx'):
        df = pd.read_excel(local_arquivo)
    else:
        df = pd.read_csv(local_arquivo)
    relatos = df[nome_coluna_relatos].astype(str).values
    return df, relatos


def get_data_frame(relatos, regex, nome_coluna, funcao):
    values = [funcao(relato, regex) for relato in relatos]
    return pd.DataFrame({
        nome_coluna: values
    })


def drop_word(find_list):
    # Expressao de palavras antecedentes
    key, pix = "(?:CHAVE:?\s?)", "(?:PIX:?\s?)"
    exp_var_pix = rf"{key}|{pix}|{key}{pix}"
    return [re.sub(rf"(?:{exp_var_pix})(?:(?:CPF|CNPJ):?\s?)?", "", j) for j in find_list]


def tokenize(text):
    RE_TOKEN = re.compile(
        r"""([#]?[@\w'’\+\-]*[\w][$]?|[:;<]\-?[\)\(3])""", re.VERBOSE)
    return RE_TOKEN.findall(text)

def nomes_verificacao(nome):
    for idx in range(len(nome)-1, 0, -1):
        for base_nome in base_nomes:
            if len(nome[idx]) >= 4 and nome[idx] in base_nome:
                return ' '.join(nome[:idx+1])
    return


def map(relato, regex):
    enc = re.findall(regex, relato)
    enc_filtrados = list(set(enc))
    value = ', '.join(enc_filtrados)
    return value

def map_btc(relato, regex):
    enc = re.findall(regex, relato)
    value = ', '.join(enc)
    # print(value)
    return value

def map_nomes(relato, regex):
    result_nomes = list(set(regex.finditer(relato)))
    for match in result_nomes:
        if nomes_verificacao(tokenize(match.group(2))):
            value = nomes_verificacao(tokenize(match.group(2)))
            return value


def map_intersection(relato, regex):
    #print(relato)
    tokens_relato = set(tokenize(relato))
    intersections = tokens_relato.intersection(base_nomes)
    value = ', '.join(intersections)
    return value

def map_pix(relato, regex):
    enc = re.findall(regex, relato)
    enc_filtrados = list(set(enc))
    # Remove as palavras antecedentes e deixa só o dado
    enc_filtrados = drop_word(enc)
    value = ', '.join(enc_filtrados)
    return value


def map_monetario(relato, regex):
    enc = re.findall(regex, relato)
    enc_filtrados = [re.sub("(?:DE\s)", "", valor) for valor in enc]
    value = ', '.join(enc_filtrados)
    return value


# def map_imei(relato, regex):
#     result_imei = list(set(regex.finditer(relato)))
#     enc_filtrados = [match.group(2) for match in result_imei]
#     value = ', '.join(enc_filtrados)
#     return value

# New function with new regex
def map_imei(relato, regex):
    result_imei = list(set(re.findall(regex, relato)))
    value = ', '.join(result_imei)
    return value

def map_conta(relato, regex):
    result_contas = list(set(regex.finditer(relato)))
    contas, agencias = [], []

    for match in result_contas:
        # Coloca os grupos de agencias e contas numa lista.
        agencias.append(match.group(2))
        contas.append(match.group(4))
        contas.append(match.group(6))
        agencias.append(match.group(8))
        contas.append(match.group(10))
        agencias.append(match.group(12))

    def formata(ag, cc): return f'ag: {ag} cc: {cc}'
    def filtro(ag, cc): return ag != None or cc != None
    enc_filtrados = [formata(ag, cc) for ag, cc in zip(
        agencias, contas) if filtro(ag, cc)]
    value = ', '.join(enc_filtrados)
    return value

## TESTE
# if __name__=='__main__':
    # getinho = get_columns(r"D:\Samuel\Documents\GitHub\Policia-Civil-Extracao\Relatos\file.xlsx", "DESCRICAOSUMARIA")
    # print(getinho)
    # print(os.path.isfile(path_rel("base_nomes.csv")))
    ## print(f"local arquivo = {local_arquivo}")