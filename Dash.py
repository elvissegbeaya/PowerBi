import dash_table
import pandas as pd
import requests
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth


# Classes
# class Well(BaseModel):
#     jobID = ""
#     jobName = ""
#     Owner = ""
#     rigNumber = ""
#     Startdate = ""
#     EndDate = ""



class UnitV1(BaseModel):
    id: str
    name: str
    abbreviation: str


class Attribute(BaseModel):
    id: str
    mode: str




# app = Dash(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# Variables
tmpAllJobs = []


# Add a global variable to store the token and input value
token = None
JobID = None
header = ['Contractor', 'Rig Number', 'Operator', 'Well name', 'IADC', 'IADC 2', 'IADC3', 'HookLoad', 'PumpPressure', 'BlockHeight', 'PumpSpm', 'PumpSpm2', 'PumpSpm3',
          'RotaryTorque', 'TopDrive RPM',
          'TopDrive Torque', 'WOB', 'ROP-F', 'T-HL', 'BitPosition', 'BitStatus', 'SlipStatus', 'Comments', 'Next 24 Hr Comments', 'Report Id', 'Report Date']
df = pd.DataFrame(tmpAllJobs)

@app.callback(Output('output-container', 'children'), [Input('update-token-button', 'n_clicks')])
def update_token(n):
    global token
    if n and n > 0:
        try:
            # Get the token
            token_response = requests.get(
                "https://data.welldata.net/api/v1/tokens/token",
                headers={"accept": "application/json", "ApplicationID": "00258061-5290-41AA-A63D-0B84E00FDA11"},
                params={},
                auth=HTTPBasicAuth(username="EDR_RestAPI", password="59ee#NK0sxtB"))

            token_response.raise_for_status()  # raise exception if the request failed

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting token: {err}")

        # Extract the token from the response
        token = token_response.json().get('token')  # replace 'token' with the correct field if different
        emoji_check = u'\u2705'  # ✅
        return html.Div(f"Token: {emoji_check}")

    return ''

@app.callback(Output('data-container', 'children'), [Input('get-data-button', 'n_clicks')])
def get_data(n):
    total = 0
    tmpJobs = []
    well_operator =''
    well_contractor = ''
    if n and n > 0:
        if token is None:
            return html.Div("No token available. Please generate a token first.")

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed
            for w in values:
                # tmpJobs.append(w['id'])
                # tmpJobs.append(f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}")  # Rig Name
                # # set operator and contractor
                # tmpJobs.append(w['assetInfoList'][0]['owner'])  # Contractor
                # tmpJobs.append(w['siteInfoList'][0]['owner'])  # Operator
                # tmpJobs.append(w['startDate'])
                # tmpJobs.append(w['firstDataDate'])
                # tmpJobs.append(w['lastDataDate'])

                tmpJobs.append([w['id'],f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}",w['assetInfoList'][0]['owner'],w['siteInfoList'][0]['owner'],w['startDate'],w['firstDataDate'],w['lastDataDate']])
            header = ['Job Id','Rig','Contractor', 'Operator','Start Date', 'First Data Date', 'Last Data Date']
            df = pd.DataFrame(tmpJobs)
            df.columns = header
            app.layout = html.Div([
                dash_table.DataTable(
                    id='AllActiveJobsTable',
                    columns=[{"name": str(i), "id": str(i)} for i in df.columns],
                    data=df.to_dict('records'),
                )
            ])


        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        return app.layout

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
            url = f"https://data.welldata.net/api/v1/jobs/{JobID}/reports/daily/2"
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
            # Getting all Jobs:






            # Getting Report Comments

            # Make the data request with the token
            url = f"https://data.welldata.net/api/v1/jobs/{JobID}/reports/daily/2"
            data_response = requests.get(url, headers={'Token': token})

            data_response.raise_for_status()  # raise exception if the request failed

            values = data_response.json()
            wells = []
            reportIds = values['availableReports']
            for w in reportIds:
                wells.append(w)

            reportId = wells[0]['id']

            url2 = f"https://data.welldata.net/api/v1/jobs/{JobID}/reports/daily/2/JSON?reportIds.ids={reportId}"
            data_response2 = requests.get(url2, headers={'Token': token})

            data_response2.raise_for_status()  # raise exception if the request failed

            # Sort Morning Reports based on Type
            report = data_response2.json()
            # Rest of your code here

            if 'GenericAmericanMorningReportDW' in str(report):
                # continue
                reportDate = report['Reports'][0]['GenericAmericanMorningReportDW']['Header']['Date']
                if 'OpsAtReportTime' in str(report):
                    comment = report['Reports'][0]['GenericAmericanMorningReportDW']['Header']['OpsAtReportTime']
                if 'OpsNext24' in str(report):
                    comment24 = report['Reports'][0]['GenericAmericanMorningReportDW']['Header']['OpsNext24']
                reportID = report['Reports'][0]['GenericAmericanMorningReportDW']['ReportAttributes']['ReportID']
                reportStatus = report['Reports'][0]['GenericAmericanMorningReportDW']['ReportAttributes']['ReportStatus']

                # 'HandPMorningReport'
            elif 'HandPMorningReport' in str(report):
                reportDate = report['Reports'][0]['HandPMorningReport']['Header']['Date']
                comment = report['Reports'][0]['HandPMorningReport']['Operations']['PresentOp']
                comment24 = ''
                reportID = report['Reports'][0]['HandPMorningReport']['ReportAttributes']['ReportID']
                reportStatus = report['Reports'][0]['HandPMorningReport']['ReportAttributes']['ReportStatus']

                # 'ScanMorningReport'
            elif 'ScanMorningReport' in str(report):
                reportDate = report['Reports'][0]['ScanMorningReport']['Header']['Date']
                reportID = report['Reports'][0]['ScanMorningReport']['ReportAttributes']['ReportID']
                reportStatus = report['Reports'][0]['ScanMorningReport']['ReportAttributes']['ReportStatus']
                comment = report['Reports'][0]['ScanMorningReport']['Header']['PresentOp']

                # 'RapadMorningReport'
            elif 'RapadMorningReport' in str(report):
                reportDate = report['Reports'][0]['RapadMorningReport']['Header']['ReportDate']
                comment = report['Reports'][0]['RapadMorningReport']['Header']['OperationsActivityCurrent']
                comment24 = report['Reports'][0]['RapadMorningReport']['Header']['OperationsActivityNext24Hours']
                reportID = report['Reports'][0]['RapadMorningReport']['ReportAttributes']['ReportID']
                reportStatus = report['Reports'][0]['RapadMorningReport']['ReportAttributes']['ReportStatus']

                # 'PattersonMorningReportRevB'
            elif 'PattersonMorningReportRevB' in str(report):
                reportDate = report['Reports'][0]['PattersonMorningReportRevB']['Header']['ReportDate']
                comment = report['Reports'][0]['PattersonMorningReportRevB']['OperationsCasingDetails']['operations_at_report_time']
                if 'operations_next_24_hours' in report['Reports'][0]['PattersonMorningReportRevB']['OperationsCasingDetails']:
                    comment24 = report['Reports'][0]['PattersonMorningReportRevB']['OperationsCasingDetails']['operations_next_24_hours']
                reportID = report['Reports'][0]['PattersonMorningReportRevB']['ReportAttributes']['ReportID']
                reportStatus = report['Reports'][0]['PattersonMorningReportRevB']['ReportAttributes']['ReportStatus']

            else:
                reportDate =''
                comment = ''
                comment24 = ''
                reportID = ''
                reportStatus = ''

            dataResponse = [reportDate,comment,comment24,reportID,reportStatus]
        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        return html.Div(str(dataResponse))

    return ''

@app.callback(Output('output-value', 'children'), [Input('input-box', 'value')])
def update_value(value):
    global JobID
    JobID = value
    return html.Div(f"Input value: {JobID}")

def process_input_value():
    # Use the input_value in your processing logic
    if JobID:
        # Process the input_value
        result = f"Processed input value: {JobID}"
        return result
    else:
        return ""

@app.callback(Output('output-processed-value', 'children'), [Input('process-button', 'n_clicks')])
def process_input(n):
    if n and n > 0:
        result = process_input_value()
        return html.Div(result)
    else:
        return ''

app.layout = html.Div([
    html.Button('Update Token', id='update-token-button', n_clicks=0),
    html.Button('Get All Active Jobs', id='get-data-button', n_clicks=0),
    html.Button('Get Comments', id='get-comments-button', n_clicks=0),
    html.Button('Get Comments 2', id='get-comments2-button', n_clicks=0),
    html.Button('Get Comments 3', id='get-comments3-button', n_clicks=0),
    dcc.Input(id='input-box', type='text', placeholder='Enter a value'),
    html.Button('<-- Enter Job ID', id='process-button', n_clicks=0),
    html.Div(id='output-value'),
    html.Div(id='output-processed-value'),
    html.Div(id='output-container'),
    html.Div(id='data-container'),
    html.Div(id='comments-container'),
    html.Div(id='comments2-container'),
    html.Div(id='comments3-container')

])

if __name__ == "__main__":
    app.run_server(debug=True)
