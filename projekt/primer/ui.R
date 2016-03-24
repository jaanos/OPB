library(shiny)

shinyUI(fluidPage(

  titlePanel("Banka"),

  sidebarLayout(
    sidebarPanel(
      sliderInput("min",
                  "Minimalni znesek transakcije:",
                  min = -10000,
                  max = 10000,
                  value = 1000)
    ),

    mainPanel(
      tableOutput("transakcije")
    )
  )
))
