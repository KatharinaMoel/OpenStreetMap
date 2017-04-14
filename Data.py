import parseXML_singleRun as parser
import csv
import os.path

class Data(object):

    def __init__(self, xml = None, csv_dir = None, max_size = 1000000):
        # xml: path to .xml file
        # csv: path to csv directory
        assert(not (xml and csv_dir))
        if xml:
            self.bounds, self.cameras, self.street_nodes, self.streets, self.areas, self.area_lats, self.area_lons = parser.collect_data(xml, max_size)
        if csv:
            assert(os.path.isdir(csv_dir))
            self.bounds = {}
            self.cameras = {}
            self.street_nodes = {}
            self.streets = {}
            self.areas = {}
            self.area_nodes = {}
            self.area_lats = {}
            self.area_lons = {}
            csv_files = ['bounds.csv', 'cameras.csv', 'street_nodes.csv', 'streets.csv', 'areas.csv', 'area_nodes.csv', 'area_lats.csv', 'area_lons.csv']
            for csv_type in csv_files:
                self.load_csv(csv_dir, csv_type)

    def get_cameras(self):
        return self.cameras

    def get_streets(self):
        street_data = self.bounds, self.streets, self.street_nodes
        return street_data

    def get_areas(self):
        return self.bounds, self.areas, self.area_nodes, self.area_lats, self.area_lons

    def load_csv(self, csv_dir, csv_type):
        csv_file = os.path.join(csv_dir, csv_type)
        with open(csv_file, 'r') as read_file:
            reader = csv.reader(read_file, delimiter=',')
            for line in reader:
                if csv_type == 'bounds.csv':
                    keys = ['minlat', 'minlon', 'maxlat', 'maxlon']
                    for k in range(4):
                        self.bounds[keys[k]] = line[k]
                if csv_type == 'cameras.csv':
                    self.cameras[line[0]] = line[1:]
                if csv_type == 'street_nodes.csv':
                    self.street_nodes[line[0]] = line[1:]
                if csv_type == 'streets.csv':
                    self.streets[line[0]] = line[1:]
                if csv_type == 'areas.csv':
                    self.areas[line[0]] = line[1:]
                if csv_type == 'area_nodes.csv':
                    self.area_nodes[line[0]] = line[1:]
                if csv_type == 'area_lats.csv':
                    self.area_lats[line[0]] = line[1:]
                if csv_type == 'area_lons.csv':
                    self.area_lons[line[0]] = line[1:]

##########################################################################################

if __name__== '__main__':

    testData = Data(csv_dir='./csv/')
    _