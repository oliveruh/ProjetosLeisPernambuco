import requests
from bs4 import BeautifulSoup
import logging

# Setting up logging
logging.basicConfig(level=logging.NOTSET)
log = logging.getLogger(__name__)


def scrap_proposal_list(page):
    url = "http://www.alepe.pe.gov.br/proposicoes"

    payload={'pagina': str(page),
    'field-tipo-filtro': 'projetos',
    'field-proposicoes-filtro': 'numero',
    'field-proposicoes': '',
    'field-proposicoes2': '',
    'field-comissoes': '',
    'field-autores': '',
    'field-palavrachave': '',
    'field-filter-data-proposicoes': ''}


    return requests.request("POST", url, data=payload)

def parse_data(response):
    soup = BeautifulSoup(response.content, "html.parser")
    proposicao_list = soup.find("div", class_="proposicao-list")
    
    return proposicao_list.find("table")

def scrap_current_proposals(page=1):

    log.info("Scraping current propositions...")
    response = scrap_proposal_list(page)

    log.info("Parseando tabela...")
    table = parse_data(response)

    table_data = []
    headers = ['Id'] + [header.text for header in table.find_all("th")] + ['Link'] 
    for row in table.find_all("tr")[1:]:
        row_data = [data['href'].replace('=', '&').split('&')[1] for data in row.find_all("td")[1]] + [data.text for data in row.find_all("td")] + ['http://www.alepe.pe.gov.br' + data['href'] for data in row.find_all("td")[1]] 
        table_data.append(dict(zip(headers, row_data)))

    log.info("Returning data...")
    return table_data

