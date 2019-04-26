# Uvozimo potrebne knjižnice
library(rvest)
library(dplyr)
library(gsubfn)
library(readr)

# Naslov, od koder pobiramo podatke
link <- "https://sl.wikipedia.org/wiki/Seznam_ob%C4%8Din_v_Sloveniji"
stran <- html_session(link) %>% read_html()

# Preberemo prvo ustrezno tabelo
tabela <- stran %>% html_nodes(xpath="//table[@class='wikitable sortable']") %>%
  .[[1]] %>% html_table()

# Nadomestimo decimalne vejice in ločila tisočic ter pretvorimo v števila
sl <- locale(decimal_mark=",", grouping_mark=".")
for (i in c(2, 3, 5, 6)) {
  tabela[[i]] <- tabela[[i]] %>% parse_number(na="-", locale=sl)
}
tabela[[9]] <- tabela[[9]] %>% parse_character(na="-")

# Zapišemo v datoteko CSV
write_csv(tabela, "obcine.csv", na="")
