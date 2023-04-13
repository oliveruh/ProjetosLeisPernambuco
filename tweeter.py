from app import create_app
import requests
import json

from app.models import ProjetoDeLeiResumo

# Setting up app context
app = create_app()
create_app().app_context().push()

url = "https://api.twitter.com/2/tweets"

CONSUMER_KEY = app.config['CONSUMER_KEY']
ACCESS_TOKEN = app.config['ACCESS_TOKEN']
OAUTH_NONCE = app.config['OAUTH_NONCE']
OAUTH_SIGNATURE = app.config['OAUTH_SIGNATURE']

def post_tweet(title, link):

    payload = {
        "text": f'{ title }\n\n{ link }'
    }

    payload = json.dumps(payload)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'OAuth oauth_consumer_key="{ CONSUMER_KEY }",oauth_token="{ ACCESS_TOKEN }",oauth_signature_method="HMAC-SHA1",oauth_timestamp="1681351384",oauth_nonce="{ OAUTH_NONCE }",oauth_version="1.0",oauth_signature="{ OAUTH_SIGNATURE }"'
    }

    requests.request("POST", url, headers=headers, data=payload)

def tweet_new_law_proposals():
    latest_resumos = ProjetoDeLeiResumo.get_latest_resumos()

    print('Latest resumos: ')
    print(latest_resumos)

    for proposal in latest_resumos:
        title = proposal.resumoTitulo
        link = f'https://projetoslei.org.pe/projeto-de-lei/{ proposal.projetoId }.html'
        post_tweet(title, link)


if __name__ == '__main__':
    tweet_new_law_proposals()