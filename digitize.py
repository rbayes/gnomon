#!/usr/bin/env python
# system libraries
import sys
import argparse
import logging
import os
import random

# gnomon
import Configuration
import Logging
import Digitizer

log = None  #  Logger for this file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='digitize the VLENF')
    parser.add_argument('--name', '-n', help='DB in CouchDB for output',
                        type=str, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--runs', '-r', metavar='N', type=int, nargs='+',
                       help='run(s) to process')
    group.add_argument('--all', '-a', action='store_true',
                       help='process all runs')
    
    parser.add_argument('--logfileless', action='store_true',
                        help='this will disable writing out a log file')

    Logging.addLogLevelOptionToArgs(parser)  #  adds --log_level
    args = parser.parse_args()

    Logging.setupLogging(args.log_level, args.name, logfileless=args.logfileless)
    log = logging.getLogger('root').getChild('simulate')
    log.debug('Commandline args: %s', str(args))

    random.seed()

    # Configuration.run not used
    Configuration.name = args.name
    
    config = Configuration.CouchConfiguration(warn_if_exists = True)
    db = config.getCurrentDB()

    if args.all:
        log.info('Runs: Using all runs in %s', args.name)
        addition = ''
    else:
        log.info('Runs: Using the following runs')
        for run in args.runs:
            log.info('\t%d', run)
        addition = 'if('
        run_conditions = ['doc.run == %d' % run for run in args.runs]
        addition += " || ".join(run_conditions)
        addition += ')'

    map_fun = """
function(doc) {
if (doc.type == 'mchit') {
%s
emit(1, 1);
}
}
""" % (addition)

    red_fun = """
function(keys, values, rereduce) {
return sum(values);
}
"""
    for row in db.query(map_fun, red_fun):
        log.warning('This process will digitize %d mchits', row.value)

    map_fun = """
function(doc) {
emit(doc.number_run, 1);
}"""

    red_fun = """
function(keys, values, rereduce) {
return sum(values);
}"""

    digitizer = Digitizer.VlenfSimpleDigitizer()

    for row in db.query(map_fun, red_fun, group=True):
        run = row.key
        log.info('Digitizing run %d', run)
        log.debug('There are %d mchits in run %d', row.value, run)

        digitizer.ProcessEvent(run)


        

