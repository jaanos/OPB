#!/usr/bin/env python3

# Uvozimo potrebne knjižnice
from lxml import html
import requests
import csv
import re

def text(tag):
    parts = [tag.text] + [text(t) for t in tag] + [tag.tail]
    if tag.tag == 'br':
        parts.insert(0, ' ')
    return re.sub(r'\s+', ' ', ''.join(filter(None, parts)))

# Naslov, od koder pobiramo podatke
link = "https://sl.wikipedia.org/wiki/Seznam_ob%C4%8Din_v_Sloveniji"
stran = html.fromstring(requests.get(link).content)

# Preberemo prvo ustrezno tabelo
tabela = [[text(c).replace('*', '').strip() for c in r.xpath("(th|td)")]
          for r in  stran.xpath("//table[@class='wikitable sortable']")[0]
                         .xpath("tr")]

# Nadomestimo decimalne vejice in ločila tisočic ter pretvorimo v števila
for r in tabela[1:]:
    r[1] = float(r[1].replace(",", "."))
    r[2] = int(r[2].replace(".", ""))

# Zapišemo v datoteko CSV
with open("obcine.csv", "w") as f:
    w = csv.writer(f)
    w.writerows(tabela)
