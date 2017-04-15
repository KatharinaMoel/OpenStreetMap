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
        self.cube_lats = pd.DataFrame( {postal: [ min(self.area_lats[postal]) , max(self.area_lats[postal]) ] for postal in areas.keys()},
                                       index = ['min', 'max'] ).T
        self.cube_lons = pd.DataFrame( {postal: [ min(self.area_lons[postal]) , max(self.area_lons[postal]) ] for postal in areas.keys()},
                                       index = ['min', 'max'] ).T
        self.cams_to_areas = self.get_cams_to_areas()

    def get_cubes_to_cam(self, cam_id):
        # get lat and lon of camera
        cam_lat = self.cameras.ix[cam_id, 'lat']
        cam_lon = self.cameras.ix[cam_id, 'lon']
        # get rows of cube dataframes that 'contain' the camera in one direction (lat resp. lon)
        cubes_to_cam_lats = self.cube_lats[(self.cube_lats['min'] <= cam_lat) & (self.cube_lats['max'] >= cam_lat)]
        cubes_to_cam_lons = self.cube_lons[(self.cube_lons['min'] <= cam_lon) & (self.cube_lons['max'] >= cam_lon)]
        # get only rows of cubes that contain the camera in both lat and lon direction
        cubes_to_cam = cubes_to_cam_lats.loc[ cubes_to_cam_lats.index.intersection(cubes_to_cam_lons.index) ]
        # return the containing cubes (by index of postal codes)
        return cubes_to_cam.index

    def get_cams_to_cube(self, postal_code):
        # get min/ max lat and lon of cube to postal code area
        cube_min_lat, cube_max_lat = self.cube_lats.ix[postal_code, 'min'], self.cube_lats.ix[postal_code, 'max']
        cube_min_lon, cube_max_lon = self.cube_lons.ix[postal_code, 'min'], self.cube_lons.ix[postal_code, 'max']
        # get rows of cameras dataframes that are 'contained' in the cube in one direction (lat resp. lon)
        cams_to_cube_lats = self.cameras.ix[ (self.cameras['lat'] <= cube_max_lat) & (self.cameras['lat'] >= cube_min_lat) , 'lat']
        cams_to_cube_lons = self.cameras.ix[ (self.cameras['lon'] <= cube_max_lon) & (self.cameras['lon'] >= cube_min_lon) , 'lon']
        # get only rows of cameras that are contained in the cube in both lat and lon direction
        cams_to_cube = cams_to_cube_lats.loc[ cams_to_cube_lats.index.intersection(cams_to_cube_lons.index) ]
        # return the contained cameras (by index of its id)
        return cams_to_cube.index

    def get_cams_to_areas(self):
        cams_to_areas = dict.fromkeys( self.areas.keys(), [] )
        for postal_code in cams_to_areas:
            cams_in_area = self.get_cams_to_area(postal_code)
            cams_to_areas[postal_code] = cams_in_area

    def get_cams_to_area(self, postal_code):
        cams_in_area = []
        for cam_id in self.get_cams_to_cube(postal_code):
            cubes_to_cam = self.get_cubes_to_cam(cam_id)
            if len(cubes_to_cam) == 1:
                print('Camera has unique postal code cube, so it must be the postal area!')
                cams_in_area.append(cam_id)
            else:
                # cam coordinates for testing whether cam is in the area
                cam_coords = (self.cameras.ix[cam_id, 'lat'], self.cameras.ix[cam_id, 'lon'])
                cube_min_lat, cube_max_lat = self.cube_lats.ix[postal_code, 'min'], self.cube_lats.ix[postal_code, 'max']
                cube_min_lon, cube_max_lon = self.cube_lons.ix[postal_code, 'min'], self.cube_lons.ix[postal_code, 'max']
                eps = (np.float_(cube_max_lat) - np.float_(cube_min_lat)) / 100
                # some point outside the postal area from which we start a ray to the cam position
                outside_point = (np.float_(cube_min_lat) - eps, np.float_(cube_max_lat))
                area_lats = np.float_(self.area_lats[postal_code])
                area_lons = np.float_(self.area_lons[postal_code])
                node_total = len(area_lats)
                # coordinates of nodes that define the area
                node_coords = list(zip(area_lats, area_lons))
                #print('zip:')
                #print(list(node_coords))
                # count how many sides the ray intersects
                # if the counter is odd, the cam is inside the area
                intersection_counter = 0
                # check every border side if the ray intersects
                for i in range(node_total):
                    x = node_coords[i]
                    y = node_coords[((i+1) % (node_total))]
                    if self.rays_intersect(np.float_(x), np.float_(y), np.float_(outside_point), np.float_(cam_coords)):
                        intersection_counter += 1
                if intersection_counter % 2 == 1:
                    cams_in_area.append(cam_id)
        return cams_in_area

    def rays_intersect(self, ray1_node1, ray1_node2, ray2_node1, ray2_node2):
        # transform ray1 (as an infinite line) to linear standard form ax + by + c = 0
        a1 = ray1_node1[1] - ray1_node2[1]
        b1 = ray1_node2[0] - ray1_node1[0]
        c1 = ( ray1_node2[0] * ray1_node1[1] ) - ( ray1_node1[0] * ray1_node2[1] )
        # by plugging in nodes of ray2 in the linear equation, check whether points of ray2 are on this line or on different sides of it (i.e. result in different signs and so intersect it)
        result1 = (a1 * ray2_node1[0]) + (b1 * ray2_node1[1]) + c1
        result2 = (a1 * ray2_node1[0]) + (b1 * ray2_node1[1]) + c1
        # if both results have the same sign, both nodes of ray2 are on the same side of the line, i.e. cannot intersect it
        if (result1 * result2 > 0):
            return False
        # if the nodes are on different sides of the line, check whether ray2 intersects not only the infinite line of ray1, but even the finite length ray1
        # for testing do the same computations as above with roles of ray1 and ray2 interchanged
        a2 = ray2_node2[1] - ray2_node1[1]
        b2 = ray2_node1[0] - ray2_node2[0]
        c2 = ( ray2_node2[0] * ray2_node1[1] ) - ( ray2_node1[0] * ray2_node2[1] )
        # get results when plugging in points of ray1
        result1 = (a2 * ray1_node1[0]) + (b2 * ray1_node1[1]) + c2
        result2 = (a2 * ray1_node1[0]) + (b2 * ray1_node1[1]) + c2
        if (result1 * result2 > 0):
            return False
        # at this point, the both rays either intersect exactly once or they are collinear
        if ((a1 * b2) - (a2 * b1) == 0.0):
            # just handle the collinear case as no intersection
            return False
        # only remaining case is that the rays intersect
        return True

    def get_camera_count(self, postal_code):
        cams = self.cams_to_areas[postal_code]
        return len(cams)


#############################################################################################################################

if __name__ == '__main__':

    from Data import Data
    new_data = Data(csv_dir='./csv/')

    cameras = new_data.get_cameras()
    bounds, areas, area_nodes, area_lats, area_lons = new_data.get_areas()
    print('bounds:')
    print(bounds)
    print('areas:')
    print({k: areas[k] for k in list(areas.keys())[:6]})
    print('area lats:')
    print({k: area_lats[k] for k in list(area_lats.keys())[:6]})
    print('area lons:')
    print({k: area_lons[k] for k in list(area_lons.keys())[:6]})

    test = PostalAreas(bounds, areas, area_nodes, area_lats, area_lons, cameras)

    print('\nCamera DataFrame:')
    print(test.cameras.head())
    print('\nCube Lats DataFrame:')
    print(test.cube_lats.head())
    print('\nCube Lons DataFrame:')
    print(test.cube_lons.head())

    some_postal_codes = list(test.areas.keys())[:20]

    for i in range(3):
        current_postal = some_postal_codes[i]
        cams_to_cube = test.get_cams_to_cube(current_postal)
        print('\nPostal Code: %s' % current_postal)
        print('Cams to Cube:')
        print(cams_to_cube)

    some_cameras = list(test.cameras.index)[:3]
    print('Some cameras:')
    print(some_cameras)
    for i in range(3):
        current_cam = some_cameras[i]
        cubes_to_cam = test.get_cubes_to_cam(current_cam)
        print('\nCam: %s' % current_cam)
        print('Cubes to Cam:')
        print(cubes_to_cam)

    for i in range(20):
        current_postal = some_postal_codes[i]
        cams_to_area = test.get_cams_to_area(current_postal)
        print('\nPostal Code: %s' % current_postal)
        print('Cams to Area:')
        print(cams_to_area)


