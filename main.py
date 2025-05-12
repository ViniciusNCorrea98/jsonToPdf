from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, AgendaDisparos
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependência de sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def gerar_grafico_status(dados, path_img):
    status_counts = {}
    for item in dados:
        status = item.status or "Desconhecido"
        status_counts[status] = status_counts.get(status, 0) + 1

    plt.figure(figsize=(8, 5))
    plt.bar(status_counts.keys(), status_counts.values(), color='royalblue')
    plt.title("Distribuição de Status dos Disparos")
    plt.xlabel("Status")
    plt.ylabel("Quantidade")
    plt.tight_layout()
    plt.savefig(path_img)
    plt.close()

def gerar_pdf(path_pdf, path_img):
    c = canvas.Canvas(path_pdf)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Relatório de Disparos - Análise Completa")
    if os.path.exists(path_img):
        c.drawImage(path_img, 100, 470, width=400, height=300)
    else:
        c.setFont("Helvetica", 12)
        c.drawString(100, 470, "Gráfico não disponível.")
    c.showPage()
    c.save()

@app.get("/disparador")
def get_disparador(page: int = Query(1), limit: int = Query(10), db: Session = Depends(get_db)):
    offset = (page - 1) * limit

    # Dados paginados para resposta
    dados_pagina = db.query(AgendaDisparos).offset(offset).limit(limit).all()
    total = db.query(AgendaDisparos).count()
    total_pages = -(-total // limit)

    # Coleta de todos os dados para gerar análise completa
    dados_analise = db.query(AgendaDisparos).all()

    # Geração de gráfico e relatório
    path_img = "grafico_status.png"
    path_pdf = "relatorio_disparador.pdf"
    gerar_grafico_status(dados_analise, path_img)
    gerar_pdf(path_pdf, path_img)

    return {
        "data": [item.__dict__ for item in dados_pagina],
        "pagination": {
            "currentPage": page,
            "totalPages": total_pages,
            "totalCount": total
        },
        "pdf_path": path_pdf
    }

@app.get("/download-pdf")
def download_pdf():
    return FileResponse("relatorio_disparador.pdf", media_type='application/pdf', filename="relatorio_disparador.pdf")
