import os
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from diarios_rss import diarios
import agrega_sentimientos
import datetime as dt
import streamlit as st

class Scrapper:

    def __init__(self):
        self.noticias = {}

    def recorre_diarios(self):
        contador = 0
        for diario in diarios:
            try:
                print(f"Obteniendo noticias de {diarios[diario]['diario']} ,seccion {diarios[diario]['seccion']} ")
                st.session_state['muestra_progreso']=f"{diarios[diario]['diario']} -- > seccion {diarios[diario]['seccion']} "
                st.write(st.session_state['muestra_progreso'])
                time.sleep(0.5)
                url = requests.get(diarios[diario]['rss'])
                soup = BeautifulSoup(url.content, "xml")
                items_pagina = soup.find_all('item')
                for item in range(len(items_pagina)):
                    noticia = {}
                    noticia['diario'] = diarios[diario]['diario']
                    noticia['seccion'] = diarios[diario]['seccion']
                    noticia['titulo'] = items_pagina[item].title.text
                    if items_pagina[item].description == None or items_pagina[item].description == " " or items_pagina[item].description == "<NA>":
                        if diarios[diario]['diario'] == 'Perfil':
                            noticia['descripcion'] = items_pagina[item].description.text.split(
                                "</p>")[1].split('<a href')[0]
                        if diarios[diario]['diario'] == 'La_izquierda_diario':
                            noticia['descripcion'] = items_pagina[item].description.text.split("<p>")[
                                1].split('</p>')[0]
                        else:
                            noticia['descripcion'] = items_pagina[item].title.text
                    else:
                        if diarios[diario]['diario'] == 'Perfil':
                            noticia['descripcion'] = items_pagina[item].description.text.split(
                                "</p>")[1].split('<a href')[0]
                        if diarios[diario]['diario'] == 'La_izquierda_diario':
                            noticia['descripcion'] = items_pagina[item].description.text.split("<p>")[
                                1].split('</p>')[0]
                        else:
                            noticia['descripcion'] = (
                                items_pagina[item].description.text)

                    self.noticias[contador] = noticia
                    contador = contador + 1
            except:
                pass

    def formateo_noticias(self):
        dataframe_noticias = pd.DataFrame(self.noticias).transpose()
        dataframe_noticias.drop_duplicates(subset=['titulo'])
        return dataframe_noticias

    def sentimientos(self, dataframe_noticias):
        with st.spinner('Descargando sentimientos para las noticias..'):  
            dia_str = str(dt.datetime.today().date())
            noticias = agrega_sentimientos.genera_excel_sentimientos(
                dataframe_noticias)
            noticias.to_csv(
                f"diarios/noticias_con_sentimientos_{dia_str}.csv", index=False)
            pass

    def apila_diarios_historicos(self):
        lista_diarios = os.listdir('diarios')
        print(lista_diarios)
        lista_diarios.remove('diarios_historicos.csv')
        dataframes = []
        dataframes.append(pd.read_csv("diarios/diarios_historicos.csv"))
        for diarios in lista_diarios:
            dataframes.append(pd.read_csv("diarios/"+diarios))
        apilados = pd.concat(dataframes, axis=0)
        apilados.to_csv(f"diarios/diarios_historicos.csv", index=False)

    def agrega_fecha_hoy(self):
        fechas = pd.read_csv("fechas.csv")
        dia_str = str(dt.datetime.today().date())
        fechas = fechas.append({'dia': dia_str}, ignore_index=True)
        fechas.to_csv("fechas.csv", index=False)
        

    def transforma_letras_para_wordcloud(self, dataframe_noticias):
        columna_analizada = list(dataframe_noticias.titulo)
        acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                   'Á': 'A', 'E': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
        lista_palabras_para_wordcloud = []
        for palabras in columna_analizada:
            palabras_div = palabras.split(' ')
            for letras in palabras_div:
                for acen in acentos:
                    if acen in letras:
                        letras = letras.replace(acen, acentos[acen])
                lista_palabras_para_wordcloud.append(letras.lower())
        return ' '.join(lista_palabras_para_wordcloud)

    def genera_wordcloud(self, palabras_para_wordcloud):
        palabras_ignoradas = set(['a', 'ante', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'para', 'por', 'segun', 'sin', 'sobre', 'el', 'la', 'los', 'las',
                                  '...', 'y', 'hoy', 'este', 'cuanto',  'un', 'del', 'las',  'que', 'con', 'todos',  'es', '¿qué',  'como', 'cada',
                                  'jueves', '¿cuanto', 'hoy', 'al', 'cual', 'se', 'su', 'sus', 'lo', 'una', 'un', 'tiene',
                                  'le', 'habia'])

        wordcloud = WordCloud(width=1920, height=1080, stopwords=palabras_ignoradas).generate(
            palabras_para_wordcloud)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")

    def run(self):
        self.recorre_diarios()
        dataframe_noticias = self.formateo_noticias()
        self.sentimientos(dataframe_noticias)
        self.apila_diarios_historicos()
        palabras_para_wordcloud = self.transforma_letras_para_wordcloud(
            dataframe_noticias)
        self.genera_wordcloud(palabras_para_wordcloud)
        self.agrega_fecha_hoy()
