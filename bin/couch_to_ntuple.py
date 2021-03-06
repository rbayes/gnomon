#!/usr/bin/env python

"""Create a ROOT file sorted by [document.number_run, document.number_event]"""

import argparse
import ROOT
import couchdb

import Configuration
import Logging

import random  # used to delay attachment post
import time    # used to delay attachment post

import logging  # FIXME TODO this and the scriptname buisiness should be new func
import sys

log = None  # Logger for this file

if __name__ == "__main__":
    my_description = 'Grab gnomon data from Couch and convert to ROOT file'
    parser = argparse.ArgumentParser(description=my_description)

    parser.add_argument('--name', '-n', help='DB in CouchDB for output',
                        type=str, required=True)
    parser.add_argument('--type', '-t', help='event type', type=str,
                        required=True)
    parser.add_argument('--logfileless', action='store_true',
                        help='this will disable writing out a log file')

    parser.add_argument('--run', help='run number',
                        type=int, required=True)

    Logging.addLogLevelOptionToArgs(parser)  # adds --log_level
    args = parser.parse_args()

    Logging.setupLogging(args.log_level, args.name)
    log = logging.getLogger('root').getChild(sys.argv[0].split('.')[0])
    log.debug('Commandline args: %s', str(args))

    Configuration.name = args.name
    Configuration.run = args.run

    config = Configuration.CouchConfiguration()
    db = config.getCurrentDB()

    # Note the key below: "[document.number_run, document.number_event]" which
    # is important because CouchDB will sort by this.  It's part of our ROOT
    # file specification that it be sorted like this.
    map_fun = """
function(doc) {
  if (doc.type == '%s' && doc.number_run == %d) {
    emit([doc.number_run, doc.number_event], 1);
}
}
""" % (args.type, args.run)

    log.debug('Map function: %s', map_fun)

    filename = 'root/gnomon_%s_%d_%s.root' % (args.name, args.run, args.type)
    file = ROOT.TFile(filename,
                      'RECREATE')
    t = ROOT.TTree('t', '')

    my_struct = None
    elements_3vector = ['x', 'y', 'z']

    for row in db.query(map_fun, include_docs=True):
        doc = row.doc

        log.info('Ntupling another %s', row.key)
        log.debug('Ntupling %s', str(doc))

        keys = [str(x) for x in doc.keys() if x[0] != '_']

        if my_struct == None:
            my_struct_code = 'struct MyStruct {'

            for key in keys:
                my_value = doc[key]
                my_type = type(my_value)

                log.debug('C++ing %s %s', key, my_value)

                if my_type == unicode:
                    my_struct_code += 'char %s[256];' % key
                elif my_type == int:
                    my_struct_code += 'int %s;' % key
                elif my_type == float:
                    my_struct_code += 'float %s;' % key
                elif my_type == dict:
                    log.debug('Type check: Seeing if dict type is 3-vector')
                    for element in elements_3vector:
                        if element not in my_value.keys():
                            raise ValueError('Dictionary is not 3-vector since missing %s',
                                             element)
                        my_struct_code += 'float %s_%s;' % (key, element)
                else:
                    raise ValueError('Unsupported type in JSON')

            my_struct_code += '};'
            log.info('Using following structure for converting Python: %s',
                     my_struct_code)

            ROOT.gROOT.ProcessLine(my_struct_code)

            from ROOT import MyStruct
            my_struct = MyStruct()

            for key in keys:
                my_value = doc[key]
                my_type = type(my_value)

                code = None
                if my_type == unicode:
                    code = 'C'
                elif my_type == int:
                    code = 'I'
                elif my_type == float:
                    code = 'F'
                elif my_type == dict:
                    # Special case, need three branches
                    code = 'F'
                    for element in elements_3vector:
                        new_key = '%s_%s' % (key, element)
                        t.Branch(new_key, ROOT.AddressOf(my_struct, new_key),
                                 '%s/%s' % (new_key, code))
                    continue
                else:
                    raise ValueError

                t.Branch(key, ROOT.AddressOf(my_struct, key),
                         '%s/%s' % (key, code))

        for key in keys:
            my_value = doc[key]

            if type(my_value) == dict:
                for element in elements_3vector:
                    new_key = '%s_%s' % (key, element)
                    setattr(my_struct, new_key, my_value[element])
            else:
                setattr(my_struct, key, my_value)

        t.Fill()

    t.Write()
    file.Close()

    # Do it in this order to avoid race condition
    try:
        db = config.getCouchDB().create('root')
    except couchdb.http.PreconditionFailed:
        db = config.getCouchDB()['root']

    # Avoid race condition, throws couchdb.http.ResourceConflict
    name = '%s_%d' % (args.name, args.run)
    try:
        doc = {'_id': name}
        db.save(doc)
    except couchdb.http.ResourceConflict:
        doc = db[name]

    try:
        db.delete_attachment(doc, filename)
    except:
        pass

    try:
        db.put_attachment(doc, open(filename, 'r'))
    except:
        # If fails, sleep... this is normally a Python issue of having:
        #   "Connection reset by peer"
        #
        log.error('Failed to upload ROOT file to CouchDB, retrying...')
        random.seed()
        wait_time = random.randint(60, 120)  # wait between 60 s and 120 s
        time.sleep(wait_time)
        db.put_attachment(doc, open(filename, 'r'))
