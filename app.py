import pandas as pd
import dash
from dash import Input, Output, dcc, html, ctx
import plotly.express as px
import dash_bootstrap_components as dbc
import pickle
import plotly.graph_objects as go
from fbprophet import Prophet

itinerarios_bases = pd.read_csv('Data/Itinerarios/itinerarios_bases.csv',index_col=0, dtype={'zip_code': 'str'})

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

buttons = html.Div(
    [
        dbc.Button("Bar chart", id="btn-bar", color="secondary"),
        dbc.Button("Line chart", id="btn-line", color="secondary"),
        dbc.Button(
            "Filled area chart", id="btn-area", color="secondary"
        ),
    ],
    className="d-grid gap-2",
)

app.layout = dbc.Container(
    [
        html.H1("Changing figures with callback_context (CTX)"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col([buttons], md=4),
                dbc.Col(dcc.Graph(id="graph"), md=8),
            ],
            align="center",
        ),
    ]
)


@app.callback(
    Output("graph", "figure"),
    Input("btn-bar", "n_clicks"),
    Input("btn-line", "n_clicks"),
    Input("btn-area", "n_clicks")
)

def display(btn_bar, btn_line, btn_area):
    button_id = ctx.triggered_id if ctx.triggered_id else "btn-bar"

    predictions = predict()
    
    if button_id == "btn-bar":
        return px.bar(predictions, x="ds", y="yhat")
    #elif button_id == "btn-line":
        #return (
            #go.Figure(go.Scatter(
            #    x =  predictions["ds"],
            #    y = predictions["yhat"],
            #    mode='lines',
            #    name = "Actual"
            #)))
    #else:
        #return px.area(predictions, x="ds", y="yhat")

def predict():
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
    
if __name__ == "__main__":
    app.run_server(debug=True)
