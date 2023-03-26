from flask import jsonify, render_template, Blueprint
from app.models import Proposicao

app = Blueprint('app', __name__)

@app.route('/')
def index():
    page = Proposicao.get_all_proposal_summary_paginated()
    return render_template('law_proposal_list.html', proposals=page['proposals'], pagination=page['pagination'], current_page=1)

@app.route('/p/<int:num_page>.html')
def page(num_page):
    page = Proposicao.get_all_proposal_summary_paginated(num_page)
    return render_template('law_proposal_list.html', proposals=page['proposals'], pagination=page['pagination'], current_page=num_page)

@app.route('/projeto-de-lei/<int:id>.html')
def proposal(id):
    proposal = Proposicao.get_proposal_summary_by_id(id)
    return render_template('law_proposal.html', proposal=proposal)

@app.route('/todos_projetos_de_lei.json')
def json_all_proposals():
    proposals = Proposicao.get_all_proposal_summary()
    return jsonify(proposals)

@app.route('/error.html')
def error():
    return render_template('error.html')