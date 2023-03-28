from app import create_app
from scrapper.proposal_list import scrap_current_proposals
from scrapper.proposal import scrap_new_law_proposal
from app.models import ProjetoDeLei
from app.models import Proposicao
from app.models import ProjetoDeLeiResumo
import os

create_app().app_context().push()

def success_scrapping(value):
    env_file = os.getenv('GITHUB_ENV')

    with open(env_file, "a") as myfile:
        myfile.write(f"SUCCESS_SCRAPPING={value}")

proposals = scrap_current_proposals()
last_proposal_date = ProjetoDeLei.get_last_dataPublicacao()

print('Searching for new proposals...')

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
print(new_proposals_msg)

for i in range(len(new_proposals)):
    try:
        resumo = scrap_new_law_proposal(new_proposals[i], i)
    except Exception as e:
        print(e)
        print('DEU ERRO!')
        continue
    ProjetoDeLei.add(new_proposals[i]['Id'], new_proposals[i]['Proposição'], new_proposals[i]['Data da publicação'], new_proposals[i]['Link'])
    Proposicao.add(new_proposals[i]['Autor'], new_proposals[i]['Id'])
    ProjetoDeLeiResumo.add(resumo['RESUMO'], new_proposals[i]['Id'], resumo['TITULO'])

print('Finishing adding proposals to database!')



