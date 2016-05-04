library(shiny)
library(dplyr)
library(RPostgreSQL)

source("../auth_public.R")

shinyServer(function(input, output) {
  # Vzpostavimo povezavo
  conn <- src_postgres(dbname = db, host = host,
                       user = user, password = password)
  # Pripravimo tabelo
  tbl.transakcija <- tbl(conn, "transakcija")
  
  output$transakcije <- renderTable({
    # Naredimo poizvedbo
    # x %>% f(y, ...) je ekvivalentno f(x, y, ...)
    t <- tbl.transakcija %>% filter(znesek > input$min) %>%
      arrange(znesek) %>% data.frame()
    # Čas izpišemo kot niz
    t$cas <- as.character(t$cas)
    # Vrnemo dobljeno razpredelnico
    t
  })

})
