# splot
Script to plot sectors given a GNG sector file. Expects sectors in sectors.txt in main folder.

usage: splot.py [-h] [-a ANNOTATE] [-s SCALE] [-l LEVELS LEVELS] sectors

positional arguments:
  sectors               Sector IDs to be plotted as main, separated by ,e.g. HEF,GED,KIR

optional arguments:
  -h, --help            show this help message and exit
  
  -a ANNOTATE, --annotate ANNOTATE
                        Boolean, whether to plot SI, Lower, Upper, default False
                        
  -s SCALE, --scale SCALE
                        Float, how far beyond primary sector to plot, default 0
                        
  -l LEVELS LEVELS, --levels LEVELS LEVELS
                        Tuple lower upper, levels for which to plot secondary sectors. If no tuple is given, the
                        minimum and maximum values of the primary sector are used.
