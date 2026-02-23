/* ==============================================================================
   Test: Processed data has the right properties
   
   This test verifies that:
   - The processed data file exists
   - All variables are within expected ranges
============================================================================== */

// Setup
clear all
set more off

// Check if processed data exists
capture confirm file "data/processed/data.csv"
if _rc != 0 {
    display as error "File data/processed/data.csv not found; can't test it!"
    exit 601
}

// Load processed data
import delimited "data/processed/data.csv", clear

// Test: hours_studied >= 0
quietly summarize hours_studied
assert r(min) >= 0

// Test: sleep_hours >= 0
quietly summarize sleep_hours
assert r(min) >= 0

// Test: attendance_percent >= 0 and <= 1
quietly summarize attendance_percent
assert r(min) >= 0
assert r(max) <= 1

// Test: previous_scores >= 0 and <= 1
quietly summarize previous_scores
assert r(min) >= 0
assert r(max) <= 1

// Test: exam_score >= 0 and <= 1
quietly summarize exam_score
assert r(min) >= 0
assert r(max) <= 1

// All tests passed
display as result "✓ All data validation tests passed!"
