from flask import Flask, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Add a global variable to store the token
token = None

@app.route('/get_token', methods=['GET'])
def update_token():
    global token
    try:
        # Get the token
        token_response = requests.get(
            "https://data.welldata.net/api/v1/tokens/token",
            headers={"accept": "application/json","ApplicationID": "00258061-5290-41AA-A63D-0B84E00FDA11"},
            params={},
            auth=HTTPBasicAuth(username= "EDR_RestAPI", password="59ee#NK0sxtB"))

        token_response.raise_for_status()  # raise exception if the request failed

    except requests.exceptions.RequestException as err:
        return jsonify({"error": f"Error occurred while getting token: {err}"}), 400

    # Extract the token from the response
    token = token_response.json().get('token')  # replace 'token' with the correct field if different
    return jsonify({"token": token})

@app.route('/get_data', methods=['GET'])
def get_data():
    if token is None:
        return jsonify({"error": "No token available. Please generate a token first."}), 400

    try:
        # Make the data request with the token
        url = "https://data.welldata.net/api/v1/jobs?jobStatus=ActiveJobs&includeCapabilities=false&sort=id%20asc&take=1000&skip=0&total=true"
        data_response = requests.get(url, headers={
            'Token': token
        })

        data_response.raise_for_status()  # raise exception if the request failed

    except requests.exceptions.RequestException as err:
        return jsonify({"error": f"Error occurred while getting data: {err}"}), 400

    return jsonify(data_response.json())


@app.route('/get_comments', methods=['GET'])
def get_comments():
    if token is None:

        return update_token()

    try:
        # Make the data request with the token
        url = "https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2"
        data_response = requests.get(url, headers={
            'Token': token
        })
        # reportId = data_response.json()[0]['id']
        #
        # url2 = f"https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2/52934755"
        # data_response2 = requests.get(url2, headers={
        #     'Token': token
        # })

        data_response.raise_for_status()  # raise exception if the request failed

    except requests.exceptions.RequestException as err:
        return jsonify({"error": f"Error occurred while getting data: {err}"}), 400

    return jsonify(data_response.json())

@app.route('/get_comments2', methods=['GET'])  #get the reports
def get_comments2():
    if token is None:

        return update_token()

    try:
        # Make the data request with the token
        url = "https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2"
        data_response = requests.get(url, headers={
            'Token': token
        })
        values = data_response.json()
        wells = []
        reportIds = values['availableReports']
        for w in reportIds:
            wells.append(w)

        reportId = wells[0]['id']

        url2 = f"https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2/JSON?reportIds.ids={reportId}"
        data_response2 = requests.get(url2, headers={
            'Token': token
        })

        data_response.raise_for_status()  # raise exception if the request failed

    except requests.exceptions.RequestException as err:
        return jsonify({"error": f"Error occurred while getting data: {err}"}), 400

    return jsonify(data_response2.json())


@app.route('/get_comments3', methods=['GET'])  #get the reports
def get_comments3():
    if token is None:

        return update_token()

    try:
        # Make the data request with the token
        url = "https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2"
        data_response = requests.get(url, headers={
            'Token': token
        })
        values = data_response.json()
        wells = []
        reportIds = values['availableReports']
        for w in reportIds:
            wells.append(w)

        reportId = wells[0]['id']

        url2 = f"https://data.welldata.net/api/v1/jobs/net_181521/reports/daily/2/JSON?reportIds.ids={reportId}"
        data_response2 = requests.get(url2, headers={
            'Token': token
        })

        data_response.raise_for_status()  # raise exception if the request failed

        # Sort Morning Reports based on Type

        # Go through Id's and pull pdf downloads of reports
        report = data_response2.json()

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
            return jsonify('no morning report')

        # else:
        #     processedJobList.append([well, str(report['Reports'][0])])
        #     # print(processedJobList)
        #     continue

    except requests.exceptions.RequestException as err:
        return jsonify(), 400

    return jsonify([comment,comment24,reportID, reportDate])
    # return jsonify(comment)

if __name__ == "__main__":
    app.run(debug=True)
