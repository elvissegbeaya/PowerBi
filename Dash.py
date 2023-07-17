import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import requests
from requests.auth import HTTPBasicAuth

app = Dash(__name__)
server = app.server

# Add a global variable to store the token
token = None

@app.callback(Output('output-container', 'children'), [Input('update-token-button', 'n_clicks')])
def update_token(n):
    global token
    if n and n > 0:
        try:
            # Get the token
            token_response = requests.get(
                "https://data.welldata.net/api/v1/tokens/token",
                headers={"accept": "application/json","ApplicationID": "00258061-5290-41AA-A63D-0B84E00FDA11"},
                params={},
                auth=HTTPBasicAuth(username="EDR_RestAPI", password="59ee#NK0sxtB"))

            token_response.raise_for_status()  # raise exception if the request failed

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting token: {err}")

        # Extract the token from the response
        token = token_response.json().get('token')  # replace 'token' with the correct field if different
        return html.Div(f"Token: {token}")

    return ''

@app.callback(Output('data-container', 'children'), [Input('get-data-button', 'n_clicks')])
def get_data(n):
    if n and n > 0:
        if token is None:
            return html.Div("No token available. Please generate a token first.")

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})

            data_response.raise_for_status()  # raise exception if the request failed

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        return html.Div(str(data_response.json()))

    return ''

@app.callback(Output('comments-container', 'children'), [Input('get-comments-button', 'n_clicks')])
def get_comments(n):
    if n and n > 0:
        if token is None:
            return update_token(n)

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2"
            data_response = requests.get(url, headers={'Token': token})

            data_response.raise_for_status()  # raise exception if the request failed

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        return html.Div(str(data_response.json()))

    return ''

@app.callback(Output('comments2-container', 'children'), [Input('get-comments2-button', 'n_clicks')])
def get_comments2(n):
    if n and n > 0:
        if token is None:
            return update_token(n)

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2"
            data_response = requests.get(url, headers={'Token': token})

            data_response.raise_for_status()  # raise exception if the request failed

            values = data_response.json()
            wells = []
            reportIds = values['availableReports']
            for w in reportIds:
                wells.append(w)

            reportId = wells[0]['id']

            url2 = f"https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2/JSON?reportIds.ids={reportId}"
            data_response2 = requests.get(url2, headers={'Token': token})

            data_response2.raise_for_status()  # raise exception if the request failed

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        return html.Div(str(data_response2.json()))

    return ''

@app.callback(Output('comments3-container', 'children'), [Input('get-comments3-button', 'n_clicks')])
def get_comments3(n):
    if n and n > 0:
        if token is None:
            return update_token(n)

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2"
            data_response = requests.get(url, headers={'Token': token})

            data_response.raise_for_status()  # raise exception if the request failed

            values = data_response.json()
            wells = []
            reportIds = values['availableReports']
            for w in reportIds:
                wells.append(w)

            reportId = wells[0]['id']

            url2 = f"https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2/JSON?reportIds.ids={reportId}"
            data_response2 = requests.get(url2, headers={'Token': token})

            data_response2.raise_for_status()  # raise exception if the request failed

            # Sort Morning Reports based on Type
            report = data_response2.json()
            # Rest of your code here

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        return html.Div(str(data_response2.json()))

    return ''

app.layout = html.Div([
    html.Button('Update Token', id='update-token-button', n_clicks=0),
    html.Button('Get Data', id='get-data-button', n_clicks=0),
    html.Button('Get Comments', id='get-comments-button', n_clicks=0),
    html.Button('Get Comments 2', id='get-comments2-button', n_clicks=0),
    html.Button('Get Comments 3', id='get-comments3-button', n_clicks=0),
    html.Div(id='output-container'),
    html.Div(id='data-container'),
    html.Div(id='comments-container'),
    html.Div(id='comments2-container'),
    html.Div(id='comments3-container')
])

if __name__ == "__main__":
    app.run_server(debug=True)
