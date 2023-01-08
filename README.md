# splot
Script to plot sectors given a GNG sector file. Expects sectors in sectors.txt in main folder.

usage: splot.py [-h] [-a] [-s SCALE] [-l LEVELS LEVELS] [-g] [-n NEIGHBOURS] [-w AIRWAYS] [-c] [-y WAYPOINTS] [-f]
                [-d DOTTED]
                sectors

positional arguments:
  sectors               Sector IDs to be plotted as main, separated by ,e.g. HEF,GED,KIR

options:
  -h, --help            show this help message and exit
  
  -a, --annotate        If set, plots SI, Lower, Upper, annotation
  
  -s SCALE, --scale SCALE
                        Float, how far beyond primary sector to plot, default 0
                        
  -l LEVELS LEVELS, --levels LEVELS LEVELS
                        Tuple lower upper, levels for which to plot secondary sectors. If no tuple is given, the
                        minimum and maximum values of the primary sector are used.
                        
  -g, --group           Group flag, if set plots all sectors beginning with Sector otherwise only plots sectors with
                        given IDs
                        
  -n NEIGHBOURS, --neighbours NEIGHBOURS
                        Sector IDs of neighbouring sectors for which to add labels, either e.g. GIN1,GIN2 or GIN,TAU
                        
  -w AIRWAYS, --airways AIRWAYS
                        Airways to plot, separated by ,
                        
  -c, --copx            Add Copx table to plot
  
  -y WAYPOINTS, --waypoints WAYPOINTS
                        Waypoints to plot, separated by ,
                        
  -f, --coloured        If set, sectors have different colours
  
  -d DOTTED, --dotted DOTTED
                        Sector IDs (GIN1,GIN2 or GIN,TAU) of sectors to plot with dashed lines
