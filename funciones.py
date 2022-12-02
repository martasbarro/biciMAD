# funciones.oy> 
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
from dash import html
from fbprophet import Prophet
import pickle



def topNRutas(df, n_top ): 
    cols_rutas=['Origen_destino','Latitud_Salida','Longitud_Salida','Distrito_Salida','Latitud_Llegada','Longitud_Llegada','Distrito_Llegada', 'idplug_station', 'idunplug_station' ]
    df_rutas=df[df['idplug_station']!=df['idunplug_station'] ].groupby(cols_rutas)['return_date'].count().to_frame().reset_index().sort_values('return_date', ascending=False)
    df_rutas.rename(columns= {'return_date': 'viajes'},  inplace=True )
    topRutas=df_rutas.head(25)
    topRutas['ruta']=topRutas.apply(lambda x: sorted([x.Longitud_Salida, x.Latitud_Salida, x.Longitud_Llegada, x.Latitud_Llegada]), axis=1)
    topRutas['ruta']=topRutas['ruta'].apply(lambda x: ' '.join([str(word) for word in x]))
    
    def rutas(df): 
        
        long_llegada=df['Longitud_Llegada'].iloc[0]
        lat_llegada=df['Latitud_Llegada'].iloc[0]
        distrito_llegada=df['Distrito_Llegada'].iloc[0]
        
        long_salida=df['Longitud_Salida'].iloc[0]
        lat_salida=df['Latitud_Salida'].iloc[0]
        distrito_salida=df['Distrito_Salida'].iloc[0]
        viajes=df['viajes'].sum()
        
        cols= ['Latitud_Salida','Longitud_Salida','Distrito_Salida','Latitud_Llegada','Longitud_Llegada','Distrito_Llegada', 'viajes']
        datos=[lat_salida, long_salida, distrito_salida, lat_llegada, long_llegada,distrito_llegada, viajes]
        return pd.Series(dict(zip(cols,datos)))
                
    topRutasFin= topRutas.groupby('ruta').apply(rutas).reset_index()
    return(topRutasFin.head(n_top))

def topEstaciones(df): 
    
    cols_llegada_estacion=['Longitud_Llegada','Latitud_Llegada', 'Distrito_Llegada' ]
    cols_salida_estacion=['Longitud_Salida', 'Latitud_Salida','Distrito_Salida']
    cols_estaciones=['Longitud','Latitud', 'Distrito']

    estaciones_llegada=df[cols_llegada_estacion]
    estaciones_salida=df[cols_salida_estacion]
    estaciones_llegada.rename(columns=dict(zip(cols_llegada_estacion,cols_estaciones)) , inplace=True)
    estaciones_salida.rename(columns=dict(zip(cols_salida_estacion,cols_estaciones)) , inplace=True)

    topEstaciones0=pd.concat([estaciones_salida, estaciones_llegada], axis=0, ignore_index=True )
    topEstaciones0['count']=1
    def top_estaciones(df): 
        distrito= df['Distrito'].iloc[0]
        count=df['count'].sum()
        cols=['Distrito', 'count']
        datos=[distrito, count]
        return(pd.Series(dict(zip(cols,datos))))
    topEstaciones=topEstaciones0.groupby(['Longitud','Latitud']).apply(top_estaciones).reset_index()

    return(topEstaciones)

def GráficoMapasRutas(itinerarios_bases, n_top):
    if  type(itinerarios_bases)==str: 
        fig=px.scatter_mapbox(width = 500, height = 400)
        fig.update_layout(
        title='Rutas más concurridas',
        autosize=True,
        hovermode='closest',
        showlegend=True,
        width = 500,
        height = 500,
        mapbox=dict(
            bearing=0,
            center=dict(
                lat=40.435,
                lon=-3.69
            ),
            zoom=11.4,
            style= 'carto-positron' # 'open-street-map'
            
            )
        )
        return fig
    else: 
        top_rutas=topNRutas(itinerarios_bases,n_top )
        top_estaciones=topEstaciones(top_rutas) 
        
        fig = px.scatter_mapbox(top_estaciones, lat="Latitud", lon="Longitud",color='Distrito', width = 500, height = 500)# zoom = 70, size='count'

        for i in range(top_rutas.shape[0]): 
            valores=top_rutas.iloc[i,:]

            fig.add_trace(
                go.Scattermapbox(
                mode = "markers+lines",
                lon = [valores['Longitud_Salida'], valores['Longitud_Llegada']],
                lat = [valores['Latitud_Salida'], valores['Latitud_Llegada']],
                line= {'width':valores['viajes']*0.005} ,
                name= 'Ruta '+str(1+i)

                ))
        hover_header = 'Estacion: %{text} '

        fig.update_layout(
            title='Rutas más concurridas',
            #autosize=True,
            hovermode='closest',
            showlegend=True,
            width = 500,
            height = 500,
            mapbox=dict(
                bearing=0,
                center=dict(
                    lat=40.435,
                    lon=-3.69
                ),
                zoom=11.4,
                style= 'carto-positron' # 'open-street-map'
                
            )
        )
        return fig

    
def prediction():
    m = pickle.load(open('Predictions/demandpredicition.pkl', 'rb'))
    
    def typeofday(ds):
        date = pd.to_datetime(ds)
        if (date.weekday() == 5 or date.weekday() == 6):
            return 0
        elif(date.weekday() == 4):
            return 1
        else:
            return 2

    date = pd.to_datetime(['2020-1-1 00:00:00'])
    date -= pd.to_timedelta(1,'h') 
    # initializing K
    k = 24*7

    future = []
    for hour in range(k):
        date += pd.to_timedelta(1,'h')
        future.append(date)

    future = pd.DataFrame(future)
    future.columns = ['ds']
    future['ds'] = pd.to_datetime(future['ds'])  
    future['typeofday'] = future['ds'].apply(typeofday)

    # use the model to make a forecast
    forecast = m.predict(future)
    forecast[forecast["yhat"]<0] = 0
    
    return forecast

# def workCloudGeneral(itinerarios_bases): 
    
#     itinerarios_bases=itinerarios_bases.astype({'Distrito_Llegada': str})
#     itinerarios_bases2=itinerarios_bases
#     itinerarios_bases2['Distrito_Llegada']=itinerarios_bases2['Distrito_Llegada'].apply(lambda x: x.replace('\xa0', ''))
#     barrios_llegada = itinerarios_bases2['Distrito_Llegada']


#     barrios_llegada_wordcloud=["".join(i for i in palabra if not i.isdigit()) for palabra in barrios_llegada]
#     barrios_frec=Counter(barrios_llegada_wordcloud)


#     wordcloud = WordCloud (
#                         background_color = 'white',
#                         width = 1000,
#                         height = 750,
#                         collocations=False).generate_from_frequencies(barrios_frec)

#     fig=px.imshow(wordcloud) # image show
#     fig.update_layout(width=1000, height=750)
#     return fig.to_image()

