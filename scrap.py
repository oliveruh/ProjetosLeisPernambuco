import logging
import time
import os

from app import create_app

from scrapper.proposal_list import scrap_current_proposals
from scrapper.proposal import scrap_new_law_proposal

from app.models import ProjetoDeLei, ProjetoDeLeiResumo, Proposicao

# Setting up logging
logging.basicConfig(level=logging.NOTSET)
log = logging.getLogger(__name__)

# Setting up app context
create_app().app_context().push()


def success_scrapping(value):
    env_file = os.getenv('GITHUB_ENV')

    with open(env_file, "a") as myfile:
        myfile.write(f"SUCCESS_SCRAPPING={value}")

def find_new_proposals(proposals, last_proposal_date, page=1):
    log.info('Searching for new proposals...')

    new_proposals = [proposal for proposal in proposals if time.strptime(proposal['Data da publicação'], "%d/%m/%Y") > last_proposal_date]

    qntd_proposals = len(new_proposals)
    new_proposals_msg = 'No new proposals found!'
    success_status = 'false'

    if qntd_proposals > 0:
        success_status = 'true'
        new_proposals_msg = f'New proposal{"s" if qntd_proposals > 1 else ""} found!'

        if qntd_proposals >= 25:
            new_page = page + 1
            new_proposals_msg += f'\nMore than 25 proposals found!\nGoing to page {str(new_page)}...'
            new_proposals.extend(find_new_proposals(scrap_current_proposals(new_page), last_proposal_date, new_page))

    success_scrapping(success_status)
    log.info(new_proposals_msg)

    return new_proposals

def proccess_new_proposals(new_proposals):
    log.info('Proccessing new proposals...')

    for index, proposal in enumerate(new_proposals):
        try:
            resumo = scrap_new_law_proposal(proposal, index)
        except Exception as e:
            log.error(e)
            log.error('Error occurred!')
            continue

        ProjetoDeLei.add(proposal['Id'], proposal['Proposição'], proposal['Data da publicação'], proposal['Link'])
        Proposicao.add(proposal['Autor'], proposal['Id'])
        ProjetoDeLeiResumo.add(resumo['RESUMO'], proposal['Id'], resumo['TITULO'])

    log.info('Finished adding proposals to database!')

def main():
    proposals = scrap_current_proposals()
    last_proposal_date = time.strptime(ProjetoDeLei.get_last_dataPublicacao(), "%d/%m/%Y")

    new_proposals = find_new_proposals(proposals, last_proposal_date)

    proccess_new_proposals(new_proposals)

if __name__ == '__main__':
    main()