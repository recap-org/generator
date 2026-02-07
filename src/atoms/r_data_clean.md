```{r}
#| label: data-cleaning
#| tbl-cap: Data summary

# Data transformation: convert percentages to proportions
df <- df |> mutate(
  attendance_percent = attendance_percent / 100,
  previous_scores = previous_scores / 100,
  exam_score = exam_score / 100
)

# Show summary statistics for the dataset
datasummary_skim(
  df,
  fun_numeric = list(
    Mean = Mean,
    SD = SD
  ),
  escape = FALSE
)
```