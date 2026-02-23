/* ==============================================================================
   I/O Helper Functions
   
   This script contains helper programs for saving figures and tables with
   sensible defaults for the project
============================================================================== */

*! Save a figure to file
*!
*! Saves figures to the assets/figures directory as a pdf, with
*! sensible defaults
*!
*! Syntax: save_figure name [, width(#) height(#)]
*!
*! name: The desired filename, without the .pdf extension
*! width: Output width; defaults to 6.2 inches (textwidth of ./tex/article)
*! height: Output height; defaults to 4 inches

program define save_figure
    syntax name [, width(real 6.2) height(real 4)]
    
    graph export "assets/figures/`namelist'.pdf", ///
        width(`width') height(`height') replace
end
