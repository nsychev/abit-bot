from lxml.html import parse
from datetime import datetime, timedelta

def parse_abit():
    page = parse("http://abit.ifmo.ru/bachelor/statistics/applications/11000181/")
    
    table = page.getroot().xpath("..//table")[0]
    
    result = []
    
    for line in table.iter("tr"):
        if len(line.attrib) > 0:
            continue
        
        cells = list(line.iter("td"))
        name = cells[1].text
        reason = cells[4].text
        enrolled = "без вступительных" in reason
        try:
            points = int(cells[6].text)
        except:
            points = 311 if enrolled else 0
        
        result.append({"name": name, "enrolled": enrolled, "points": points})
    return result

def generate_message():
    data = parse_abit()
    
    enrolled = len([abit for abit in data if abit["enrolled"]])
    submitted = len(data)
    
    if len(data) < 120:
        passing = 0
    else:
        passing = data[119]["points"]
    
    return "Подано *{}* заявлений БВИ\nВсего *{}* заявлений\nПроходной балл — *{}*\n\n_Обновлено: {}_\nпо данным [abit.ifmo.ru](https://abit.ifmo.ru/bachelor/rating_rank/all/181/)".format(enrolled, submitted, passing, (datetime.now() + timedelta(hours=3)).strftime("%H:%M"))
