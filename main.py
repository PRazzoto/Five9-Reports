from five9 import Five9
import time
from gerar_pdf import data, create_pdf
from datetime import datetime
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# Initialize an empty list to store all transformed data records
all_transformed_data = []

# Reading the username and password
filename = r"credentials.txt"
with open(filename, "rt") as f:
    text = f.readline()
username, password = text.strip().split()

# Five9 parameters
client = Five9(username=username, password=password)
start = "2024-11-01T00:00:00.000"
end = "2024-11-30T23:59:59.000"


def getReturn():

    anapolis = 0
    araguaina = 0
    caldas = 0
    catalao = 0
    gurupi = 0
    jatai = 0
    mineiros = 0
    morrinhos = 0
    regional = 0
    rioVerde = 0
    valeCorumba = 0

    criteria = {"time": {"end": end, "start": start}}
    identifier = client.configuration.runReport(
        folderName="MyReports",
        reportName="Abandonadas",
        criteria=criteria,
    )
    time.sleep(2)
    get_results = client.configuration.getReportResult(identifier)

    formato = "%a, %d %b %Y %H:%M:%S"

    lista_abandonadas = []
    for record in get_results["records"]:
        record_data = record["values"]["data"]
        campanha = record_data[2]
        dt = datetime.strptime(record_data[1], formato)
        info = (record_data[0], dt.strftime("%d %b %Y"), campanha)
        lista_abandonadas.append(info)

    identifier = client.configuration.runReport(
        folderName="MyReports",
        reportName="Contacted",
        criteria=criteria,
    )
    time.sleep(2)
    get_results2 = client.configuration.getReportResult(identifier)

    lista_contactadas = []
    for record in get_results2["records"]:
        record_data = record["values"]["data"]
        campanha = record_data[2]
        dt = datetime.strptime(record_data[1], formato)
        info = (record_data[0], dt.strftime("%d %b %Y"), campanha)
        lista_contactadas.append(info)

    lista_abandonadas = set(lista_abandonadas)
    intersection = lista_abandonadas.intersection(lista_contactadas)
    intersection = list(intersection)

    for i in intersection:
        match i[2]:
            case "Unimed Anápolis":
                anapolis += 1
            case "Unimed Araguaína":
                araguaina += 1
            case "Unimed Caldas Novas":
                caldas += 1
            case "Unimed Catalão":
                catalao += 1
            case "Unimed Gurupi":
                gurupi += 1
            case "Unimed Jataí":
                jatai += 1
            case "Unimed Mineiros":
                mineiros += 1
            case "Unimed Morrinhos":
                morrinhos += 1
            case "Unimed Regional Sul":
                regional += 1
            case "Unimed Rio Verde":
                rioVerde += 1
            case "Unimed Vale do Corumbá":
                valeCorumba += 1
            case _:
                print("Erro")

    return {
        "Unimed Anápolis": anapolis,
        "Unimed Araguaína": araguaina,
        "Unimed Caldas Novas": caldas,
        "Unimed Catalão": catalao,
        "Unimed Gurupi": gurupi,
        "Unimed Jataí": jatai,
        "Unimed Mineiros": mineiros,
        "Unimed Morrinhos": morrinhos,
        "Unimed Regional Sul": regional,
        "Unimed Rio Verde": rioVerde,
        "Unimed Vale do Corumbá": valeCorumba,
    }


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
        return record_data[2]


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
aband = getRelatorioChamadas()
getTmaTme()
getRelatorioSLA()

retornos = getReturn()
for item in all_transformed_data:
    nome_campanha = item["nome"]
    if nome_campanha in retornos:
        # Adiciona a contagem retornada por getReturn() ao dicionário
        item["qtde"] = retornos[nome_campanha]
    else:
        # Caso não haja correspondência, pode deixar sem intersect_count ou
        # definir como 0
        item["qtde"] = 0

print(all_transformed_data)
# Append all data to the PDF generation list and create the PDF
data.extend(all_transformed_data)
create_pdf()
