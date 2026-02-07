```{r}
#| label: analysis

models <- list(
  lm(exam_score ~ previous_scores, data = df),
  lm(exam_score ~ hours_studied + sleep_hours + attendance_percent + previous_scores, data = df)
)
```