import logging
import os

from app import create_app

from scrapper.proposal_list import scrap_current_proposals
from scrapper.proposal import scrap_new_law_proposal

from app.models import ProjetoDeLei, ProjetoDeLeiResumo, Proposicao

log = logging.getLogger(__name__)


create_app().app_context().push()

def success_scrapping(value):
    env_file = os.getenv('GITHUB_ENV')

    with open(env_file, "a") as myfile:
        myfile.write(f"SUCCESS_SCRAPPING={value}")

def find_new_proposals(proposals, last_proposal_date):
    log.info('Searching for new proposals...')

    new_proposals = [proposal for proposal in proposals if proposal['Data da publicação'] > last_proposal_date]

    qntd_proposals = len(new_proposals)
    new_proposals_msg = 'No new proposals found!'
    success_status = 'false'

    if qntd_proposals > 0:
        success_status = 'true'
        new_proposals_msg = f'New proposal{"s" if qntd_proposals > 1 else ""} found!'

        if qntd_proposals > 50:
            new_proposals_msg += '\nMore than 50 proposals found!\nGoing to third page...'
            new_proposals.extend(scrap_current_proposals(3))
        elif qntd_proposals > 25:
            new_proposals_msg += '\nMore than 25 proposals found!\nGoing to second page...'
            new_proposals.extend(scrap_current_proposals(2))

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
    last_proposal_date = ProjetoDeLei.get_last_dataPublicacao()

    new_proposals = find_new_proposals(proposals, last_proposal_date)

    proccess_new_proposals(new_proposals)

if __name__ == '__main__':
    main()