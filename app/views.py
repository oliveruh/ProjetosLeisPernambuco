from flask import jsonify, render_template, Blueprint, make_response, request
from app.models import Proposicao
from datetime import datetime

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

def generate_static_urls():
    # Static routes with static content
    static_urls = list()
    index = {
        "loc": f"https://projetoslei.org.pe/",
        "lastmod": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "priority": "1.0"
    }
    json = {
        "loc": f"https://projetoslei.org.pe/todos_projetos_de_lei.json",
        "lastmod": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "priority": "0.6"
    }
    static_urls.append(index)
    static_urls.append(json)

    return static_urls

def generate_dynamic_urls():
    # Dynamic routes with dynamic content
    dynamic_urls = list()
    proposals = Proposicao.get_all_proposal_summary()
    for proposal in proposals:
        url = {
            "loc": f"https://projetoslei.org.pe/projeto-de-lei/{proposal['id']}.html",
            "lastmod": datetime.strptime(proposal['dataPublicacao'], '%d/%m/%Y').strftime("%Y-%m-%dT%H:%M:%SZ"),
            "priority": "0.80"
            }
        dynamic_urls.append(url)

    for page in range(1, Proposicao.get_all_proposal_summary_paginated()['pagination'].pages + 1):
        url = {
            "loc": f"https://projetoslei.org.pe/p/{page}.html",
            "lastmod": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "priority": "0.80"
            }
        dynamic_urls.append(url)

    return dynamic_urls

@app.route("/sitemap.xml")
def sitemap():
    
    static_urls = generate_static_urls()
    dynamic_urls = generate_dynamic_urls()

    xml_sitemap = render_template("sitemap.xml", static_urls=static_urls, dynamic_urls=dynamic_urls)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"

    return response

@app.route('/robots.txt')
def robots():
    return render_template('robots.txt')