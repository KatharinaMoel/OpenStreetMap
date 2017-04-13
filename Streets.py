import pandas as pd
import numpy as np
import time

class Streets(object):

    def __init__(self, bounds, streets, node_coords, add_length = True):
        # street_info = {..., street_id: [street_type, is_oneway, street_postal_code, street_name], ...}
        street_info = {street_id: streets[street_id][:4] for street_id in streets.keys()}
        # street_nodes = {..., street_id: [node1, node2, ..], ...}
        street_nodes = {street_id: streets[street_id][4:] for street_id in streets.keys()}
        self.street_data = pd.DataFrame(street_info, index = ['type', 'is_oneway', 'postal_code', 'name']).T
        # collect all possible street types in a set
        self.street_types = set(self.street_data['type'])
        # collect all nodes that define any street in a set
        self.street_nodes = set()
        for node_list in self.streets.values():
            self.street_nodes.update(node_list)
        # collect the coordinates of all street nodes in a dict
        self.node_coords = {}
        for node in self.street_nodes:
            if not node in self.node_coords.keys():
                if (node in node_coords.keys()):
                    self.node_coords[node] = node_coords[node]
                else:
                    print('... Node not in input node_coords!')
            else:
                print('NODE already in node coords!!')
        # save min/ max coordinates of the map excerpt
        self.minlat, self.minlon =  np.float_(bounds['minlat']), np.float_(bounds['minlon'])
        self.maxlat, self.maxlon =  np.float_(bounds['maxlat']), np.float_(bounds['maxlon'])
        # optional: add column with street lengths to the street_data dataframe
        if add_length:
            self.street_data['lengths'] = self.street_data.index
            self.street_data['lengths'] = self.street_data['lengths'].apply(lambda x: self.get_street_length(x))

    def get_street_coords(self, street_id, as_lists = False):
        '''
        default: return single list of coordinate tuples for a single street with id way_id.
        if as_lists = True: return a list of two lists (separate lat-coordinates resp. lon-coordinates) for a single street with id way_id. '''
        assert(street_id in self.street_nodes)
        way_nodes = self.street_nodes[street_id]
        street_coords = []
        if as_lists:
            lat_coords = []
            lon_coords = []
        for node_id in way_nodes:
            if node_id in self.node_coords:
                node_lat, node_lon = self.node_coords[node_id]
            else:
                print('NO NODE ID in Node Coords: %s' %node_id)
                node_lat, node_lon = 0, 0
            if as_lists:
                lat_coords.append(node_lat)
                lon_coords.append(node_lon)
            else:
                street_coords.append( (node_lat, node_lon) )
        if as_lists:
            street_coords = [lat_coords, lon_coords]
        return street_coords

    def get_street_length(self, street_id):
        '''
        Compute and return the length of a street with id street_id.
        '''
        coords = self.get_street_coords(street_id)
        street_length = 0
        for n in range( len(coords)-1 ):
            diff_coords = np.subtract(np.float_(coords[n+1]), np.float_(coords[n]))
            path_length = np.sqrt( diff_coords[0]**2 + diff_coords[0]**2 )
            street_length += path_length
        return street_length

#############################################################################################################################

if __name__== '__main__':

    ###DEBUG
    import pdb

    from Data import Data
    new_data = Data(csv_dir='./csv/')

    bounds, streets, node_coords = new_data.get_streets()
    print('bounds:')
    print(bounds)
    print('streets:')
    print({k: streets[k] for k in list(streets.keys())[:6]})
    print('node set length:')
    print(len(street_nodes_set))
    print('node coords:')
    print({k: node_coords[k] for k in list(node_coords.keys())[:6]})

    ###DEBUG
    pdb.set_trace()

    test = Streets(bounds, streets, node_coords, add_length = True)
    #test_part = {k: test.street_nodes[k] for k in list(test.street_nodes.keys())[:10]}

    print('\n')
    print(test.street_data.head(10))



