#!/usr/bin/env python3

# Uvozimo potrebne knjižnice
from lxml import html
import requests
import csv

# Naslov, od koder pobiramo podatke
link = "https://sl.wikipedia.org/wiki/Seznam_ob%C4%8Din_v_Sloveniji"
stran = html.fromstring(requests.get(link).content)

# Preberemo prvo ustrezno tabelo
tabela = [[c.xpath(".//a")[0].text if i == 0 and c.text is None else c.text
          for i, c in enumerate(r.xpath("(th|td)"))] for r in
          stran.xpath("//table[@class='wikitable sortable']")[0].xpath("tr")]

# Nadomestimo decimalne vejice in ločila tisočic ter pretvorimo v števila
for i in range(1, len(tabela)):
    tabela[i][1] = float(tabela[i][1].replace(",", "."))
    tabela[i][2] = int(tabela[i][2].replace(".", ""))

# Zapišemo v datoteko CSV
with open("obcine.csv", "w") as f:
    w = csv.writer(f)
    w.writerows(tabela)
