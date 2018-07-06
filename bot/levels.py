import csv

data = {}
with open("levels.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        data[row[0]] = int(row[1])


def get(olymp):
    return data.get(olymp, 3)

