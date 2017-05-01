#! /usr/bin/env python

import os
import csv
import time
import xml.etree.ElementTree as et  # for reading the xml file
import numpy as np

def collect_data(FILE = 'map.xml', csv_output = True, max_size = 1000000):
    '''
    This function collects all required data out of an OpenStreetMap-like XML-file **FILE**.
    (correct path to it) and returns the following:
        - **bounds** dictionary, where keys are 'maxlat', 'maxlon', 'minlat' and 'minlon'
        - **cameras** dictionary in form {..., node_id: [node_lat, node_lon], ... } if node_id refers to a camera
        - **street_nodes** in form {..., node_id: [node_lat, node_lon], ... }} if node_id refers to a street defining node
        - **streets** dictionary in form {..., street_id: [type, is_oneway, postal_code, name, node1, node2, ..], ... }
        - **postal_areas** dictionary in form {..., postal_code: [way1, way2, way3, ..], ... }
        - **area_lats** dictionary in form {..., postal_code: [node1_lat, node2_lat, ..], ... }
        - **area_lons** dictionary in form {..., postal_code: [node1_lon, node2_lon, ..], ... }
    It parses the XML-code incrementally in character bunches of length **max_size**.
    If csv output is wanted, it creates a new directory csv_%time with including files bounds.csv, cameras.csv, street_nodes.csv,
    streets.csv, areas.csv, area_lats.csv, area_lons.csv.
    '''

    # init return Data-Types
    bounds = {}
    cameras = {}
    street_nodes = {}
    streets = {}
    postal_areas = {}
    area_lats = {}
    area_lons = {}

    # init other Data containers
    nodes = {}                          # collect all elements with tag 'node' here, dict of form {..., node_id: [node_lat, node_lon], ...}
    ways = {}                           # collect all elements with tag 'way' here, dict of form {..., way_id: [node1, node2, ..], ...}
    street_nodes_set = set()            # collect all node_ids that define any street in a set
    area_ways_set = set()               # collect all way_ids that define any postal area border in a set

    # get current time
    time_now = time.strftime('%d.%m.%Y_%H.%M.%S')

    # init parser
    parser = et.XMLPullParser(['start','end'])

    try:
        if csv_output:
            # set paths of the output files
            head, tail = os.path.split(FILE)
            out_dir = os.path.join(head, 'csv_%s' % time_now)
            print('outdir:\t %s' % out_dir)
            if not os.path.isdir(out_dir):
                os.mkdir(out_dir)
            csv_files = map( lambda x: os.path.join(out_dir, x),
                             ['bounds.csv', 'cameras.csv', 'street_nodes.csv', 'streets.csv', 'areas.csv',
                              'area_nodes.csv', 'area_lats.csv', 'area_lons.csv'] )
        else:
            csv_files = None
        with open(FILE, 'r') as read_file:
            for csv_file in csv_files:
                # open files to write
                head, tail = os.path.split(csv_file)
                if tail == 'bounds.csv':
                    bound_file = open(csv_file, 'w')
                if tail == 'cameras.csv':
                    camera_file = open(csv_file, 'w')
                if tail == 'street_nodes.csv':
                    street_node_file = open(csv_file, 'w')
                if tail == 'streets.csv':
                    street_file = open(csv_file, 'w')
                if tail == 'areas.csv':
                    area_file = open(csv_file, 'w')
                if tail == 'area_nodes.csv':
                    area_node_file = open(csv_file, 'w')
                if tail == 'area_lats.csv':
                    area_lat_file = open(csv_file, 'w')
                if tail == 'area_lons.csv':
                    area_lon_file = open(csv_file, 'w')

            if csv_output:
                # init csv files to write
                bounds_csv = csv.writer(bound_file, delimiter=',')
                camera_csv = csv.writer(camera_file, delimiter=',')
                street_node_csv = csv.writer(street_node_file, delimiter=',')
                street_csv = csv.writer(street_file, delimiter=',')
                area_csv = csv.writer(area_file, delimiter=',')
                area_node_csv = csv.writer(area_node_file, delimiter=',')
                area_lat_csv = csv.writer(area_lat_file, delimiter=',')
                area_lon_csv = csv.writer(area_lon_file, delimiter=',')

            # init parsing variables
            root = None
            relevancy_level = 0
            elements_to_delete = []
            case_dict = None

            # Start with parsing...
            rep = 0
            while True:
                test_func = None
                rep += 1

                line = read_file.read(max_size)
                if not line:
                    break

                # feed the parser
                parser.feed(line)

                # iterate through all parsed elements
                for event, elem in parser.read_events():

                    if root is None:
                        root = elem

                    # get bounds of the given map excerpt
                    if elem.tag == 'bounds':
                        if event == "end":
                            output = []
                            for key in ['minlat', 'minlon', 'maxlat', 'maxlon']:
                                bounds[key] = elem.attrib[key]
                                test_func = None
                                output.append(elem.attrib[key])
                            if csv_output:
                                bounds_csv.writerow(list(output))
                                bound_file.close()
                    # process all node tags with _get_camera
                    if elem.tag == 'node':
                        test_func = _get_camera
                        case_dict = cameras
                    # process all way tags with _get_street
                    if elem.tag == 'way':
                        test_func = _get_street
                        case_dict = streets
                    # process all relation tags with _get_relation
                    if elem.tag == 'relation':
                        test_func = _get_relation
                        case_dict = postal_areas

                    if not test_func:
                        continue

                    if event == "start":
                        if test_func(elem):
                            # in case of an opening tag:
                            # increase level if elem consists of required data (otherwise/ on level 0, elem would deleted before having read all its children)
                            relevancy_level += 1
                    if event == "end":
                        # in case of an ending tag:
                        # have processed complete element, so add it to list of elements to delete
                        elements_to_delete.append(elem)
                        if test_func(elem):
                            # decrease level if elem consists of required data (finally only on level 0, i. e. when all its child tags are read, it will be freed to delete)
                            relevancy_level -= 1
                            # get output of test_func
                            output = test_func(elem)
                            # in case of a node tag: get node coords and if it refers to a camera add it to the cameras dict
                            if case_dict == cameras:
                                is_cam = output[0]
                                id = output[1]
                                coordinates = output[2:]
                                nodes[id] = coordinates
                                if is_cam:
                                    assert(id not in cameras)
                                    cameras[id] = coordinates
                                    if csv_output:
                                        camera_csv.writerow(list(output[1:]))
                            # in case of a way tag:
                            elif case_dict == streets:
                                is_highway = output[0]
                                id = output[1]
                                info = output[2:6]
                                way_nodes = output[6:]
                                assert(id not in streets)
                                # only if way refers to a street add it to the streets dict
                                if is_highway:
                                    streets[id] = info + way_nodes
                                    # collect all nodes which are defining a street in the street_nodes set
                                    street_nodes_set.update(set(way_nodes))
                                    if csv_output:
                                        street_csv.writerow(list(output[1:]))
                                # otherwise save only its nodes in ways dict
                                ways[id] = way_nodes
                            # in case of a relation tag: get the bounding ways (ids) of an postal area and save it to the postal_areas dict
                            elif case_dict == postal_areas:
                                postal_code = output[0]
                                postal_ways = output[1:]
                                assert(postal_code not in postal_areas)
                                postal_areas[postal_code] = postal_ways
                                # collect all ways which are defining a postal area in the area_ways set
                                area_ways_set.update(set(postal_ways))
                                if csv_output:
                                    area_csv.writerow(list(output))

                # delete elements only when we parsed them completely (including all its children)
                if relevancy_level == 0:
                    for elem in elements_to_delete:
                        elem.clear()
                        if elem is not root:
                            root.clear()
                    elements_to_delete.clear()

        # save only coordinates of those nodes that are part of a street (and optional save it to file)
        street_nodes = { node_id: nodes[node_id] for node_id in street_nodes_set }
        street_nodes_set.clear()
        if csv_output:
            for (node_id, coords) in street_nodes.items():
                street_node_csv.writerow([node_id] + list(coords) )

        # save only coordinates of those nodes that are defining a postal area boundary (and optional save it to file)
        area_ways = { way_id: ways[way_id] for way_id in area_ways_set if way_id in ways}
        area_ways_set.clear()

        # get all nodes that define some postal area in a set
        area_nodes_set = set()
        for node_list in area_ways.values():
            area_nodes_set.update(node_list)
        area_ways.clear()

        # collect coordinates to all area nodes in dict
        area_nodes = { node_id: nodes[node_id] for node_id in area_nodes_set if node_id in nodes}
        area_nodes_set.clear()
        if csv_output:
            for (node_id, coords) in area_nodes.items():
                area_node_csv.writerow([node_id] + list(coords))

        # for each postal_code area save all its defining node coords in two dicts (separately for all its lat resp. lon coordinates)
        # form will be e. g. area_lats = { ..., postal_code1: [node1_lat, node2_lat, ..], ...}
        for postal_code in postal_areas.keys():
            print('\nNew Postal code: %s' % postal_code)
            postal_node_lats = []
            postal_node_lons = []
            for way_id in postal_areas[postal_code]:
                if way_id in ways:
                    way_lats = []
                    way_lons = []
                    for node_id in ways[way_id]:
                        if node_id in nodes:
                            node_lat, node_lon = nodes[node_id]
                            way_lats.append(np.float_(node_lat))
                            way_lons.append(np.float_(node_lon))
                        else:
                            print('\t\tNode %s NOT in ways[%s].' %(node_id, way_id))
                    postal_node_lats = list(postal_node_lats) + list(way_lats)
                    postal_node_lons = list(postal_node_lons) + list(way_lons)
            area_lats[postal_code] = postal_node_lats
            area_lons[postal_code] = postal_node_lons

            if csv_output:
                area_lat_csv.writerow( [postal_code] + list(area_lats[postal_code]) )
                area_lon_csv.writerow( [postal_code] + list(area_lons[postal_code]) )

        # close all opened files
        if csv_output:
            camera_file.close()
            street_node_file.close()
            street_file.close()
            area_file.close()
            area_node_file.close()
            area_lat_file.close()
            area_lon_file.close()

        # return required data
        return bounds, cameras, street_nodes, streets, postal_areas, area_nodes, area_lats, area_lons

    except MemoryError:
        print('Out of Memory.')

def _get_camera(elem):
    '''
    Input:
    * elem: xml element
    Output:
    * None if elem is no camera
    * (cam_id, cam_lat, cam_lon) else
    '''
    # only elements of type node are candidates for cameras
    if elem.tag == 'node':
        is_cam = False
        for child in elem:
            # test by node's tags and attributes if element is a cam
            if ( (child.tag == 'tag')
                    and (all( key in child.attrib for key in ('k', 'v') )) ):
                if ( (child.attrib['k'] == 'man_made')
                        and (child.attrib['v'] == 'surveillance') ):
                    # it is a cam
                    is_cam = True
        # get node data (id and coordinates)
        id = elem.attrib['id']
        lat = elem.attrib['lat']
        lon = elem.attrib['lon']
        # return the is_cam (Bool), id, lat and lon data of the cam
        return is_cam, id, np.float_(lat), np.float_(lon)
    else:
        # no cam
        return None

def _get_street(elem):
    '''
    Input:
    * elem: xml element
    Output:
    * None if elem is no way
    * If it is a way and even a highway/ street: (way_id, way_type, way_oneway, way_postal, way_name, node1, node2, ...)
    * If it is a way and no highway/ street: (way_id, node1, node2, ...)
    '''
    # only elements of type way are candidates for streets
    if elem.tag == 'way':
        is_highway = False
        highway_type = None
        is_oneway = 0
        postal_code = None
        name = None
        id = None
        way_nodes =[]
        for child in elem:
            if child.tag == 'nd':
                # collect all nodes of the way in way_nodes
                assert('ref' in child.attrib)
                way_nodes.append(child.attrib['ref'])
            # test by way's tags and attributes if element is a street
            if ( (child.tag == 'tag')
                    and (all( key in child.attrib for key in ('k', 'v') )) ):
                if child.attrib['k'] == 'highway':
                    # it is a highway/ street, get its street type
                    highway_type = child.attrib['v']
                    is_highway = True
                if is_highway:
                    # get additional data (name, is_oneway, postal_code) in case of a highway
                    if child.attrib['k'] == 'name':
                        name = child.attrib['v']
                    if ( 'oneway' in child.attrib.values() and (child.attrib['k'] == 'oneway')
                            and (child.attrib['v'] == 'yes') ):
                        # return the id, lat and long of the cam
                        is_oneway = 1
                    if ( 'postal_code' in child.attrib.values() and child.attrib['k'] == 'postal_code'):
                        postal_code = child.attrib['v']
        # independent of being a highway get element's id
        id = elem.attrib['id']
        if is_highway:
            # return all way data including all its nodes
            way_info = (is_highway, id, highway_type, is_oneway, postal_code, name) + tuple(way_nodes)
        else:
            # if it is no highway, return only is_highway (Bool), id and its corresponding nodes
            way_info = (is_highway, id, None, None, None, None) + tuple(way_nodes)
        way_nodes.clear()
        return way_info
    else:
        # no way
        return None

def _get_relation(elem):
    '''
    Input:
    * elem: xml element
    Output:
    * None if elem is no postal code area
    * (postal_code, way1, way2, ...) else
    '''
    # only elements of type relation are candidates for cameras
    if elem.tag == 'relation':
        buffer_ways =[]
        is_boundary = False
        postal_code = None
        for child in elem:
            # get all boundary ways of the area
            if child.tag == 'member':
                if ('type' in child.attrib and child.attrib['type'] == 'way'):
                    way_id = child.attrib['ref']
                    buffer_ways.append(way_id)
            # test by child's tags and attributes if element is a postal area
            if ( (child.tag == 'tag')
                    and (all( key in child.attrib for key in ('k', 'v') )) ):
                if child.attrib['k'] == 'boundary':
                    if child.attrib['v'] == 'postal_code':
                        # it is a postal area
                        is_boundary = True
                if is_boundary:
                    if child.attrib['k'] == 'postal_code':
                        postal_code = child.attrib['v']
        if postal_code:
            postal_info = (postal_code,) + tuple(buffer_ways)
            buffer_ways.clear()
            # return the postal area data
            return postal_info
        else:
            # no postal area
            return None
    else:
        # no cam
        return None

#####################################################################################################################

if __name__ == '__main__':

    collect_data()