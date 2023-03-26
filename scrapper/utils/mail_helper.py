from app import create_app
import yagmail

app = create_app()

smtp_server = app.config['EMAIL_HOST']
smtp_port = app.config['EMAIL_PORT']
sender_email = app.config['SENDER_EMAIL_USERNAME']
sender_password = app.config['SENDER_EMAIL_PASSWORD']
receiver_email = app.config['RECEIVER_EMAIL']

def send_email(subject, message):
    print("Enviando e-mail com log de erro...")

    yag = yagmail.SMTP(sender_email, sender_password)

    subject = "ERRO no Law-Logger: " + subject
    contents = 'Um erro ocorreu ao fazer o scrapping dos projetos de lei do dia. \n\n' + message

    yag.send(to=receiver_email, subject=subject, contents=contents)

def get_erro_subject(erroType):
    match erroType:
        case 'textoGrande':
            return 'Texto da lei muito grande.'
        case 'erroGPT3':
            return 'Erro na requisição para o GPT-3.'
        case 'jsonInvalido':
            return 'GPT-3 não retornou um JSON válido.'

def get_erro_message(erroType, proposal, proposalIndex, resumoLei=''):
    match erroType:
        case 'textoGrande':
            return f"""Texto da lei muito grande, não foi possível persistir a proposta {proposal['Proposição']}. 
                    \n Proposta de Id: {proposal['Id']}.
                    \n Lugar da proposta na fila: {str(proposalIndex)}.
                    """
        case 'erroGPT3':
            return f"""Erro na requisição para o GPT-3, não foi possível persistir a proposta {proposal['Proposição']}. 
                    \n Proposta de Id: {proposal['Id']}.
                    \n Lugar da proposta na fila: {str(proposalIndex)}.
                    """
        case 'jsonInvalido':
            return f"""GPT-3 não retornou um JSON válido, não foi possível persistir a proposta {proposal['Proposição']}. 
                    \n Proposta de Id: {proposal['Id']}.
                    \n Lugar da proposta na fila: {str(proposalIndex)}.
                    \n\n Resposta do GPT-3: {resumoLei} \n
                    """