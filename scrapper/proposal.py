from bs4 import BeautifulSoup
import requests
import json
import string
from scrapper.utils.gpt_helper import ask_gpt_3_to_explain_law
from scrapper.utils.json_helper import validateJSON
from scrapper.utils.mail_helper import get_erro_message, get_erro_subject, send_email


def scrapping_alepe(url):
    projetoResponse = requests.get(url)
    return BeautifulSoup(projetoResponse.content, "html.parser")

def parse_data_texto_lei(projetoSoup):
    textoLeiEl = projetoSoup.find_all("div", class_="proposicao-list-item-text")
    textoLei = ''
    for i in textoLeiEl[0].find_all("p"):
        textoLei += i.text + "\n"
    return textoLei, textoLeiEl[1].text

def scrap_new_law_proposal(proposal, proposalIndex):

    print("Scraping " + proposal['Proposição'] + "...")
    projetoSoup = scrapping_alepe(proposal['Link'])

    print("Parsing data...")
    textoLei, justificativa = parse_data_texto_lei(projetoSoup)

    # Cheking text size
    textAll = textoLei + justificativa
    allWords = sum([i.strip(string.punctuation).isalpha() for i in textAll.split()]) 

    if allWords > 1500:
        send_email(get_erro_subject('textoGrande'), get_erro_message('textoGrande', proposal, proposalIndex))
        raise Exception("Texto muito grande, não foi possível persistir a proposta " + proposal['Proposição'])

    print("Enviando para o GPT-3...")
    resumoLei = []
    try:
        resumoLei = ask_gpt_3_to_explain_law(textoLei, justificativa)
    except Exception as e:
        send_email(get_erro_subject('erroGPT3'), get_erro_message('erroGPT3', proposal, proposalIndex))
        print("Erro no GPT-3: \n")
        return e

    if validateJSON(resumoLei['choices'][0]['message']['content']):
        print("Resposta do GPT-3: " + str(resumoLei))
        return {
            "TITULO": json.loads(resumoLei['choices'][0]['message']['content'])['TITULO'].upper(),
            "RESUMO": json.loads(resumoLei['choices'][0]['message']['content'])['RESUMO']
        }
    else:
        send_email(get_erro_subject('jsonInvalido'), get_erro_message('jsonInvalido', proposal, proposalIndex, resumoLei))
        raise Exception("GPT-3 não retornou JSON válido: " + str(resumoLei))


