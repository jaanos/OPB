library(shiny)
library(dplyr)
library(RPostgreSQL)

source("../auth_public.R")

shinyServer(function(input, output) {
  conn <- src_postgres(dbname = db, host = host,
                       user = user, password = password)
  tbl.transakcija <- tbl(conn, "transakcija")
  
  output$transakcije <- renderTable({
    t <- data.frame(arrange(filter(tbl.transakcija, znesek > input$min),
                            znesek))
    t$cas <- as.character(t$cas)
    t
  })

})
