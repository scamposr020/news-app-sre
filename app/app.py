from flask import Flask, jsonify, render_template_string, Response
import requests
from bs4 import BeautifulSoup
import os
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

URL = "https://crhoy.com/"
ARCHIVO_TITULARES = "titulares.txt"

# Métricas Prometheus con etiquetas
nuevas_noticias_total = Counter(
    'nuevas_noticias_total',
    'Cantidad total de noticias nuevas detectadas',
    ['source']
)
latencia_histogram = Histogram(
    'latencia_peticion_seconds',
    'Latencia de las peticiones al endpoint /nuevos',
    ['endpoint']
)

def obtener_titulares():
    try:
        resp = requests.get(URL, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        titulares_raw = soup.select("div.news-item-content h2.text-body")
        if not titulares_raw:
            return []
        vistos = set()
        titulares_unicos = []
        for h2 in titulares_raw:
            texto = h2.text.strip()
            if texto and texto not in vistos:
                titulares_unicos.append(texto)
                vistos.add(texto)
        return titulares_unicos
    except Exception as e:
        logging.exception("Error al obtener titulares")
        return []

def cargar_titulares_previos():
    if not os.path.exists(ARCHIVO_TITULARES):
        return []
    with open(ARCHIVO_TITULARES, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def guardar_titulares(titulares):
    with open(ARCHIVO_TITULARES, "w", encoding="utf-8") as f:
        for titulo in titulares:
            f.write(titulo + "\n")

@app.route("/")
def home():
    titulares_actuales = obtener_titulares()
    if titulares_actuales:
        guardar_titulares(titulares_actuales)
    else:
        titulares_actuales = ["⚠️ No se pudieron obtener titulares."]
    html = """
    <h1>📰 Titulares CRHoy</h1>
    <ul>
    {% for t in titulares %}
        <li>{{ t }}</li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, titulares=titulares_actuales)

@app.route("/nuevos")
def nuevos():
    with latencia_histogram.labels(endpoint="/nuevos").time():
        titulares_actuales = obtener_titulares()
        titulares_previos = cargar_titulares_previos()
        nuevas = [t for t in titulares_actuales if t not in titulares_previos]
        if nuevas:
            guardar_titulares(titulares_actuales)
            nuevas_noticias_total.labels(source="crhoy").inc(len(nuevas))
        return jsonify({
            "nuevas": nuevas,
            "total": len(nuevas)
        })

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
