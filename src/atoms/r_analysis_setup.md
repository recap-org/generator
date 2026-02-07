```{r}
#| label: setup

# load packages; hide startup messages for pretty output
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(modelsummary))

# load functions
source("./src/lib/io.R")

# read data; we know the column types, so we can suppress the messages
df <- read_csv("./data/processed/data.csv", show_col_types = FALSE)
```