import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import swat
from dash import Dash, Input, Output, callback, dcc, html
from sasctl import Session
from sasctl.services import microanalytic_score as mas

SASurl = "https://server.demo.sas.com"
user = "student"
password = "Metadata0"
data_source = "https://raw.githubusercontent.com/sassoftware/sas-viya-programming/master/data/cars.csv"
table_name = "cars"

conn = swat.CAS(
    f"{SASurl}/cas-shared-default-http",
    ssl_ca_list="/Users/sbxxab/Downloads/server.demo.sas.com.cer",
)

tbl = conn.read_csv(data_source, table_name)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

header_bar = dbc.NavbarSimple(
    id="header-bar",
    brand="Dash, SWAT, and SASCTL integration",
    color="primary",
    dark=True,
)

app.layout = dbc.Container(
    children=[
        header_bar,
        dbc.Select(tbl.origin.unique(), "Europe", id="origin-selection"),
        dcc.Graph(id="graph-content"),
        dbc.Row([dbc.Col(id="details", width=6), dbc.Col(id="score", width=6)]),
    ]
)


@callback(
    Output("graph-content", "figure"),
    Input("origin-selection", "value"),
)
def update_graph(value):
    filter = f"origin='{value}'"
    df = tbl.query(filter).to_frame()
    return px.bar(
        df,
        x="Make",
        y="Invoice",
        color="Make",
        hover_data={"Make": False, "Model": True, "Invoice": True},
    )


@callback(
    Output("details", "children"),
    Input("graph-content", "clickData"),
    prevent_initial_call=True,
)
def on_graph_click(clickData):
    make = clickData["points"][0]["x"]
    model = clickData["points"][0]["customdata"][0]
    filter = f"make='{make}' and model='{model}'"
    df = tbl.query(filter).to_frame()
    list = []
    if df.shape[0] == 1:
        for index, values in df.iterrows():
            for id in values.index:
                if id not in ["Make", "Model", "Invoice"]:
                    list_item = dbc.ListGroupItem(f"{id}: {values[id]}")
                    list.append(list_item)
    card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Row(
                    [
                        dbc.Col(html.H3(make), width=6),
                        dbc.Col(html.H3(model), width=6),
                    ]
                )
            ),
            dbc.CardBody(dbc.ListGroup(list)),
            dbc.CardFooter(html.H3(f"Invoice: ${df.iloc[0]['Invoice']:.0f}")),
        ]
    )
    return card


@callback(
    Output("score", "children"),
    Input("graph-content", "clickData"),
    prevent_initial_call=True,
)
def score_data(clickData):
    make = clickData["points"][0]["x"]
    model = clickData["points"][0]["customdata"][0]
    filter = f"make='{make}' and model='{model}'"
    df = tbl.query(filter).to_frame()
    list = {}
    if df.shape[0] == 1:
        for index, values in df.iterrows():
            for id in values.index:
                if id not in ["Make", "Model", "Invoice", "Origin", "MSRP", "Length"]:
                    list[id] = values[id]
    with Session(SASurl, user, password, verify_ssl=False):
        result = mas.execute_module_step("msrp_prediction", "score", **list)
        card = dbc.Card(
            [
                dbc.CardHeader(
                    dbc.Row(
                        [
                            dbc.Col(html.H3(make), width=6),
                            dbc.Col(html.H3(model), width=6),
                        ]
                    )
                ),
                dbc.CardBody(html.Div(f"Suggested Price:${result['P_MSRP']:.0f}")),
            ]
        )
    return card


if __name__ == "__main__":
    app.run(debug=True)
