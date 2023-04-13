from datetime import datetime, timedelta
from app import db 
from sqlalchemy import func
from app.utils import ellipsize_text

class ProjetoDeLei(db.Model):
    __tablename__ = 'PROJETO_DE_LEI'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    dataPublicacao = db.Column(db.String(255), nullable=False)
    urlProposicao = db.Column(db.String(255), nullable=False)

    @staticmethod
    def add(id, nome, dataPublicacao, urlProposicao):
        projeto = ProjetoDeLei(id=id, nome=nome, dataPublicacao=dataPublicacao, urlProposicao=urlProposicao)
        db.session.add(projeto)
        db.session.commit()
        return projeto

    @classmethod
    def get_last_dataPublicacao(cls):
        projeto = cls.query.order_by(func.STR_TO_DATE(cls.dataPublicacao, '%d/%m/%Y').desc()).first()
        if projeto:
            return projeto.dataPublicacao
        return None

class Proposicao(db.Model):
    __tablename__ = 'PROPOSICAO'
    id = db.Column(db.Integer, primary_key=True)
    nomeAutor = db.Column(db.String(255), nullable=False)
    projetoId = db.Column(db.Integer, db.ForeignKey('PROJETO_DE_LEI.id'), nullable=False)
    accepted = db.Column(db.Boolean, default=False)
    projeto = db.relationship('ProjetoDeLei', backref='proposicoes')

    @staticmethod
    def add(nomeAutor, projetoId):
        proposicao = Proposicao(nomeAutor=nomeAutor, projetoId=projetoId)
        db.session.add(proposicao)
        db.session.commit()
        return proposicao

    def get_proposal_summary_by_id(id):
        query = (db.session.query(
                    db.func.concat(ProjetoDeLei.id).label('id'),
                    ProjetoDeLei.nome.label('nomeLei'),
                    ProjetoDeLei.dataPublicacao,
                    Proposicao.nomeAutor,
                    ProjetoDeLeiResumo.resumoTitulo,
                    ProjetoDeLeiResumo.resumoProjeto
                )
                .join(Proposicao, ProjetoDeLei.id == Proposicao.projetoId)
                .join(ProjetoDeLeiResumo, ProjetoDeLei.id == ProjetoDeLeiResumo.projetoId)
                .filter(ProjetoDeLei.id == id))

        proposal = query.first()._asdict()

        return query.first()

    def get_all_proposal_summary():
        proposals = Proposicao.query.join(ProjetoDeLei).join(ProjetoDeLeiResumo).with_entities(
            ProjetoDeLei.id.label('id'),
            ProjetoDeLei.nome.label('nomeLei'),
            ProjetoDeLei.dataPublicacao,
            Proposicao.nomeAutor,
            ProjetoDeLeiResumo.resumoTitulo,
            ProjetoDeLeiResumo.resumoProjeto
        ).order_by(func.STR_TO_DATE(ProjetoDeLei.dataPublicacao, '%d/%m/%Y').desc()).all()
        return [proposal._asdict() for proposal in proposals]

    def get_all_proposal_summary_paginated(page=1, per_page=10):
        page = Proposicao.query.join(ProjetoDeLei).join(ProjetoDeLeiResumo).with_entities(
            ProjetoDeLei.id.label('id'),
            ProjetoDeLei.nome.label('nomeLei'),
            ProjetoDeLei.dataPublicacao,
            Proposicao.nomeAutor,
            ProjetoDeLeiResumo.resumoTitulo,
            ProjetoDeLeiResumo.resumoProjeto
        ).order_by(func.STR_TO_DATE(ProjetoDeLei.dataPublicacao, '%d/%m/%Y').desc()).paginate(page=page, per_page=per_page, count=True)

        proposals = [{
            'id': proposal.id,
            'nomeLei': proposal.nomeLei,
            'dataPublicacao': proposal.dataPublicacao,
            'nomeAutor': proposal.nomeAutor,
            'resumoTitulo': proposal.resumoTitulo,
            'resumoProjeto': ellipsize_text(proposal.resumoProjeto, 35) 
        } for proposal in page.items]

        return {
            'proposals': proposals,
            'pagination': page
        }

class ProjetoDeLeiResumo(db.Model):
    __tablename__ = 'PROJETO_DE_LEI_RESUMO'
    id = db.Column(db.Integer, primary_key=True)
    resumoProjeto = db.Column(db.Text, nullable=False)
    dataPublicacaoAdicionada = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)
    projetoId = db.Column(db.Integer, db.ForeignKey('PROJETO_DE_LEI.id'), nullable=False)
    resumoTitulo = db.Column(db.String(255))
    projeto = db.relationship('ProjetoDeLei', backref='resumos')

    @staticmethod
    def add(resumoProjeto, projetoId, resumoTitulo=None):
        resumo = ProjetoDeLeiResumo(resumoProjeto=resumoProjeto, projetoId=projetoId, resumoTitulo=resumoTitulo)
        db.session.add(resumo)
        db.session.commit()
        return resumo

    def get_latest_resumos():
        today = datetime.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today + timedelta(days=1), datetime.min.time())
        print(start_of_day, end_of_day)
        latest_resumos = ProjetoDeLeiResumo.query.filter(
            ProjetoDeLeiResumo.dataPublicacaoAdicionada >= start_of_day,
            ProjetoDeLeiResumo.dataPublicacaoAdicionada < end_of_day
        ).order_by(
            ProjetoDeLeiResumo.dataPublicacaoAdicionada.desc()
        ).limit(5).all()
        return latest_resumos