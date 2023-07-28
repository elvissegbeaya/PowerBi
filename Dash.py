import time
from datetime import date
import dash
import pandas as pd
import requests
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth
from tenacity import retry, stop_after_attempt, wait_fixed
# from cachetools import cached, TTLCache, Cache
from functools import lru_cache
import json
import sqlite3





class UnitV1(BaseModel):
    id: str
    name: str
    abbreviation: str


class Attribute(BaseModel):
    id: str
    mode: str





# Creating a database using SQL Lite
# Create a connection to the SQLite database
conn = sqlite3.connect('cache.db')

# Create a cursor to execute SQL commands
c = conn.cursor()

# Create a table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

# Define a function to get a value from the cache
def get_from_cache(key):
    with sqlite3.connect('cache.db') as conn:
        c = conn.cursor()
        c.execute("SELECT value FROM cache WHERE key=?", (key,))
        result = c.fetchone()
        return json.loads(result[0]) if result else None

def add_to_cache(key, value):
    with sqlite3.connect('cache.db') as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)", (key, json.dumps(value)))
        conn.commit()





@retry(stop=stop_after_attempt(4), wait=wait_fixed(2), retry_error_callback=lambda _: print("Retrying..."))
class HistoricalTimeRequest(BaseModel):
    attributes: list
    fromTime: str
    toTime: str
    interval: float
    isDifferential: bool = False

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_callback=lambda _: print("Retrying..."))
def historical_data_time(job_id: str, payload: HistoricalTimeRequest, token: any):
    """
    args
        job
        payload
    """
    uri = f'https://data.welldata.net/api/v1/jobs/{job_id}/data/time'
    header = {'token': token}
    r = requests.post(uri, data=payload, headers=header)
    # print(r.status_code)
    return r.json()


# app = Dash(__name__)
#
# # Initialize the Flask-Caching
# cache = Cache(app.server)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server





# Add a global variable to store the token and input value
token = None
JobID = None
header = ['Contractor', 'Rig Number', 'Operator', 'Well name', 'IADC', 'IADC 2', 'IADC3', 'HookLoad', 'PumpPressure', 'BlockHeight', 'PumpSpm', 'PumpSpm2', 'PumpSpm3',
          'RotaryTorque', 'TopDrive RPM',
          'TopDrive Torque', 'WOB', 'ROP-F', 'T-HL', 'BitPosition', 'BitStatus', 'SlipStatus', 'Comments', 'Next 24 Hr Comments', 'Report Id', 'Report Date']
# Variables
tmpAllJobs = []
lookup_table = {}
df = pd.DataFrame(tmpAllJobs)

# @app.callback(Output('output-container', 'children'), [Input('update-token-button', 'n_clicks')])
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


def update_lookup():
    global token
    if token is None:
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

        # Now that we have the token, we need to update the Lookup Table
        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed

            for w in values:
                # jobs.append([w['id'], w['assetInfoList'][0]['owner'], w['assetInfoList'][0]['name']])
                key = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                # key = w['siteInfoList'][0]['owner']
                value = w['id']
                lookup_table[key] = value
        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting token: {err}")

        return lookup_table
    else:
        # Now that we have the token, we need to update the Lookup Table
        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed

            for w in values:
                # jobs.append([w['id'], w['assetInfoList'][0]['owner'], w['assetInfoList'][0]['name']])
                key = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                # key = w['siteInfoList'][0]['owner']
                value = w['id']
                lookup_table[key] = value
        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting token: {err}")

        return lookup_table

    return ''

lookup_table = update_lookup()

@app.callback(Output('lookup-container', 'children'), [Input('lookup-table-button', 'n_clicks')])
def lookup_data(n):
    global lookup_table
    total = 0
    tmpJobs = []
    if n and n > 0:
        if token is None and lookup_table is None:
            lookup_table = update_lookup()
            return html.Div("No token available. Please generate a token first.")

        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed

            for w in values:
                # jobs.append([w['id'], w['assetInfoList'][0]['owner'], w['assetInfoList'][0]['name']])
                key = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                # key = w['siteInfoList'][0]['owner']
                value = w['id']
                lookup_table[key] = value

            # app.layout = html.Div([
            #     html.H1('Lookup Table'),
            #     html.Div([
            #         html.Div([html.Span(f"{key}: "), html.Span(value)])
            #         for key, value in sorted(lookup_table.items())
            #     ])
            # ])

            # app.layout = html.Div([
            #     html.H1('Lookup Table'),
            #     html.Div([
            #         html.Div(id='value-display', style={'marginRight': '20px'}),
            #         html.Div([
            #             html.Button(key, id={'type': 'dynamic-button', 'index': key},
            #                         style={'border': 'thin lightgrey solid',
            #                                'padding': '10px',
            #                                'margin': '10px',
            #                                'maxWidth': '100px',
            #                                'textOverflow': 'ellipsis',
            #                                'overflow': 'hidden',
            #                                'whiteSpace': 'nowrap'})
            #             for key in sorted(lookup_table.keys())
            #         ], style={'display': 'flex',
            #                   'grid-template-columns': 'repeat(minmax(200px, 1fr), minmax(200px, 1fr))',
            #                   'grid-gap': '10px',
            #                   'overflow': 'auto',
            #                   'maxHeight': '80vh'
            #                   })
            #     ], style={'display': 'flex','grid-template-columns': 'repeat(minmax(200px, 1fr), minmax(200px, 1fr))'}),
            # ])
            app.layout = html.Div([
                html.H1('Lookup Table'),
                html.Div([
                    dcc.Dropdown(
                        id='dropdown',
                        options=[{'label': key, 'value': key} for key in sorted(lookup_table.keys())],
                        placeholder='Select a key'
                    ),
                    html.Div(id='value-display'),
                ]),
            ])

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")

        return app.layout

    return ''



@app.callback(
    Output('value-display', 'children'),
    [Input('dropdown', 'value')]
)
def display_value(value):
    if value is None:
        return ''
    return html.Div(f"{value}: {lookup_table[value]}")

#
# @app.callback(
#     Output('value-display', 'children'),
#     [Input({'type': 'dynamic-button', 'index': ALL}, 'n_clicks')],
#     [State({'type': 'dynamic-button', 'index': ALL}, 'id')]
# )
# def display_value(n_clicks, ids):
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         raise PreventUpdate
#     else:
#         button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#         key = json.loads(button_id)['index']
#         return html.Div([html.B(f"{key}: "), html.Span(lookup_table[key])])


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
            #url = "https://data.welldata.net/api/v1/jobs?jobStatus=AllJobs&startDateMin=2022-12-15%205%3A13%3A48%20PM&includeCapabilities=false&sort=id%20asc&take=6500&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            data_response.raise_for_status()  # raise exception if the request failed
            for w in values:
                tmpJobs.append([w['id'],f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}",w['assetInfoList'][0]['owner'],w['siteInfoList'][0]['owner'],w['startDate'],w['firstDataDate'],w['lastDataDate']])

                # tmpJobs.append(w['id'])
                # tmpJobs.append(f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}")  # Rig Name
                # # set operator and contractor
                # tmpJobs.append(w['assetInfoList'][0]['owner'])  # Contractor
                # tmpJobs.append(w['siteInfoList'][0]['owner'])  # Operator
                # tmpJobs.append(w['startDate'])
                # tmpJobs.append(w['firstDataDate'])
                # tmpJobs.append(w['lastDataDate'])

            for w in values:
                key = f"{w['assetInfoList'][0]['owner']} {w['assetInfoList'][0]['name']}"
                value = w['id']
                lookup_table[key] = value


            header = ['Job Id','Rig','Contractor', 'Operator','Start Date', 'First Data Date', 'Last Data Date']
            df = pd.DataFrame(tmpJobs, columns = header)
            # df.to_excel('EndedJobs.xlsx', index=False)
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
    global token,lookup_table
    if n and n > 0:
        if token is None:
            return update_token(n)
        if lookup_table is None:
            return update_lookup()

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
    # Start the timer
    start_time = time.time()

    # Getting Attributes per job
    # Process Name, used for stateless process control

    # gets all active jobs data and Status
    today = date.today().strftime('%m-%d-%Y')
    today2 = date.today().strftime('%Y-%m-%d')
    datetime_string_from = today2 + 'T06:05:17'
    datetime_string_to = today2 + 'T06:06:17'

    attsLst = []
    jobsTimeBased =[]
    attribute_mapping = {}
    holder = []
    # JobsList = get_from_cache('ActiveJobList_pandas')
    JobsList =[]
    JobsList is None


    active_jobList= []



    if n and n > 0:
        if token is None:
            return update_token(n)


        try:
            # Make the data request with the token
            url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
            data_response = requests.get(url, headers={'Token': token})
            total = data_response.json()['total']
            values = data_response.json()['jobs']
            for w in values:
                active_jobList.append(w['id'])

        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")


        try:
            # if JobsList is None:
            if active_jobList is not None:
                JobsList = []
                for count, w in enumerate(active_jobList[0:10], start=1):
                    #check if record is already in database, if not update database with record
                    record = get_from_cache(w)
                    if record is None:
                        print(f"I'm working on job {w}, which is item {count} in the list of {len(active_jobList)}.")

                        #variables
                        # Define emojis as Unicode characters
                        emoji_check = u'\u2705'  # 3  # u'\u2705'  # ✅
                        emoji_exclamation = u'\u2757'  # 2  # u'\u2757'  # ❗
                        emoji_x = u'\u274C'  # 0  # u'\u274C'  # ❌

                        # Attribute Values
                        HookLoadbool = emoji_x
                        PumpPressurebool = emoji_x
                        BlockHeightbool = emoji_x
                        PumpSpmbool = emoji_x
                        PumpSpm2bool = emoji_x
                        PumpSpm3bool = emoji_x
                        RotaryTorquebool = emoji_x
                        BitPositionbool = emoji_x
                        BitStatusbool = emoji_x
                        SlipStatusbool = emoji_x
                        tpDriveRPM = emoji_x
                        comment = 'NA'
                        comment24 = 'NA'
                        reportDate = ''
                        reportID = ''
                        reportStatus = ''
                        realTime = emoji_x
                        tpDriveTorq = emoji_x
                        weightonBit = emoji_x
                        RP_Fast = emoji_x
                        tHookLoad = emoji_x

                        HookLoad_val = ''
                        PumpPressure_val = ''
                        BlockHeight_val = ''
                        PumpSpm_val = ''
                        PumpSpm2_val = ''
                        PumpSpm3_val = ''
                        RotaryTorque_val = ''
                        tpDriveRPM_val = ''
                        tpDriveTorq_val = ''
                        weightonBit_val = ''
                        BitPosition_val = ''
                        BitStatus_val = ''
                        RP_Fast_val = ''
                        SlipStatus_val = ''
                        tHookLoad_val = ''
                        Iadc_Rig_val = ''
                        Iadc2_Rig_val = ''
                        Iadc3_Rig_val = ''
                        reportDate = ''
                        comment = ''
                        comment24 = ''
                        reportID = ''
                        reportStatus = ''


                        # Get Job Info


                        url1 = f'https://data.welldata.net/api/v1/jobs/{w}'

                        #checking if results are in db, if not query and update db
                        values = get_from_cache(url1)
                        if values is None:
                            data_response = requests.get(url1, headers={'Token': token})
                            values = data_response.json()
                            add_to_cache(url1, values)

                        rig_name = f'{values["assetInfoList"][0]["owner"]} {values["assetInfoList"][0]["name"]}'
                        job_contractor = values["assetInfoList"][0]["owner"]
                        job_operator = values['siteInfoList'][0]['owner']
                        holder = []


                        # Getting Attributes
                        # Make the data request with the token
                        url = f"https://data.welldata.net/api/v1/jobs/{w}/attributes"
                        values = get_from_cache(url)
                        if values is None:
                            data_response = requests.get(url, headers={'Token': token})
                            data_response.raise_for_status()  # raise exception if the request failed
                            values = data_response.json()
                            add_to_cache(url, values)

                        mnemonics = ['HOOKLOAD_MAX', 'STP_PRS_1', 'BLOCK_POS', 'MP1_SPM', 'MP2_SPM', 'MP3_SPM', 'ROT_TORQUE', 'TD_SPEED','TD_TORQUE','WOB', 'BIT_DEPTH', 'BIT_ON_BTM', 'FAST_ROP_FT_HR', 'SLIPS_STAT','Trigger Hkld','IADC_RIG_ACTIVITY' , 'IADC_RIG_ACTIVITY2', 'IADC_RIG_ACTIVITY3']

                        for c in values['attributes']:
                            if c.get('hasData'):
                                if c.get('alias', {}).get('witsml_mnemonic') in mnemonics:
                                    attr = Attribute(id=c['id'], mode='Last')
                                    attsLst.append(attr)


                        hist_interval = 60
                        hist_payload = HistoricalTimeRequest(job_id=w,attributes=attsLst, toTime=datetime_string_to, fromTime=datetime_string_from, interval=hist_interval)
                        hist = historical_data_time(job_id=w, payload=hist_payload.model_dump_json(exclude_unset=True), token=token)

                        # Ensure that 'timeRecords' list contains at least one element before accessing it
                        if 'timeRecords' in hist and len(hist['timeRecords']) > 0:
                            # Extract 'values' from the first record in 'timeRecords'
                            timerecord_values = hist['timeRecords'][0]['values']
                        else:
                            # Handle the situation where 'timeRecords' is None or empty
                            print('No Time Records or empty timeRecords list')
                            continue

                        # Iterate over the 'attributes' list and map each attribute to its value from timestamp 0
                        for i, attribute in enumerate(hist['attributes']):
                            attribute_id = attribute['id']
                            # Ensure the index is within the 'timerecord_values' list bounds
                            attribute_value = timerecord_values[i][1] if i < len(timerecord_values) else ''
                            attribute_mapping[attribute_id] = attribute_value
                        # print(attribute_mapping)

                        attribute_results = {}
                        keys_to_check = ['HookLoad', 'PumpPressure', 'BlockHeight', 'PumpSpm', 'PumpSpm2', 'PumpSpm3', 'RotaryTorque', 'TopDrvRpm', 'TopDrvTorque', 'BitWeightQualified', 'BitPosition', 'BitStatus', 'FastRopFtHr', 'SlipStatus', 'TrigHkld']

                        for key, value in attribute_mapping.items():
                            if key in keys_to_check:
                                value = float(value)
                                if isinstance(value, float) or isinstance(value, int):

                                    if value == 0.00:
                                        attribute_results[key] = emoji_exclamation
                                    elif value > 0.00:
                                        attribute_results[key] = emoji_check
                                    else:
                                        attribute_results[key] = emoji_x
                            elif key in ['IadcRigActivity', 'IadcRigActivity2', 'RigActivity']:
                                attribute_results[key] = value


                        url = f"https://data.welldata.net/api/v1/jobs/{w}/reports/daily/2"
                        values = get_from_cache(url)
                        if values is None:
                            data_response = requests.get(url, headers={'Token': token})
                            data_response.raise_for_status()  # raise exception if the request failed
                            values = data_response.json()
                            add_to_cache(url, values)


                        for key, value in attribute_results:
                            print(attribute_results[key])
                        # if no values, print out current channels without the reports
                        if len(values) == 0:
                            holder.extend([
                                w, rig_name, job_contractor, job_operator,
                                str(attribute_results.get['IadcRigActivity']), str(attribute_results.get['IadcRigActivity2']), str(attribute_results.get['RigActivity']),
                                attribute_results.get['HookLoad'], attribute_results.get['PumpPressure'], attribute_results.get['BlockHeight'], attribute_results.get['PumpSpm'],
                                attribute_results.get['PumpSpm2'], attribute_results.get['PumpSpm3'], attribute_results.get['RotaryTorque'],
                                attribute_results.get['TopDrvRpm'], attribute_results.get['TopDrvTorque'], attribute_results.get['BitWeightQualified'], attribute_results.get['FastRopFtHr'],
                                attribute_results.get['TrigHkld'], attribute_results.get['BitPosition'], str(attribute_results.get['BitStatus']),
                                str(attribute_results.get['SlipStatus']), comment, comment24,
                                reportID, reportDate, reportStatus
                            ])

                            add_to_cache(w, holder)
                            JobsList.append(holder)

                            continue
                        wells = []
                        reportIds = values['availableReports']
                        for rep in reportIds:
                            wells.append(rep)

                        reportId = wells[0]['id']

                        url2 = f"https://data.welldata.net/api/v1/jobs/{w}/reports/daily/2/JSON?reportIds.ids={reportId}"

                        report = get_from_cache(url2)
                        if values is None:
                            data_response2 = requests.get(url2, headers={'Token': token})
                            data_response2.raise_for_status()  # raise exception if the request failed
                            # Sort Morning Reports based on Type
                            report = data_response2.json()
                            add_to_cache(url2, report)


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
                            reportDate = ''
                            comment = ''
                            comment24 = ''
                            reportID = ''
                            reportStatus = ''

                        holder.extend([
                            w, rig_name, job_contractor, job_operator,
                            str(attribute_results.get['IadcRigActivity']), str(attribute_results.get['IadcRigActivity2']), str(attribute_results.get['RigActivity']),
                            attribute_results.get['HookLoad'], attribute_results.get['PumpPressure'], attribute_results.get['BlockHeight'], attribute_results.get['PumpSpm'],
                            attribute_results.get['PumpSpm2'], attribute_results.get['PumpSpm3'], attribute_results.get['RotaryTorque'],
                            attribute_results.get['TopDrvRpm'], attribute_results.get['TopDrvTorque'], attribute_results.get['BitWeightQualified'],
                            attribute_results.get['FastRopFtHr'],
                            attribute_results.get['TrigHkld'], attribute_results.get['BitPosition'], str(attribute_results.get['BitStatus']),
                            str(attribute_results.get['SlipStatus']), comment, comment24,
                            reportID, reportDate, reportStatus
                        ])

                        add_to_cache(w, holder)
                        JobsList.append(holder)


                #saving JobList to DB
                add_to_cache('ActiveJobList_pandas', JobsList)



            header = ['Job Id', 'Rig', 'Contractor', 'Operator', 'IADC', 'IADC 2', 'IADC3', 'HookLoad', 'PumpPressure', 'BlockHeight', 'PumpSpm', 'PumpSpm2', 'PumpSpm3',
                      'RotaryTorque', 'TopDrive RPM', 'TopDrive Torque', 'WOB', 'ROP-F', 'T-HL', 'BitPosition', 'BitStatus', 'SlipStatus','comment', 'comment24', 'reportID','reportDate', 'reportStatus' ]

            df = pd.DataFrame(JobsList)
            df.columns = header

            # Stop the timer
            end_time = time.time()
            # Calculate the elapsed time
            elapsed_time = end_time - start_time
            print(f"The for loop took {elapsed_time:.6f} seconds.")


            return dash_table.DataTable(
                    id='Attributes ID',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                )


        except requests.exceptions.RequestException as err:
            return html.Div(f"Error occurred while getting data: {err}")


    # Return an empty Div if n is None or 0
    return html.Div()


# # Measure the execution time of the function
# execution_time = timeit.timeit("get_comments2(10)", globals=globals(), number=10)
#
# # Print the result
# print(f"Execution time: {execution_time:.6f} seconds")


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





########################################
########################################
# Additionatl Call Backs
#########################################
#########################################

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


@app.callback(
    Output('output-container', 'children'),
    [Input('update-token-button', 'n_clicks'),
     Input('lookup-table-button', 'n_clicks'),
     Input('get-data-button', 'n_clicks'),
     Input('get-comments-button', 'n_clicks'),
     Input('get-comments2-button', 'n_clicks'),
     Input('get-comments3-button', 'n_clicks'),
     Input('process-button', 'n_clicks'),
     Input('input-box', 'value')]
)
def update_output(n1, n2, n3, n4, n5, n6, n7, n8):
    # Get the ID of the button that triggered the callback
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'No button has been clicked yet'

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    # global JobID
    # global token
    # Do something based on which button was clicked
    if button_id == 'update-token-button' and n1 > 0:
        return update_token(n1)
    elif button_id == 'lookup-table-button' and n2 > 0:
        return lookup_data(n2)
    elif button_id == 'get-data-button' and n3 > 0:
        return get_data(n3)
    elif button_id == 'get-comments-button' and n4 > 0:
        return get_comments(n4)
    elif button_id == 'get-comments2-button' and n5 > 0:
         return get_comments2(n5)
    elif button_id == 'get-comments3-button' and n6 > 0:
        return get_comments3(n6)
    elif button_id == 'process-button' and n7 > 0:
        return update_value(n8)



app.layout2 = html.Div([
    html.Button('Get Comments', id='get-comments2-button'),
    html.Div(id='comments2-container')
])


app.layout = html.Div([
html.Div([
    html.Button('Update Token', id='update-token-button', n_clicks=0),
    html.Button('Lookup Table', id='lookup-table-button', n_clicks=0),
    html.Button('Get All Active Jobs', id='get-data-button', n_clicks=0),
    html.Button('Reportings', id='get-comments-button', n_clicks=0),
    html.Button('All Active Job Status', id='get-comments2-button', n_clicks=0),
    html.Button('EDR Only Status', id='get-comments3-button', n_clicks=0),

    dcc.Input(id='input-box', type='text', placeholder='Enter a Job Id'),
    html.Button(' ^^^ Submit Job Id ^^^', id='process-button', n_clicks=0)],style={
        'display': 'flex',
        'flexDirection': 'column',
        'width': '200px',
        'marginRight': '10px'
    }),
    html.Div(id='output-container'),
], style={
    'display': 'grid',
    'gridTemplateColumns': '2fr 2fr'
})

# Callback to update the output-div based on the input
@app.callback(
    Output('output-div', 'children'),
    [Input('input-value', 'value')]
)
def update_output(n7):
    # Call the expensive function to get the result
    result = get_comments2(n7)
    return result

if __name__ == "__main__":
    app.run_server(debug=True)
