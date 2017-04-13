import pandas as pd
import numpy as np

class PostalAreas(object):

    def __init__(self, bounds, areas, area_nodes, area_lats, area_lons, cameras):
        self.minlat, self.minlon =  np.float_(bounds['minlat']), np.float_(bounds['minlon'])
        self.maxlat, self.maxlon =  np.float_(bounds['maxlat']), np.float_(bounds['maxlon'])
        self.areas = areas
        self.area_nodes = area_nodes
        self.area_lats, self.area_lons = area_lats, area_lons
        self.cameras = pd.DataFrame(cameras, index = ['lat', 'lon']).T
        print(self.cameras.head())
        self.cube_lats = pd.DataFrame( {postal: [ min(self.area_lats[postal]) , max(self.area_lats[postal]) ] for postal in areas.keys()},
                                       index = ['min', 'max'] ).T
        self.cube_lons = pd.DataFrame( {postal: [ min(self.area_lons[postal]) , max(self.area_lons[postal]) ] for postal in areas.keys()},
                                       index = ['min', 'max'] ).T

#############################################################################################################################

if __name__ == '__main__':

    from Data import Data
    new_data = Data(csv_dir='./csv/')

    cameras = new_data.get_cameras()
    bounds, areas, area_lats, area_lons = new_data.get_areas()
    print('bounds:')
    print(bounds)
    print('areas:')
    print({k: areas[k] for k in list(areas.keys())[:6]})
    print('area lats:')
    print({k: area_lats[k] for k in list(area_lats.keys())[:6]})
    print('area lons:')
    print({k: area_lons[k] for k in list(area_lons.keys())[:6]})
