require(dplyr)

# Priklop na bazo. Vnesite ustrezno geslo.
geslo <- "telebajsek" 

db <- src_postgres(host="baza.fmf.uni-lj.si", 
                   dbname = "banka", user = "student", 
                   password = geslo)

# Priklop na tabele
tposta <- db %>% tbl("kraj")
toseba <- db %>% tbl("oseba")
tracun <- db %>% tbl("racun")
ttransakcija <- db %>% tbl("transakcija")

# Izvedba poizvedbe
db %>% tbl(sql("select posta from kraj")) %>% 
  data.frame %>% 
  View

# Pomožna funkcija
stolpci <- function(tab) {tab %>% data.frame %>% names}

# Izpis imen stolpcev tabel
tabele <- list(tposta, toseba, tracun, ttransakcija)
lapply(tabele, stolpci)

# JOIN narejen preko dplyr, ki se v resnici izvede preko SQL na bazi
toseba %>% inner_join(tracun, by=c("emso"="lastnik")) %>% 
  select(ime, priimek, stevilka) 

# S collect() naredimo dejansko poizvedbo. Rezultat lahko pretvorimo v data.frame
tposta %>% collect() %>% 
  data.frame %>% names

# Primer "WHERE" s pomočjo funkcije FILTER
tposta %>% select(posta) %>% filter(posta > 1000) 

