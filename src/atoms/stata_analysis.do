// Estimate Model 1: Simple regression
regress exam_score previous_scores
estimates store model1

// Estimate Model 2: Multiple regression
regress exam_score hours_studied sleep_hours attendance_percent previous_scores
estimates store model2

// Create and save regression table using esttab
esttab model1 model2 using "assets/tables/table.tex", ///
    replace ///
    booktabs ///
    b(3) se(3) ///
    star(* 0.10 ** 0.05 *** 0.01) /// 
    stats(r2 N, fmt(3 0) labels("R-squared" "Observations")) ///
    nonotes addnotes("Standard errors in parentheses" "* p$<$0.10, ** p$<$0.05, *** p$<$0.01")

// Create coefficient plot
coefplot model1 model2, ///
    drop(_cons) ///
    xline(0) ///
    title("Coefficient Estimates with Confidence Intervals") ///
    legend(label(2 "Model 1") label(4 "Model 2"))

// Save figure using helper function
save_figure figure

// Display confirmation message
display "Analysis complete"
