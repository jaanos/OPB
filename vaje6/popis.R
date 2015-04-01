library(dplyr)    # Knjižnica za delo s podatki
library(RSQLite)  # Knjižnica za povezavo z bazo

# Datoteka, v kateri je baza
BAZA <- "popis.sqlite3"

# Povežemo se na obstoječo bazo
baza <- src_sqlite(BAZA)

# Pripravimo tabele
tbl.obcina <- tbl(baza, "obcina")
tbl.podatki <- tbl(baza, "podatki")
join <- select(mutate(inner_join(tbl.obcina, tbl.podatki,
                                 by = c("id" = "obcina")),
                      semester = leto %||% "/" %||% polletje),
               obcina = name, semester, spol, starost, stevilo)
skupine <- group_by(join, semester)

# Prebivalstvo Slovenije
summarise(skupine, stevilo = sum(stevilo))

# Mlajši od 30 let v Ljubljani
summarise(filter(skupine, name == "Ljubljana" & starost < 30),
          stevilo = sum(stevilo))

# Poiščimo nekaj občin z največjima deležema moških in žensk
t2011.2 <- group_by(filter(join, leto == 2011 & polletje == 2), obcina)
m2011.2 <- summarise(filter(t2011.2, spol == "Moški"),
                     moski = sum(stevilo))
z2011.2 <- summarise(filter(t2011.2, spol == "Ženske"),
                     zenske = sum(stevilo))
delez <- mutate(inner_join(m2011.2, z2011.2, by = "obcina"),
                delez.m = 1*moski/(moski+zenske))
head(arrange(delez, delez.m), n = 5)
head(arrange(delez, desc(delez.m)), n = 5)
