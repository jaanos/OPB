require(dplyr)
require(DBI)
require(RPostgreSQL)

# Priklop na bazo. Vnesite ustrezno geslo.
geslo <- "telebajsek" 

db <- dbConnect(PostgreSQL(), host="baza.fmf.uni-lj.si", dbname="banka",
                user="student", password=geslo)

# Priklop na tabele
tposta <- db %>% tbl("kraj")
toseba <- db %>% tbl("oseba")
tracun <- db %>% tbl("racun")
ttransakcija <- db %>% tbl("transakcija")

# Izvedba poizvedbe
db %>% tbl(sql("select * from kraj")) %>% 
  data.frame %>% 
  View()

# Pomožna funkcija
stolpci <- . %>% data.frame() %>% names()

# Izpis imen stolpcev tabel
tabele <- list(tposta, toseba, tracun, ttransakcija)
lapply(tabele, stolpci)

# JOIN narejen preko dplyr, ki se v resnici izvede preko SQL na bazi
racuni <- toseba %>% inner_join(tracun, by=c("emso"="lastnik")) %>% 
  select(ime, priimek, stevilka) 

racuni %>% data.frame() %>% View()

# S collect() naredimo dejansko poizvedbo.
# Rezultat lahko pretvorimo v data.frame
tposta %>% collect() %>% 
  data.frame() %>% names()

# Primer "WHERE" s pomočjo funkcije FILTER
tposta %>% select(posta) %>% filter(posta > 5000) 

