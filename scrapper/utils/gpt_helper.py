import openai

def ask_gpt_3_to_explain_law(textoLei, justificativa):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": """Você é um sistema que analisa projetos de leis criados por parlamentares do legislativo estadual 
                                                pernambucano enviados para análise e escreve um resumo de cunho jornalístico e informativo da lei para
                                                o entendimento da população geral, com palavras simplificadas e linguagem objetiva para o entendimento
                                                de todos. Você retorna sempre dois campos no formato JSON: TITULO (sempre em caixa-alta) e RESUMO. 
                                                Não use o nome ou data da lei no resumo e nem no titulo. """},
                {"role": "user", "content": "TEXTO LEI: " + textoLei + " JUSTIFICATIVA: " + justificativa + "---- \n Obs. Retorne em um JSON;\n Não utilize o nome da lei ou algo do tipo 'Lei XX' no titulo e nem no resumo, você tem de ser informativo;\n Trate o conteúdo como um projeto, passível ou não de aprovação no plenário, então evite utilizar frases que sugiram que a lei já está em efetivação."}
        ],
        max_tokens=800
    )