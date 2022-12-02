import pandas as pd
import dash
from dash import Input, Output, dcc, html, ctx
import plotly.express as px
import dash_bootstrap_components as dbc
import pickle
import plotly.graph_objects as go
from fbprophet import Prophet

itinerarios_bases = pd.read_parquet('./Data/Itinerarios/itinerarios_bases.parquet')

barrios_dropdown_options = [{'label':x, 'value':x} for x in sorted(itinerarios_bases["Barrio_Salida"].unique())]

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-top": "2rem",
    "position":"fixed",
}

sidebar = dbc.Card(
    [
        dbc.CardBody([
            dbc.NavItem(dbc.NavLink(html.I(className="bi bi-bicycle", style = {"font-size":"5rem"}), style={"text-align":"center"},href="https://www.bicimad.com/", external_link=True)),
            html.H1("BiciMAD",  style = {"text-align":"center"}),
            html.Hr(),
            html.P("Cuadro de mandos de red de bicicletas eléctricas de la Comunidad de Madrid", className = "lead"),
            dbc.Nav(
                children = [
                    dbc.NavLink("General", href="/", active = "exact"),
                    dbc.NavLink("Comparativa", href="/comparativa", active="exact"),
                    dbc.NavLink("Predicciones", href="/predicciones", active="exact"),
                ],
                vertical = True,
                pills = True,
            ),
        ], style={"margin-top":"0rem"}),
    ], color = "light",
        style = {"height":"100vh", "width":"16rem",  "position":"fixed"}    
)    
    

content = dbc.Container(
    id="page-content",
    children = [],
    style = CONTENT_STYLE,
)

# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, "customStyle.css",dbc.icons.BOOTSTRAP], 
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

app.layout = html.Div([
        dcc.Location(id="url"),
        sidebar,
        content
])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)

def render_page_content(pathname):
    if pathname == "/":
        return [
            dbc.Row([
                dbc.Col(
                    html.H1([dbc.Badge("Página principal de BiciMAD", className="ms-1",  color = "light", style={"color":"#18bc9c"})]),
                    width=12
                )
            ])
        ]
    elif pathname == "/comparativa":
        return [
            html.H1('ESTO ES LA COMPARATIVA',
                    style={'color': 'blue'})
        ]

    elif pathname == "/predicciones":
        return [
            html.Div(
                [
                    dbc.Row([
                        dbc.Col(html.Div(html.H1("Predicciones",style={"color":"#18bc9c"})), width=3),
                        dbc.Col(dcc.Graph(id="avg-demand-day", figure={}), width=3),
                        dbc.Col(html.Div(html.P("Med demanda hora")), width=3),
                        dbc.Col(html.Div(html.P("med demanda mes")), width=3)
                    ]),

                    dbc.Row([
                        dbc.Col(dcc.Dropdown(id="start-date-prediction", multi=False, value="2020-01-01", options=barrios_dropdown_options), width = 6),
                        dbc.Col(dcc.Dropdown(id="start-date-prediction", multi=False, value="2020-01-01", options=barrios_dropdown_options), width = 6)   
                    ], justify='start') # center, end, between, around
                ])
            ]

    return dbc.Jumbotron(
        children = [
            html.H1("404: Not found", className = "text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised...")
        ]
    )

@app.callback(
    Output("avg-demand-day", "figure"),
    Input("start-date-prediction", "value")
)

def bar_demand_day(barrio_selected):
    itinerarios_bases["unplug_hourTime"] = pd.to_datetime(itinerarios_bases["unplug_hourTime"])
    df = itinerarios_bases[itinerarios_bases["Barrio_Salida"]==barrio_selected]
    fig = go.Figure(go.Bar(
        x = df.groupby(df["unplug_hourTime"].dt.dayofweek).agg({'Count':'mean'}).index,
        y = df.groupby(df["unplug_hourTime"].dt.dayofweek).agg({'Count':'mean'})['Count']
    ))
    fig.update_layout(title_text="Media <b>demanda por día de la semana</b> BiciMAD", yaxis_title="Demand")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=3000)