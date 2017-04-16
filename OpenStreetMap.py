import argparse
import os.path

def parse_args(args):
    if args.command in ['parseXML', 'pa', 'parse']:
        command = 'parseXML'
        csv = args.csv
        xml_file = args.file
        size = int(args.max_size)
    elif args.command in ['streets', 'st']:
        command = 'streets'
        csv_dir = args.csv_dir
        print_types = args.print_types
        stat = args.lengths
        street_type = args.type
        plot = args.plot
        dpi = args.dpi
        oneway = args.oneway
    elif args.command in ['postal_areas', 'po', 'postals']:
        command = 'postal_areas'
        csv_dir = args.csv_dir
        cam_counts = args.cam_counts
        postal_area = args.area
    print('\nSpecified program:\n\t %s' % command)
    print('Used options to it are:')
    for arg in vars(args):
        if not arg == args.command:
            print('\t %s = %s' %(arg, getattr(args, arg)))
    if command == 'parseXML':
        parseXML_program(xml_file, size, csv)
    elif command == 'streets':
        if not any([print_types, stat, plot, oneway]):
            print("\nPlease specify at least one of the options of '--print_types', '--analyze_lengths', '--plot', '--oneway_quota'.\n")
            exit(1)
        streets_program(csv_dir, print_types, stat, street_type, plot, dpi, oneway)
    elif command == 'postal_areas':
        if not any([cam_counts, postal_area]):
            print("\nPlease specify at least one of the options of '--cam_counts', '--cams_to_area'.\n")
            exit(1)
        postals_program(cam_counts, postal_area)

def parseXML_program(xml_file, size, csv):
    from parseXML_singleRun import collect_data
    collect_data(FILE = xml_file, csv_output = csv, max_size = size)

def streets_program(csv_dir, print_types, stat, street_type, plot, dpi, oneway):
    from Streets import Streets
    from Data import Data
    new_data = Data(csv_dir=csv_dir)
    bounds, streets, node_coords = new_data.get_streets()
    new_streets = Streets(bounds, streets, node_coords, add_length = True)
    new_streets.run_streets(print_types, stat, street_type, plot, dpi, oneway)

def postals_program(csv_dir, cam_counts, postal_area):
    from PostalAreas import PostalAreas
    from Data import Data
    new_data = Data(csv_dir=csv_dir)
    cameras = new_data.get_cameras()
    bounds, areas, area_nodes, area_lats, area_lons = new_data.get_areas()
    new_postals = PostalAreas(bounds, areas, area_nodes, area_lats, area_lons, cameras)
    new_postals.run_postals(cam_counts, postal_area)

#############################################################################################################################################

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

xml_parser = subparsers.add_parser('parseXML', aliases=['pa','parse'])
xml_parser.add_argument('--file', '-f', default='map.xml', help='path to xml file to get data from.', dest='file')
xml_parser.add_argument('--max_size', '--size', '-s', default='1000000', help='How many characters should be parsed in one iteration.', dest='max_size')
xml_parser.add_argument('--csv_output', '--csv', '-c', action='store_false', help='Without this option the parsed data will not be saved to csv files.', dest='csv')

street_parser = subparsers.add_parser('streets', aliases=['st'])
street_parser.add_argument('--csv_dir', '--csv', '--c', nargs=1, default='./csv/', help='Specify the csv directory from which the data will be loaded.', dest='csv_dir')
street_parser.add_argument('--print_types', '-pt', action='store_true', default=False, help='With this option one can print all street_types.', dest='print_types')
street_parser.add_argument('--analyze_lengths', '--lengths', '-l', default=None, help="Value must be some statistic out of 'min', 'max', 'average', 'median'.", dest='lengths')
street_parser.add_argument('--street_type', '--type', '-t', default=None, help='Which street type to analyze.', dest='type')
street_parser.add_argument('--plot', '-p', action='store_true', default=False, help='With this option, all streets (or all of the given type) will be plotted to file.', dest='plot')
street_parser.add_argument('--dpi',  default=None, help='Which resolution to use for png image output.', dest='dpi')
street_parser.add_argument('--oneway_quota', '--oneway', '-o', default=False, action='store_true', help='With this option, the oneway_quota of all streets (or of all streets of the given type) will be printed.', dest='oneway')

postal_parser = subparsers.add_parser('postal_areas', aliases=['po', 'postals'])
postal_parser.add_argument('--csv_dir', '--csv', '-c', nargs=1, default='./csv/', help='Specify the csv directory from which the data will be loaded.', dest='csv_dir')
postal_parser.add_argument('--cam_counts', '--counts', '-co', default=False, action='store_true', help='With this option one can print a list a table of camera counts per postal area.', dest='cam_counts')
postal_parser.add_argument('--cams_to_area', '--area', '-a', default=None, help='With this option one can print a list of all cameras for the given postal area.', dest='area')

#############################################################################################################################################

if __name__ == '__main__':
    args = parser.parse_args()
    parse_args(args)
    #args.func(args)