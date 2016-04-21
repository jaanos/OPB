require(pxR)
require(dplyr)

# Branje datoteke v formatu px-axis
tab <- read.px("0955003S.px", encoding="cp1250")
df <- as.data.frame(tab)

names(df)
sapply(df, class)

# Ureditev tipov stolpca 
df$ŠTUDIJSKO.LETO <- df$ŠTUDIJSKO.LETO %>% as.character() %>% as.integer()

df$NAČIN %>% unique()
df$VRSTA.IZOBRAŽEVANJA %>% unique()
df$PODROČJA.IZOBRAŽEVANJA %>% unique()

# Število vrstic
df %>% nrow()

df$value %>% is.na() %>% which() %>% length()
length(which(is.na(df$value))) 

df %>% View
df %>% nrow
df %>% unique() %>% nrow

#df[[6]] <- NULL 
#df %>% unique() %>% nrow()
#df[[5]] <- NULL

head(df)

# Pojavil se je problem z interpretacijo vnešenih znakov v Windows ...
df[2,1] %>% as.character() == "Ženske"
  
df %>% filter(SPOL=="Ženske") %>% View


