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

    def get_cubes_to_cam(self, cam_id):
        # get lat and lon of camera
        cam_lat = self.cameras[cam_id]['lat']
        cam_lon = self.cameras[cam_id]['lon']
        # get rows of cube dataframes that 'contain' the camera in one direction (lat resp. lon)
        cubes_to_cam_lats = self.cube_lats.loc[ (self.cube_lats['min'] <= cam_lat) & (self.cube_lats['max'] >= cam_lat) ]
        cubes_to_cam_lons = self.cube_lons.loc[ (self.cube_lons['min'] <= cam_lon) & (self.cube_lons['max'] >= cam_lon) ]
        # get only rows of cubes that contain the camera in both lat and lon direction
        cubes_to_cam = cubes_to_cam_lats.loc[ cubes_to_cam_lats.intersection(cubes_to_cam_lons.index) ]
        # return the containing cubes (by index of postal codes)
        return cubes_to_cam.index

    def get_cams_to_cube(self, postal_code):
        # get min/ max lat and lon of cube to postal code area
        cube_min_lat, cube_max_lat = self.cube_lats.ix[postal_code, 'min'], self.cube_lats.ix[postal_code, 'max']
        cube_min_lon, cube_max_lon = self.cube_lons.ix[postal_code, 'min'], self.cube_lons.ix[postal_code, 'max']
        # get rows of cameras dataframes that are 'contained' in the cube in one direction (lat resp. lon)
        cams_to_cube_lats = self.cameras.ix[ (self.cameras['lat'] <= cube_max_lat) & (self.cameras['lat'] >= cube_max_lat) , 'lat']
        cams_to_cube_lons = self.cameras.ix[ (self.cameras['lon'] <= cube_max_lon) & (self.cameras['lon'] >= cube_max_lon) , 'lon']
        # get only rows of cameras that are contained in the cube in both lat and lon direction
        cams_to_cube = cams_to_cube_lats.loc[ cams_to_cube_lats.intersection(cams_to_cube_lons.index) ]
        # return the contained cameras (by index of its id)
        return cams_to_cube.index


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
