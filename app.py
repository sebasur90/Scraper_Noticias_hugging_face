import streamlit as st
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from scrapper_rss import Scrapper
import datetime as dt

st.set_option('deprecation.showPyplotGlobalUse', False)

scrapper = Scrapper()

noticias = pd.read_csv('./diarios/diarios_historicos.csv')
noticias=noticias.drop('descripcion' ,axis=1)
fechas = pd.read_csv('./fechas.csv')

diarios = list(noticias.diario.unique())
secciones = list(noticias.seccion.unique())
columna_para_nube = ['titulo', 'descripcion']

st.set_page_config(
        page_title="Observatorio de noticias",        
        initial_sidebar_state="expanded"
    )


with st.sidebar:
    st.write("Creado por [sebasur90](https://www.linkedin.com/in/sebastian-rodriguez-9b417830/)")

    diarios_select = st.multiselect('Selecciona los  diarios',
                                    diarios, default=diarios)
    secciones_select = st.multiselect('Selecciona las secciones',
                                      secciones, default=secciones)
    palabra_buscada = st.text_input('Buscar palabra', 'Ninguna')

    if st.button('Actualizar Diarios'):
        dia_str = str(dt.datetime.today().date())
        if fechas.iloc[-1]['dia'] == dia_str:
            st.success("Las noticias ya estan actualizadas")
            pass
        else:
            with st.spinner('Actualizando los siguientes diarios..'):            
                scrapper.run()
                st.write("Se actualizaron las noticias")

    


if palabra_buscada == "Ninguna" or palabra_buscada == "":
    st.title("Observatorio de Noticias")
    st.write("""            

            Hola! Bienvenido a la aplicación de análisis de sentimientos en las noticias. Esta aplicación extrae las noticias de algunos de los diarios mas
            importantes del país ( a traves del RSS) y realiza un analisis de sentimientos sobre los titulos de cada una.
            La app permite filtrar por palabra clave y generar una nube de palabras con los resultados 

            De acuerdo al sentimiento analizado sobre cada noticia encontraremos 3 grupos: 
            
            **Sentimiento Positivo:** "YPF aumentó la distribución de gasoil y aseguró que el campo tiene garantizado el abastecimiento" 
               *Probabilidades: NEGATIVA=0.008 ---  NEUTRA 0.43  ---    POSITIVA 0.56 (GANADOR --> POSITIVA)* 
               
            
            **Sentimiento Neutro:** "El aeroclub de Comodoro Rivadavia celebró su 87° aniversario"
            *Probabilidades: NEGATIVA=0.02 ---  NEUTRA 0.67  ---    POSITIVA 0.30 (GANADOR --> NEUTRA)* 
            
            **Sentimiento Negativo:** "Crecen las expectativas de inflación del mercado"
            *Probabilidades: NEGATIVA=0.60 ---  NEUTRA 0.37  ---    POSITIVA 0.15 (GANADOR --> NEGATIVA)* 
            
            """)

    

    pass
else:
    #st.title("Observatorio de Noticias")
    st.header(f"Resultados para : {palabra_buscada}")
    
    noticias = noticias[noticias['titulo'].str.contains(palabra_buscada)]

st.session_state['dataframe_filtrado'] = noticias[(noticias.diario.isin(
    diarios_select)) & (noticias.seccion.isin(secciones_select))]

st.subheader("Muestra aleatoria de noticias")
st.dataframe(st.session_state['dataframe_filtrado'].sample(frac=1))
st.session_state['dataframe_agrupado'] = st.session_state['dataframe_filtrado'].groupby(
    'diario')[['pond_negativos', 'pond_neutro', 'pond_positivo']].mean().reset_index()

fig = px.bar(st.session_state['dataframe_agrupado'], x="diario", y=['pond_neutro', "pond_negativos", 'pond_positivo'], text_auto=True,
             title=f"Analisis de sentimientos para las noticias seleccionadas según el diario"
             )

newnames = {'pond_neutro':'NEUTRAL', 'pond_negativos': 'NEGATIVA','pond_positivo': 'POSITIVA'}
fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                      legendgroup = newnames[t.name],
                                      hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                     )
                  )
fig.update_layout(
    xaxis_title="Diarios",
    yaxis_title="Probabilidades (de 0 a 1)",
    
)                  
fig.update_layout(legend_title_text='Probabilidades')

st.plotly_chart(fig)


def transforma_letras_para_wordcloud(dataframe_noticias):
    columna_analizada = list(dataframe_noticias['titulo'])
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


def genera_wordcloud(dataframe_noticias):
    palabras_para_wordcloud = transforma_letras_para_wordcloud(
        dataframe_noticias)
    palabras_ignoradas = set(['a', 'ante', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'para', 'por', 'segun', 'sin', 'sobre', 'el', 'la', 'los', 'las',
                              '...', 'y', 'hoy', 'este', 'cuanto',  'un', 'del', 'las',  'que', 'con', 'todos',  'es', '¿qué',  'como', 'cada',
                              'jueves', '¿cuanto', 'hoy', 'al', 'cual', 'se', 'su', 'sus', 'lo', 'una', 'un', 'tiene',
                              'le', 'habia'])

    wordcloud = WordCloud(width=1920, height=1080, stopwords=palabras_ignoradas).generate(
        palabras_para_wordcloud)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot()


if st.button('Generar Nube'):
    genera_wordcloud(st.session_state['dataframe_filtrado'])
else:
    pass
