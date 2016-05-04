# Neposredno klicanje SQL ukazov v R
library(dplyr)
library(RPostgreSQL)

source("auth.R")

# Povežemo se z gonilnikom za PostgreSQL
drv <- dbDriver("PostgreSQL")      

# Uporabimo tryCatch,
# da prisilimo prekinitev povezave v primeru napake
tryCatch({
  # Vzpostavimo povezavo
  conn <- dbConnect(drv, dbname = db, host = host,
                    user = user, password = password)
  
  # Poizvedbo zgradimo s funkcijo build_sql
  # in izvedemo s funkcijo dbGetQuery
  znesek <- 1000
  t <- dbGetQuery(conn, build_sql("SELECT * FROM transakcija
                                  WHERE znesek >", znesek, "
                                  ORDER BY znesek, id"))
  # Rezultat dobimo kot razpredelnico (data frame)
  }, finally = {
    # Na koncu nujno prekinemo povezavo z bazo,
    # saj preveč odprtih povezav ne smemo imeti
    dbDisconnect(conn)
    # Koda v finally bloku se izvede, preden program konča z napako
  })
