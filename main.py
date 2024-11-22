from five9 import Five9
import time
from gerar_pdf import data, create_pdf

# Initialize an empty list to store all transformed data records
all_transformed_data = []

# Reading the username and password
filename = r"credentials.txt"
with open(filename, "rt") as f:
    text = f.readline()
username, password = text.strip().split()

# Five9 parameters
client = Five9(username=username, password=password)
start = "2024-10-01T00:00:00.000"
end = "2024-10-31T23:59:59.000"


def getRelatorioChamadas():
    criteria = {"time": {"end": end, "start": start}}
    identifier = client.configuration.runReport(
        folderName="MyReports",
        reportName="Relatório Chamadas",
        criteria=criteria,
    )
    time.sleep(2)
    get_results = client.configuration.getReportResult(identifier)

    for record in get_results["records"]:
        record_data = record["values"]["data"]
        if record_data[3] is None:
            record_data[3] = 0
        # Initialize transformed data for each record
        transformed_data = {
            "nome": record_data[0],
            "total_atend": int(record_data[1]) if record_data[1] else 0,
            "total": int(record_data[4]) if record_data[4] else 0,
            "aban": (
                round(float(record_data[2]), 2) if record_data[2] is not None else 0
            ),
            "aban_percent": (
                round(float(record_data[2]) / float(record_data[1]), 2)
                if record_data[2] and record_data[1]
                else 0
            ),
            # Adding placeholders for fields from other reports
            "tma": "00:00:00",
            "tme": "00:00:00",
            "sl": "N/A",
        }
        all_transformed_data.append(transformed_data)


def getTmaTme():
    criteria = {"time": {"end": end, "start": start}}
    identifier = client.configuration.runReport(
        folderName="MyReports",
        reportName="Relatório Chamadas (TMA e TME)",
        criteria=criteria,
    )
    time.sleep(2)
    get_results_2 = client.configuration.getReportResult(identifier)

    for idx, record in enumerate(get_results_2["records"]):
        record_data_2 = record["values"]["data"]
        # Update the respective record in the list with TMA and TME
        if idx < len(all_transformed_data):
            all_transformed_data[idx].update(
                {
                    "tma": (
                        record_data_2[3] if record_data_2[3] is not None else "00:00:00"
                    ),
                    "tme": (
                        record_data_2[4] if record_data_2[4] is not None else "00:00:00"
                    ),
                }
            )


def getRelatorioSLA():
    criteria = {"time": {"end": end, "start": start}}
    identifier = client.configuration.runReport(
        folderName="MyReports",
        reportName="Relatório com o SLA",
        criteria=criteria,
    )
    time.sleep(2)
    get_results_3 = client.configuration.getReportResult(identifier)

    for idx, record in enumerate(get_results_3["records"]):
        record_data_3 = record["values"]["data"]
        # Update the respective record in the list with atend_esp and sl
        if idx < len(all_transformed_data):
            all_transformed_data[idx].update(
                {
                    "sl": record_data_3[2] if record_data_3[2] else "N/A",
                }
            )


# Call functions to gather data from the reports
getRelatorioChamadas()
getTmaTme()
getRelatorioSLA()

# Append all data to the PDF generation list and create the PDF
data.extend(all_transformed_data)
create_pdf()
