// Data transformation: convert percentages to proportions
replace attendance_percent = attendance_percent / 100
replace previous_scores = previous_scores / 100
replace exam_score = exam_score / 100

// Display summary statistics
summarize, detail
