import parseXML_singleRun as parser
import os.path

class Data(object):

    def __init__(self, xml = None, max_size = 1000000):
        # xml: path to .xml file
        if xml:
            self.bounds, self.cameras, self.street_nodes, self.streets, self.areas, self.area_lats, self.area_lons = parser.collect_data(xml, max_size)

    def get_cameras(self):
        return self.cameras

    def get_streets(self):
        street_data = self.bounds, self.streets, self.nodes
        return street_data

    def get_areas(self):
        return self.bounds, self.areas, self.area_nodes, self.area_lats, self.area_lons


##########################################################################################

if __name__== '__main__':

    testData = Data(xml='./map.xml')
