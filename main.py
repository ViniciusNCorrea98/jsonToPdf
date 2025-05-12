from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from models import Base, AgendaDisparos
from fastapi.responses import FileResponse
from collections import defaultdict
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib.pyplot as plt
import os
import platform
import subprocess

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def abrir_imagem(path):
    print(f"Imagem gerada: {path}")
    if os.path.exists(path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

def gerar_grafico_status(dados, path_img):
    status_counts = {}
    for item in dados:
        status = item.status or "Desconhecido"
        status_counts[status] = status_counts.get(status, 0) + 1

    labels = list(status_counts.keys())
    values = list(status_counts.values())

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color='royalblue')
    plt.title("Distribuição de Status dos Disparos")
    plt.xlabel("Status")
    plt.ylabel("Quantidade")

    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(path_img)
    plt.close()
    abrir_imagem(path_img)

def gerar_grafico_midias(dados, path_img):
    midia_counts = {"imagem": 0, "audio": 0, "video": 0, "texto": 0}
    for item in dados:
        if item.imagem:
            midia_counts["imagem"] += 1
        elif item.audio:
            midia_counts["audio"] += 1
        elif item.video:
            midia_counts["video"] += 1
        else:
            midia_counts["texto"] += 1

    labels = list(midia_counts.keys())
    values = list(midia_counts.values())

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color='darkgreen')
    plt.title("Tipos de Conteúdo Enviado")
    plt.xlabel("Tipo")
    plt.ylabel("Quantidade")

    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(path_img)
    plt.close()
    abrir_imagem(path_img)


def gerar_grafico_colaboradores(dados, path_img):
    colaboradores = {}
    for item in dados:
        nome = item.nome_colaborador or "Desconhecido"
        colaboradores[nome] = colaboradores.get(nome, 0) + 1

    labels = list(colaboradores.keys())
    values = list(colaboradores.values())

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color='orange')
    plt.title("Disparos por Colaborador")
    plt.xlabel("Colaborador")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=45)

    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(path_img)
    plt.close()
    abrir_imagem(path_img)

def gerar_grafico_envios_por_dia(dados, path_img):
    envio_por_dia = defaultdict(int)

    for item in dados:
        if item.send_at:
            data_formatada = item.send_at.strftime('%Y-%m-%d')
            envio_por_dia[data_formatada] += 1

    datas = sorted(envio_por_dia.keys())
    quantidades = [envio_por_dia[dt] for dt in datas]

    plt.figure(figsize=(10, 5))
    plt.plot(datas, quantidades, marker='o', color='teal', linestyle='-')
    plt.title("Envios Realizados por Dia")
    plt.xlabel("Data")
    plt.ylabel("Quantidade de Envios")
    plt.xticks(rotation=45)

    for i, (data, qtd) in enumerate(zip(datas, quantidades)):
        plt.text(i, qtd, str(qtd), ha='center', va='bottom')

    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path_img)
    plt.close()
    abrir_imagem(path_img)

def gerar_pdf(path_pdf, *imagens):
    c = canvas.Canvas(path_pdf)
    width, height = c._pagesize

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 100, "Relatório de Disparos - Análise Completa")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 140, "Gráficos gerados automaticamente com base nos dados")

    positions = [(450, imagens[0]), (50, imagens[1])]

    for y_pos, img_path in positions:
        if os.path.exists(img_path):
            c.drawImage(img_path, x=80, y=y_pos, width=width - 160, height=250, preserveAspectRatio=True)
        else:
            c.setFont("Helvetica", 12)
            c.drawString(100, y_pos, f"Imagem não encontrada: {img_path}")

    c.showPage()

    # Página com os outros dois gráficos
    if os.path.exists(imagens[2]):
        c.drawImage(imagens[2], x=80, y=400, width=width - 160, height=250, preserveAspectRatio=True)
    else:
        c.drawString(100, 400, f"Imagem não encontrada: {imagens[2]}")

    if os.path.exists(imagens[3]):
        c.drawImage(imagens[3], x=80, y=80, width=width - 160, height=250, preserveAspectRatio=True)
    else:
        c.drawString(100, 80, f"Imagem não encontrada: {imagens[3]}")

    c.showPage()
    c.save()
    print(f"PDF gerado: {path_pdf}")
    abrir_imagem(path_pdf)

@app.get("/disparador")
def get_disparador(page: int = Query(1), limit: int = Query(10), db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    dados_pagina = db.query(AgendaDisparos).offset(offset).limit(limit).all()
    total = db.query(AgendaDisparos).count()
    total_pages = -(-total // limit)

    dados_analise = db.query(AgendaDisparos).all()

    path_status = "grafico_status.png"
    path_midia = "grafico_midias.png"
    path_colab = "grafico_colaboradores.png"
    path_envios = "grafico_envios_por_dia.png"

    gerar_grafico_status(dados_analise, path_status)
    gerar_grafico_midias(dados_analise, path_midia)
    gerar_grafico_colaboradores(dados_analise, path_colab)
    gerar_grafico_envios_por_dia(dados_analise, path_envios)

    path_pdf = "relatorio_disparador.pdf"
    gerar_pdf(path_pdf, path_status, path_midia, path_colab, path_envios)

    return FileResponse(path_pdf, media_type='application/pdf', filename="relatorio_disparador.pdf")
