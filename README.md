# OpenStreetMap

You can run this program on the command line by 'python3 OpenStreetMap.py' with the following options:

    **parseXML**
        > usage: OpenStreetMap.py parseXML [-h] [--file FILE] [--max_size MAX_SIZE] [--csv_output]
        > optional arguments:
          -h, --help            show this help message and exit
          --file FILE, -f FILE  path to xml file to get data from.
          --max_size MAX_SIZE, --size MAX_SIZE, -s MAX_SIZE
                                How many characters should be parsed in one iteration.
          --csv_output, --csv, -c
                                Without this option the parsed data will not be saved
                                to csv files.
                                
    **streets**
        > usage: OpenStreetMap.py streets [-h] [--csv_dir CSV_DIR] [--print_types]
                                [--analyze_lengths LENGTHS]
                                [--street_type TYPE] [--plot] [--dpi DPI]
                                [--oneway_quota]
        > optional arguments:
          -h, --help            show this help message and exit
          --csv_dir CSV_DIR, --csv CSV_DIR, --c CSV_DIR
                                Specify the csv directory from which the data will be
                                loaded.
          --print_types, -pt    With this option one can print all street_types.
          --analyze_lengths LENGTHS, --lengths LENGTHS, -l LENGTHS
                                Value must be some statistic out of 'min', 'max',
                                'average', 'median'.
          --street_type TYPE, --type TYPE, -t TYPE
                                Which street type to analyze.
          --plot, -p            With this option, all streets (or all of the given
                                type) will be plotted to file.
          --dpi DPI             If --plot is used: Which resolution to use for png image output.
          --oneway_quota, --oneway, -o
                                With this option, the oneway_quota of all streets (or
                                of all streets of the given type) will be printed.
                                
    **postal_areas**
          > usage: OpenStreetMap.py postal_areas [-h] [--csv_dir CSV_DIR] [--cam_counts]
                                     [--cams_to_area AREA]
          > optional arguments:
            -h, --help            show this help message and exit
            --csv_dir CSV_DIR, --csv CSV_DIR, -c CSV_DIR
                                  Specify the csv directory from which the data will be
                                  loaded.
            --cam_counts, --counts, -co
                                  With this option one can print a list a table of
                                  camera counts per postal area.
            --cams_to_area AREA, --area AREA, -a AREA
                                  With this option one can print a list of all cameras
                                  for the given postal area.



      
