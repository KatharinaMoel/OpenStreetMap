import os
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from PIL import Image

class Streets(object):

    def __init__(self, bounds, streets, node_coords, add_length = True):
        # street_info = {..., street_id: [street_type, is_oneway, street_postal_code, street_name], ...}
        street_info = {street_id: streets[street_id][:4] for street_id in streets.keys()}
        # street_nodes = {..., street_id: [node1, node2, ..], ...}
        street_nodes = {street_id: streets[street_id][4:] for street_id in streets.keys()}
        self.street_data = pd.DataFrame(street_info, index = ['type', 'is_oneway', 'postal_code', 'name']).T
        # collect all possible street types in a set
        self.street_types = set(self.street_data['type'])
        self.street_nodes = street_nodes
        # collect all nodes that define any street in a set
        self.street_nodes_set = set()
        for node_list in self.street_nodes.values():
            self.street_nodes_set.update(node_list)
        # collect the coordinates of all street nodes in a dict
        self.node_coords = {}
        for node in self.street_nodes_set:
            if not node in self.node_coords.keys():
                if (node in node_coords.keys()):
                    self.node_coords[node] = node_coords[node]
        # save min/ max coordinates of the map excerpt
        self.minlat, self.minlon =  np.float_(bounds['minlat']), np.float_(bounds['minlon'])
        self.maxlat, self.maxlon =  np.float_(bounds['maxlat']), np.float_(bounds['maxlon'])
        # optional: add column with street lengths to the street_data dataframe
        if add_length:
            self.street_data['lengths'] = self.street_data.index
            self.street_data['lengths'] = self.street_data['lengths'].apply(lambda x: self.get_street_length(x))

    def print_street_types(self):
        print('Possible street types are...\n')
        print(self.street_types)

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

    def analyze_street_lengths(self, stat, street_type = None):
        '''
        Compute and return a specific statistic of street lengths.
        stat: which statistic to use, possibilities: 'max', 'min', 'median', 'average'.
        street_type: optional, compute statistic only for the desired street types.
        '''
        assert(stat in ['max', 'min', 'median', 'average'])
        if not street_type:
            # use complete list of streets independent of their types
            length_data = self.street_data['lengths']
        else:
            # use only list of streets that are of the given type
            assert(street_type in self.street_types)
            length_data = self.street_data.loc[ self.street_data['type'] == street_type ]['lengths']
        # compute desired statistic
        if stat == 'median':
            result = length_data.median()
            print('The median of street lengths is %s.\n' %result)
            return result
        if stat == 'average':
            result = length_data.mean()
            print('The average of street lengths is %s.\n' %result)
            return result
        if stat == 'max':
            stat_idx = length_data.idxmax()
        if stat == 'min':
            stat_idx = length_data.idxmin()
        stat_value = length_data[stat_idx]
        stat_row = self.street_data.loc[stat_idx, :]
        print('\nThe result of computing %s of street lengths is %s.\n' %(stat, stat_value))
        return stat_value, stat_idx, stat_row

    def plot(self, street_type = None, dpi = 200):
        print('\nPlotting streets...')
        counter = 0
        count_file = 0
        plt.rc('lines', linewidth=0.1, color='black')
        fig = plt.figure()
        fig_plot = fig.add_subplot(1, 1, 1)
        fig_plot.axis([0, 0.5, 0, 0.2])
        fig_plot.axis('off')
        if street_type:
            assert(street_type in self.street_types)
            street_ids = list(self.street_data.loc[ self.street_data['type'] == street_type ].index)
            street_nodes = { id: self.street_nodes[id] for id in street_ids }
        else:
            street_nodes = self.street_nodes
        street_total = len(street_nodes)
        # get current time
        time_now = time.strftime('%d.%m.%Y_%H.%M.%S')
        # set paths of the temporary directory to store single images
        out_dir = os.path.join('./', 'images/')
        print('outdir:\t %s' % out_dir)
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        for street_id in street_nodes:
            counter += 1
            x_coords = []
            y_coords = []
            for (lat, lon) in self.get_street_coords(street_id):
                (y_0, x_0) = (np.float_(lat) - self.minlat, np.float_(lon) - self.minlon)
                x_coords.append(x_0)
                y_coords.append(y_0)
            fig_plot.plot(x_coords , y_coords, color = 'k')
            if counter >= 10000:
                plt.savefig( (os.path.join('./images/', 'street-layer_%s_%s.png' % (time_now, count_file))),
                                dpi = dpi, linewith = 1, frameon=False, transparent = True)
                plt.close()
                fig = plt.figure()
                fig_plot = fig.add_subplot(1, 1, 1)
                fig_plot.axis('off')
                fig_plot.axis([0, 0.5, 0, 0.2])
                count_file +=1
                counter = 0
            processed_streets_count = counter + (count_file * 10000)
            if processed_streets_count == street_total:
                fig.savefig( (os.path.join('./images/','street-layer_%s_%s.png' % (time_now, count_file))),
                                dpi = dpi, linewith = 1, frameon=False, transparent = False )   # bbox_inches='tight'
                plt.close()
                break
        self.merge_plots(time_now, count_file)
        print("Saving street image to file 'Streets_%s.png'..." % time_now)
        for k in range(count_file + 1):
            current_file = os.path.join('./images/','street-layer_%s_%s.png' % (time_now, k))
            if os.path.exists(current_file):
                os.remove(current_file)
        print('Done.')
        return os.path.join('./images/', 'Streets_%s.png' % time_now)

    def merge_plots(self, time_now, count_file):
        # open images
        src0 = Image.open(os.path.join('./images/','street-layer_%s_%s.png' % (time_now, count_file)))
        for k in range(count_file - 1):
            src1 = Image.open(os.path.join('./images/','street-layer_%s_%s.png' % (time_now, k)))
            src0.paste(src1, (0, 0), src1)
        src0.save(os.path.join('./images/', 'Streets_%s.png' % time_now))

    def get_oneway_quota(self, street_type = None):
        if not street_type:
            oneway_data = self.street_data['is_oneway']
        else:
            assert(street_type in self.street_types)
            oneway_data = self.street_data.loc[self.street_data['type'] == street_type]['is_oneway']
        total_number = len(oneway_data)
        # depending on the used pandas version, two different functions must be called to convert values of oneway_data to int
        if pd.__version__ < str(0.17):
            oneway_number = oneway_data.convert_objects(convert_numeric=True).sum()
        else:
            oneway_number = pd.to_numeric(oneway_data).sum()
        quota = oneway_number / total_number
        print('Oneway quota is %s %%.\n' % (quota*100))
        print('The total count of oneway streets is %s out of %s streets in total.' %(oneway_number, total_number))
        return quota, oneway_number, total_number

    def run_streets(self, print_types=None, stat=None, street_type=None, plot=False, dpi=None, oneway=False):
        if street_type:
            print('\nChosen street_type is %s' %street_type)
        else:
            print('\nStreet type will refer to all streets.\n')
        if print_types:
            self.print_street_types()
        if stat:
            if not stat in ['max', 'min', 'median', 'average']:
                print("Given statistic %s is not valid. Use one of 'max', 'min', 'mean', 'average'.\n")
            self.analyze_street_lengths(stat, street_type)
        if plot:
            self.plot(street_type, dpi)
        if oneway:
            self.get_oneway_quota(street_type)

#############################################################################################################################

if __name__== '__main__':

        from Data import Data
        new_data = Data(csv_dir='./csv/')
        bounds, streets, node_coords = new_data.get_streets()
        new_streets = Streets(bounds, streets, node_coords, add_length = True)

        print('MAIN FUNCTION !!!')
        print('\nbounds:')
        print(bounds)
        print('\nstreet_nodes:')
        print({k: new_streets.street_nodes[k] for k in list(new_streets.street_nodes.keys())[:10]})
        print('\nstreet node set length:')
        print(len(new_streets.street_nodes_set))
        print('\nnode coords:')
        print({k: new_streets.node_coords[k] for k in list(new_streets.node_coords.keys())[:10]})
        print(new_streets.street_data.head(10))
        print('\nMin:')
        print(new_streets.analyze_street_lengths('min'))
        print('\nAverage:')
        print(new_streets.analyze_street_lengths('average'))
        print('\nAverage RESIDENTIAL:')
        print(new_streets.analyze_street_lengths('average', street_type='residential'))
        print('\nMax RESIDENTIAL')
        print(new_streets.analyze_street_lengths('max', street_type='residential'))
        print('\n\n')
        print(new_streets.get_oneway_quota())
        print('\n\n')

        new_streets.plot(street_type='secondary')



