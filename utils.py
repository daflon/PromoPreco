import re
from rapidfuzz import fuzz, process

def validar_cnpj(cnpj):
    if not cnpj:
        return True
    cnpj = re.sub(r'\D', '', cnpj)
    return len(cnpj) == 14 and cnpj.isdigit()

def validar_ean(ean):
    if not ean:
        return True
    ean = re.sub(r'\D', '', ean)
    return len(ean) == 13 and ean.isdigit()

def sanitizar_busca(termo):
    if not termo:
        return ''
    termo_limpo = re.sub(r'[^\w\s\u00C0-\u017F]', '', termo)
    return termo_limpo.strip()[:100]

def busca_fuzzy(termo, opcoes, limite=5):
    if not termo or not opcoes:
        return []
    matches = process.extract(termo, opcoes, limit=limite, scorer=fuzz.partial_ratio)
    return [match[0] for match in matches if match[1] >= 60]