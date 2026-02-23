/* ==============================================================================
   Test: I/O helper functions work correctly
   
   This test verifies that:
   - save_figure creates a PDF file in assets/figures/
============================================================================== */

// Setup
clear all
set more off

// Load helper functions
do "src/lib/io.do"

// Test: save_figure works
display as text "Testing save_figure..."

// Create some test data
clear
set obs 10
generate x = rnormal()
generate y = rnormal()

// Create a scatter plot
scatter y x

// Save the figure (this should create assets/figures/test.pdf)
save_figure test

// Check if file was created
capture confirm file "assets/figures/test.pdf"
if _rc != 0 {
    display as error "save_figure failed: assets/figures/test.pdf not found"
    exit 601
}

// Clean up
erase "assets/figures/test.pdf"
display as result "✓ save_figure test passed!"

// All tests passed
display as result "✓ All I/O tests passed!"
