from app import create_app
from scrapper.proposal_list import scrap_current_proposals
from scrapper.proposal import scrap_new_law_proposal
from app.models import ProjetoDeLei
from app.models import Proposicao
from app.models import ProjetoDeLeiResumo

create_app().app_context().push()

proposals = scrap_current_proposals()
last_proposal_date = ProjetoDeLei.get_last_dataPublicacao()

print('Searching for new proposals...')

qntd_proposals = 0
new_proposals = []
for i in range(len(proposals)):
    if proposals[i]['Data da publicação'] > last_proposal_date:
        qntd_proposals += 1
        proposals.append(proposals[i])

if qntd_proposals == 1:
    print('New proposal found!')
elif (qntd_proposals > 1):
    print('New proposals found!')
elif (qntd_proposals > 25):
    print('More than 25 proposals found!')
    print('Going to second page...')
    proposals.append(scrap_current_proposals(2))
elif (qntd_proposals > 50):
    print('More than 50 proposals found!')
    print('Going to third page...')
    proposals.append(scrap_current_proposals(3))
else:
    print('No new proposals found!')

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



