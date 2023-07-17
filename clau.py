import os
from typing import Dict, Any

import requests
from requests.auth import HTTPBasicAuth

import dash
from dash import Input, Output, State, callback_context

# Load sensitive values from environment
API_KEY = os.environ["API_KEY"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

app = dash.Dash(__name__)

# Initialize token
token = None


def get_access_token() -> str:
    response = requests.get(
        "https://data.welldata.net/api/v1/tokens/token",
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    return response.json()["token"]


def get_data() -> Dict[str, Any]:
    response = requests.get(
        "https://data.api.com/data",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()


# Implement other API functions

@app.callback(Output("output", "children"),
              Input("update", "n_clicks"),
              # other inputs
              )
def update(n_clicks):
    global token
    if not token:
        token = get_access_token()

    ctx = callback_context

    if ctx.triggered_id == "update":
        token = get_access_token()
        return "Token updated"

    # Call API functions based on triggered button

    return ""


if __name__ == "__main__":
    app.run_server(debug=True)