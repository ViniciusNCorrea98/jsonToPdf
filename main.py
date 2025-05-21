import matplotlib
matplotlib.use('Agg')
from fastapi import FastAPI, Depends, Query, HTTPException
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

from concurrent.futures import ThreadPoolExecutor

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/test_db")
def test_db(db: Session = Depends(get_db)):
    dados = db.query(AgendaDisparos).all()
    return dados

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
    try:
        status_counts = defaultdict(int)
        for item in dados:
            status = item.status or "Desconhecido"
            status_counts[status] += 1

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
    except Exception as e:
        print(f"Erro ao gerar gráfico de status: {str(e)}")

def gerar_grafico_midias(dados, path_img):
    try:
        midia_counts = defaultdict(int)
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
    except Exception as e:
        print(f"Erro ao gerar gráfico de mídias: {str(e)}")

def gerar_grafico_colaboradores(dados, path_img):
    try:
        colaboradores = defaultdict(int)
        for item in dados:
            nome = item.nome_colaborador or "Desconhecido"
            colaboradores[nome] += 1

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
    except Exception as e:
        print(f"Erro ao gerar gráfico de colaboradores: {str(e)}")

def gerar_grafico_envios_por_dia(dados, path_img):
    try:
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
    except Exception as e:
        print(f"Erro ao gerar gráfico de envios por dia: {str(e)}")

def gerar_pdf(path_pdf, *imagens):
    try:
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
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")

def gerar_markdown(path_md, *imagens):
    with open(path_md, 'w', encoding='utf-8') as f:
        f.write("# 📊 Relatório de Disparos\n\n")
        f.write(f"_Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}_\n\n")
        f.write("## 1. Distribuição de Status dos Disparos\n")
        f.write(f"![Status]({imagens[0]})\n\n")
        f.write("## 2. Tipos de Conteúdo Enviado\n")
        f.write(f"![Mídias]({imagens[1]})\n\n")
        f.write("## 3. Disparos por Colaborador\n")
        f.write(f"![Colaboradores]({imagens[2]})\n\n")
        f.write("## 4. Envios Realizados por Dia\n")
        f.write(f"![Envios por Dia]({imagens[3]})\n\n")

def gerar_e_upload_em_paralelo(dados_analise):
    # Geração sequencial dos gráficos
    gerar_grafico_status(dados_analise, "grafico_status.png")
    gerar_grafico_midias(dados_analise, "grafico_midias.png")
    gerar_grafico_colaboradores(dados_analise, "grafico_colaboradores.png")
    gerar_grafico_envios_por_dia(dados_analise, "grafico_envios_por_dia.png")

    # Aguarde arquivos estarem presentes
    for path in [
        "grafico_status.png",
        "grafico_midias.png",
        "grafico_colaboradores.png",
        "grafico_envios_por_dia.png"
    ]:
        if not os.path.exists(path):
            raise Exception(f"Arquivo de gráfico não foi gerado: {path}")

    # Geração de PDF e markdown
    path_pdf = "relatorio_disparador.pdf"
    gerar_pdf(path_pdf, "grafico_status.png", "grafico_midias.png", "grafico_colaboradores.png", "grafico_envios_por_dia.png")

    path_md = "relatorio_disparador.md"
    gerar_markdown(path_md, "grafico_status.png", "grafico_midias.png", "grafico_colaboradores.png", "grafico_envios_por_dia.png")

    # Limpeza dos gráficos
    for path in [
        "grafico_status.png",
        "grafico_midias.png",
        "grafico_colaboradores.png",
        "grafico_envios_por_dia.png"
    ]:
        try:
            os.remove(path)
        except:
            pass


@app.get("/disparador")
def get_disparador(page: int = Query(1), limit: int = Query(10), db: Session = Depends(get_db)):
    if page <= 0:
        raise HTTPException(status_code=400, detail="Página deve ser maior que 0")
    if limit <= 0 or limit > 100:
        raise HTTPException(status_code=400, detail="Limite deve estar entre 1 e 100")

    offset = (page - 1) * limit


    dados = db.query(AgendaDisparos).offset(offset).limit(limit).all()
    
    if not dados:
        return {"mensagem": "Nenhum dado encontrado para os parâmetros informados"}

    try:
        # Geração de gráficos, PDF e upload
        gerar_e_upload_em_paralelo(dados)
    except Exception as e:
        return {"mensagem": f"Erro ao gerar gráficos e PDF: {str(e)}"}

    path_pdf = "relatorio_disparador.pdf"
    try:
        return FileResponse(path_pdf, media_type="application/pdf", filename="relatorio_disparador.pdf", headers={"Content-Disposition": "attachment; filename=relatorio_disparador.pdf"})
    except Exception as e:
        return {"mensagem": f"Erro ao retornar FileResponse: {str(e)}"}
