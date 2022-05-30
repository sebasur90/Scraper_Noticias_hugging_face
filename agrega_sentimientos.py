import pandas as pd
from pysentimiento import create_analyzer
def genera_excel_sentimientos(noticias):
    titulos_buscados=noticias.titulo
    from pysentimiento import create_analyzer
    analyzer = create_analyzer(task="sentiment", lang="es")
    sentimientos=[]
    negativos=[]
    neutros=[]
    positivos=[]
    for titulo in titulos_buscados:
        prediccion=analyzer.predict(titulo)
        sentimientos.append(prediccion.output)
        negativos.append(prediccion.probas['NEG'])
        neutros.append(prediccion.probas['NEU'])
        positivos.append(prediccion.probas['POS']) 
        print(prediccion)
    
    noticias=noticias.copy()
    noticias['sentimiento']=sentimientos
    noticias['pond_negativos']=negativos
    noticias['pond_neutro']=neutros
    noticias['pond_positivo']=positivos

    #noticias.to_excel("noticias_con_sentimientos.xlsx")

    return noticias