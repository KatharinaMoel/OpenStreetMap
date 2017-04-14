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
            print('\nstreet types:\n')
            print(self.street_types)
            length_data = self.street_data.loc[ self.street_data['type'] == street_type ]['lengths']
        # compute desired statistic
        if stat == 'median':
            return length_data.median()
        if stat == 'average':
            return length_data.mean()
        if stat == 'max':
            stat_idx = length_data.idxmax()
        if stat == 'min':
            stat_idx = length_data.idxmin()
        stat_value = length_data[stat_idx]
        stat_row = self.street_data.loc[stat_idx, :]
        return stat_value, stat_idx, stat_row

    def plot(self, dpi = 1000):
        counter = 0
        count_file = 0
        plt.rc('lines', linewidth=0.1, color='black')
        fig = plt.figure()
        fig_plot = fig.add_subplot(1, 1, 1)
        fig_plot.axis([0, 0.5, 0, 0.2])
        fig_plot.axis('off')
        street_total = len(self.street_nodes)
        print('========================= NODE TOTAL: %s' % street_total)
        # get current time
        time_now = time.strftime('%d.%m.%Y_%H.%M.%S')
        for street_id in self.street_nodes:
            counter += 1
            x_coords = []
            y_coords = []
            for (lat, lon) in self.get_street_coords(street_id):
                print((lat, lon))
                (y_0, x_0) = (np.float_(lat) - self.minlat, np.float_(lon) - self.minlon)
                x_coords.append(x_0)
                y_coords.append(y_0)
                # compute back lists of separate coords
                fig_plot.plot(x_coords , y_coords, color = 'k')
                print(counter)
            if counter >= 10000:
                plt.savefig(('street-layer_%s_%s.png' % (time_now, count_file)),
                                dpi = dpi, linewith = 1, frameon=False, transparent = True)
                plt.close()
                fig = plt.figure()
                fig_plot = fig.add_subplot(1, 1, 1)
                fig_plot.axis('off')
                fig_plot.axis([0, 0.5, 0, 0.2])
                count_file +=1
                counter = 0
            processed_streets_count = counter + (count_file * 10000)
            print('>>>>> PROCESSED: %s' % processed_streets_count)
            if processed_streets_count == street_total:
                fig.savefig( ('street-layer_%s_%s.png' % (time_now, count_file)),
                                dpi = dpi, linewith = 1, frameon=False, transparent = False )   # bbox_inches='tight'
                plt.close()
                break
        print('\nThere are %s different street types' % len(self.street_types))
        self.merge_plots(time_now, count_file)

    def merge_plots(self, time_now, count_file):
        # open images
        src0 = Image.open('street-layer_%s_10.png' % time_now)
        src1 = Image.open('street-layer_%s_1.png' % time_now)
        src0.paste(src1, (0, 0), src1)
        src2 = Image.open('street-layer_%s_2.png' % time_now)
        src0.paste(src2, (0, 0), src2)
        src3 = Image.open('street-layer_%s_3.png' % time_now)
        src0.paste(src3, (0, 0), src3)
        src4 = Image.open('street-layer_%s_4.png' % time_now)
        src0.paste(src4, (0, 0), src4)
        src5 = Image.open('street-layer_%s_5.png' % time_now)
        src0.paste(src5, (0, 0), src5)
        src6 = Image.open('street-layer_%s_6.png' % time_now)
        src0.paste(src6, (0, 0), src6)
        src7 = Image.open('street-layer_%s_7.png' % time_now)
        src0.paste(src7, (0, 0), src7)
        src8 = Image.open('street-layer_%s_8.png' % time_now)
        src0.paste(src8, (0, 0), src8)
        src9 = Image.open('street-layer_%s_9.png' % time_now)
        src0.paste(src9, (0, 0), src9)
        src10 = Image.open('street-layer_%s_0.png' % time_now)
        # paste all images into the first
        src0.paste(src10, (0, 0), src10)
        src0.save('NEW_PASTE_%s.png' % time_now)

    def get_oneway_quota(self, street_type = None):
        if not street_type:
            oneway_data = self.street_data['is_oneway']
        else:
            assert(street_type in self.street_types)
            oneway_data = self.street_data.loc[self.street_data['type'] == street_type]['is_oneway']
        total_number = len(oneway_data)
        oneway_number = pd.to_numeric(oneway_data).sum()
        quota = oneway_number / total_number
        return quota, oneway_number, total_number

#############################################################################################################################

if __name__== '__main__':

    ###DEBUG
    #import pdb

    from Data import Data
    new_data = Data(csv_dir='./csv/')

    bounds, streets, node_coords = new_data.get_streets()

    ###TODO
    #street_nodes = node_coords

    test = Streets(bounds, streets, node_coords, add_length = True)
    #test_part = {k: test.street_nodes[k] for k in list(test.street_nodes.keys())[:10]}


    print('\nbounds:')
    print(bounds)
    print('\nstreet_nodes:')
    print({k: test.street_nodes[k] for k in list(test.street_nodes.keys())[:10]})
    print('\nstreet node set length:')
    print(len(test.street_nodes_set))
    print('\nnode coords:')
    print({k: test.node_coords[k] for k in list(test.node_coords.keys())[:10]})

    ###DEBUG
    #pdb.set_trace()

    print(test.street_data.head(10))
    print('\nMin:')
    print(test.analyze_street_lengths('min'))
    print('\nAverage:')
    print(test.analyze_street_lengths('average'))
    print('\nAverage RESIDENTIAL:')
    print(test.analyze_street_lengths('average', street_type='residential'))
    print('\nMax RESIDENTIAL')
    print(test.analyze_street_lengths('max', street_type='residential'))

    ###DEBUG
    #pdb.set_trace()

    test.plot()


