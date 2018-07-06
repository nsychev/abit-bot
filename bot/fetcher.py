from bs4 import BeautifulSoup
import requests


def get(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")

    table = soup.find("table")

    result = [[] for _ in range(len(table.find_all("tr")))]

    row_num = 0
    cell_num = 0

    for row in table.find_all("tr"):
        for cell in row.find_all("td"):
            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))

            while cell_num < len(result[row_num]) and result[row_num][cell_num] is not None:
                cell_num += 1

            for current_row_num in range(row_num, row_num + rowspan):
                if len(result) <= current_row_num:
                    result.append([])
                while cell_num >= len(result[current_row_num]):
                    result[current_row_num].append(None)
                for current_cell_num in range(cell_num, cell_num + colspan):
                    if len(result[current_row_num]) == current_cell_num:
                        result[current_row_num].append(str(cell.string))
                    else:
                        result[current_row_num][current_cell_num] = str(cell.string) if cell.string else None

            cell_num += colspan
        row_num += 1
        cell_num = 0

    return result

