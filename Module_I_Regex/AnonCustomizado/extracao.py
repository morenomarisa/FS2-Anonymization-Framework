import pandas as pd
import re
import util
import os
import pathlib

# RETORNA O PATH DO ARQUIVO (arg: arquivo [str] = nome do arquivo) NA PASTA names_apps_banks
#path_rel = lambda arquivo: os.path.realpath(r"./names_apps_banks/" + arquivo)
# def path_rel(arquivo):
#     return str(pathlib.Path.joinpath(pathlib.Path(
#         __file__).parent.resolve(),  "names_apps_banks", arquivo)) #

# ======================================================
# PATHS ESTÁVEIS: sempre relativos ao próprio arquivo
# ======================================================
BASE_HERE = os.path.dirname(os.path.realpath(__file__))

def path_rel(arquivo: str) -> str:
    """
    Retorna o caminho absoluto de um arquivo dentro de:
    <pasta_do_extracao.py>/names_apps_banks/<arquivo>
    """
    return os.path.join(BASE_HERE, "names_apps_banks", arquivo)

def path_base_nome(x: str) -> str:
    return path_rel(x)

## TESTE
# if __name__ == '__main__':
#     pprint = path_rel("nomes_aplicativos.csv")
#     print(os.path.isfile(pprint), pprint, sep="\n")

def aplicativos(relatos):

    # LISTA DE APLICATIVOS
    aplicativos = util.get_columns(
        path_rel("nomes_aplicativos.csv"), "APLICATIVOS")[1]
    # Concatena cada iterator com '|'
    exp_apps = "|".join(aplicativos)
    # Cria a expressão regular
    regex = re.compile(exp_apps)
    return util.get_data_frame(relatos, regex, "APLICATIVOS", util.map)


def bancos(relatos):

    # LISTA DE BANCOS
    bancos = util.get_columns(
        path_rel("nomes_bancos.csv"), "BANCOS")[1]
    exp_bancos = "|".join(bancos)
    regex = re.compile(exp_bancos)
    return util.get_data_frame(relatos, regex, "BANCO", util.map)


# def nomes(relatos):

#     prefixo_nomes = util.get_columns(
#         path_rel("prefixos_nomes.csv"), "PREFIXOS NOME")[1]
#     # Concatena cada iterator com '|'
#     exp_prefixo = "|".join(prefixo_nomes)
#     exp_sufixo = '(?:[^a-zA-Z]+[a-zA-Z]+){0,5}'
#     # Cria a expressão regular
#     regex = re.compile(rf'({exp_prefixo})({exp_sufixo})')
#     return util.get_data_frame(relatos, regex, "NOMES", util.map_nomes)

def path_base_nome(x): return os.path.realpath(r"./names_apps_banks/" + x)




def nomes(relato):
    print(relato)
    # intersections = util.map_intersection(relato)
    # patterns = list(intersections)
    # sep = "\\b|\\b"

    #regex = re.compile(rf'(?:\b{sep.join(map(re.escape, patterns))}\b)')
    regex = re.compile(rf'.*')
    # print(regex)
    return util.get_data_frame(relato, regex, "NOMES", util.map_intersection)
      


def chavepix(relatos):

    # Expressao de e-mail
    #exp_email = r"[0-9A-z]+[.-]?[0-9A-z]*@[0-9A-z]+[.-]?[0-9A-z]+[.-]?[0-9A-z]*"
    exp_email = r"[A-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:[.][A-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?[.])+[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?"
    # Expressao de Chave aleatoria
    exp_random = r"[A-Z0-9]{8}-(?:[A-Z0-9]{4}-){3}[A-Z0-9]{12}"
    # Expressao de CPF e CNPJ
    exp_CPF = r"(?:[0-9]{2}[.]?[0-9]{3}[.]?[0-9]{3}[/][0-9]{4}[-][0-9]{2})|(?:[0-9]{3}[.][0-9]{3}[.][0-9]{3}[-][0-9]{2})"
    # Mini-Expressao de numero de telefone
    exp_number = r"(?:[0-9]{9,11})"
    # Expressao de palavras antecedentes
    #key, pix = "(?:CHAVE:?\s?)", "(?:PIX:?\s?)"
    key, pix = (r"(?:CHAVE:?\s?)", r"(?:PIX:?\s?)")

    exp_var_pix = rf"{key}|{pix}|{key}{pix}"

    # Expressao PRINCIPAL que concatena todas as outras expressoes acima
    regex = re.compile(
        rf"(?:{exp_var_pix}(?:ALEATORIA:?\s?)?)(?:{exp_email}|(?:{exp_number})|(?:{exp_random})|(?:(?:CPF|CNPJ):?\s?)(?:{exp_CPF}))")
    return util.get_data_frame(relatos, regex, "CHAVEPIX", util.map_pix)


def email(relatos):
    # Regex email
    #regex = re.compile(r"(?:\w+[\.\-\_]?[\w]*@[\w]+[\.\-]?(?:[\.\-]?[\w])*)")
    regex = r"[A-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:[.][A-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?[.])+[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?"
    return util.get_data_frame(relatos, regex, "EMAIL", util.map)


def endereco(relatos):
    prefixo_endereco = util.get_columns(
        path_rel("prefixos_enderecos.csv"), "PREFIXOS ENDERECO")[1]
    exp_prefixo = "|".join(prefixo_endereco)
    #exp_endereco = 'CEP[: ]*[\d]{5}-?[\d]{3}'
    exp_endereco = r'CEP[: ]*[\d]{5}-?[\d]{3}'

    # Regex endereço, pega de Rua, Travessa, Avenida, Passagem até CEP.
    regex = re.compile(rf"((?:{exp_prefixo}).+?(?:{exp_endereco}))")
    return util.get_data_frame(relatos, regex, "ENDERECO", util.map)


def valormonetario(relatos):

    # REGEX DE VALOR MONETARIO
    regex = re.compile(
        r"(?:(?:DE\s)\d{1,3}(?:,|\.?\d{3})*(?:,\d{2}))|(?:R?[$]\s?\d{1,3}(?:,|\.?\d{3})*(?:(?:,|\.)?\d+))")
    return util.get_data_frame(relatos, regex, "R$", util.map_monetario)


def url(relatos):

    # Regex url
    regex = re.compile(
        r"((?:HTTPS?|WWW)(?:\:\/\/?)?[a-zA-Z0-9\.\/\?\:@\-_=#]+[\.][a-zA-Z]{2,6}[a-zA-Z0-9\.\&\/\?\:@\-_=#]*)")
    return util.get_data_frame(relatos, regex, "URL", util.map)


def cpf_cnpj_old(relatos):
    # Regex original
    regex = re.compile(
        r'(?:[\d]{2}[.]?(?:[\d]{3}[.]?){2}[/]?[\d]{4}[-]?[\d]{2})|'
        r'(?:(?:[\d]{3}[.]?){2}[\d]{3}[-]?[\d]{2})|'
        r'(?:[*]{3}[.][\d]{3}[.][\d]{3}[.]?[-][*]{2})'
    )
    return util.get_data_frame(relatos, regex, "CPF/CNPJ", util.map)


def cpf_cnpj_new(relatos):
    # Regex refinada: aceita espaços, "." no lugar de "/" no CNPJ e "." no lugar de "-" no CPF
    regex = re.compile(
        r'(?<!\d)('
        r'(?:\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\.\s]?\d{4}[-\s]?\d{2})'  # CNPJ pontuado (aceita / ou .)
        r'|(?:\d{14})'                                             # CNPJ só dígitos
        r'|(?:\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\.\s]?\d{2})'           # CPF pontuado (aceita - ou .)
        r'|(?:\d{11})'                                             # CPF só dígitos
        r'|(?:\*{3}[.\s]?\d{3}[.\s]?\d{3}[-\.\s]?\*{2})'           # CPF mascarado (opcional)
        r')(?!\d)'
    )
    return util.get_data_frame(relatos, regex, "CPF/CNPJ", util.map)




def imei(relatos):

    # Regex de Imei (old)
    # regex = re.compile(r"(IMEI[\s:12]*([\d]{15,16}))")

    # New Regex
    #regex = re.compile(r"(?#IMEI[\s:12]*)\d{15,16}")
    regex = re.compile(r"(IMEI[\s:12]*([\d]{15,16}))")
    return util.get_data_frame(relatos, regex, "IMEI", util.map_imei)


#def conta(relatos):

    #regex_agencia = r'(?:(AGENCIA|AG|AGENCIA DESTINO)[ :]*([0-9]{1,5}[\/-]?[0-9]{0,2}))'
    #regex_conta = r'(?:(CONTA|CONTA CORRENTE|C/?C|CONTA CORRENTE PJ|CONTA DESTINO|CONTA CORRENTE N°)[ ,:]*([0-9]+(?:[-.]?[0-9])+))'

    #regex = re.compile(
        #rf'(?:{regex_agencia}).*?(?:{regex_conta})|(?:{regex_conta}).*?(?:{regex_agencia})|(?:{regex_conta})|(?:{regex_agencia})',
        #re.IGNORECASE
    #)

    #return util.get_data_frame(relatos, regex, "AGENCIA E CONTA", util.map_conta)


# No seu extracao.py:
def conta(relatos):
    # Aceita dígitos, hífens, pontos e o X (maiúsculo ou minúsculo)
    regex_agencia = r'(?:(AGENCIA|AG|AGENCIA DESTINO)[ :]*([0-9]{1,5}[-.]?[0-9xX]?))'
    
    # Melhora a captura da conta para aceitar o X no dígito final
    regex_conta = r'(?:(CONTA|C/?C|CONTA CORRENTE)[ ,:]*([0-9]{2,}(?:[-.]?[0-9xX])+))'

    regex = re.compile(
        rf'(?:{regex_agencia}).*?(?:{regex_conta})|(?:{regex_conta}).*?(?:{regex_agencia})|(?:{regex_conta})|(?:{regex_agencia})',
        re.IGNORECASE
    )
    return util.get_data_frame(relatos, regex, "AGENCIA E CONTA", util.map_conta)

#def telefone(relatos):
#    regex = re.compile(
#         r"(?:\+\d\d\s)?\(?[\d]{2}\)?\s\d?\s?[\d]{4}[-][\d]{4}|(?:\+\d\d\s)[\d]{2}\s[\d]{4}\s?[\d]{4}")
#    return util.get_data_frame(relatos, regex, "TELEFONE", util.map)

#def telefone(relatos):

#regex = re.compile(

#r'(?<!\d)' # não pode ter dígito antes

#r'(?:\+?\d{1,3}\s*)?' # +55, 55, +351 etc (opcional)

#r'(?:\(?\d{2}\)?\s*)?' # DDD (opcional)

#r'(?:9\s*)?\d{4}\s*[-.\s]?\s*\d{4}' # 8/9 dígitos (celular pode ter 9)

#r'(?!\d)' # não pode ter dígito depois
#)

#return util.get_data_frame(relatos, regex, "TELEFONE", util.map)

def telefone(relatos):
    regex = re.compile(
        r'(?i)'                                      # Case-insensitive
        r'(?:tel(?:efone)?|cel(?:ular)?|contato)?'    # Âncoras opcionais (tel, cel, etc)
        r'[\s:]*'                                    # Espaços ou dois pontos
        r'(?<!\d)'                                   # Garantia: sem dígito colado antes
        r'(?:'
            r'(?:\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4})'   # Formato com DDD: (11) 98765-4321
            r'|'
            r'(?:\d{4,5}[-\s]\d{4})'                 # Formato sem DDD, mas OBRIGA hífen ou espaço
        r')'
        r'(?!\d)'                                    # Garantia: sem dígito colado depois
    )
    return util.get_data_frame(relatos, regex, "TELEFONE", util.map)

def endereco_btc(relatos):
    regex = re.compile(
        r"BC1[A-Z0-9]{39}|[13][A-Z0-9]{33}")
    return util.get_data_frame(relatos, regex, "ENDEREÇO BITCOIN", util.map_btc)

def run(local_arquivo, nome_coluna_relatos):
    try:
        df, relatos = util.get_columns(local_arquivo, nome_coluna_relatos)
    except Exception as error:
        return error
    dfs = [
        df,
        nomes(relatos), #ok
        #aplicativos(relatos),
        #bancos(relatos),
        #chavepix(relatos),
        email(relatos), #ok
        #endereco(relatos),
        #valormonetario(relatos),
        #url(relatos),
        cpf_cnpj(relatos), #ok
        #imei(relatos), #ok
        conta(relatos), #ok
        telefone(relatos),
        #endereco_btc(relatos)
    ]
    return pd.concat(dfs, axis=1)
