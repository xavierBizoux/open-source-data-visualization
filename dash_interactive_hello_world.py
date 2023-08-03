from dash import Dash, Input, Output, State, callback, dcc, html

app = Dash(__name__)

app.layout = html.Div(
    [
        html.Div(
            children=[
                "Say hello to:",
                dcc.Input(
                    id="name",
                    type="text",
                    placeholder="Enter a name",
                ),
                html.Button("Update",id="button")
            ]
        ),
        html.H1(id="message")
    ]
)

@callback(
    Output("message", "children"),
    Input("button", "n_clicks"),
    State("name", "value")
)
def updateMessage(nb, name):
    if nb:
        message = f"Hello {name}!"
    else:
        message = "Hello world"
    return message

if __name__ == "__main__":
    app.run(debug=True)
