import pandas as pd
import numpy as np
import time

class Streets(object):

    def __init__(self, bounds, streets, node_coords):
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

#############################################################################################################################

if __name__== '__main__':

    ###DEBUG
    import pdb

    from Data import Data
    new_data = Data()

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

    print(test.street_data.head(10))


