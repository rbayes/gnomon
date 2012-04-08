import tempfile
import sys
import os
import time
import couchdb
import random
import batch_queue_config

servers = ['http://gnomon:balls@tasd.fnal.gov:5984/',
           'http://gnomon:harry@gnomon.iriscouch.com/',
           'http://gnomon:balls@172.16.84.2:8080/']

number_of_events = 1000

flags = '--log_level WARNING --logfileless'

random.seed()

for momentum in batch_queue_config.momenta:
    for pid in batch_queue_config.pids:
        for polarity in ['-', '+']:
            if polarity == '-':
                db_name = 'malcolm_minus_%d_%d' % (momentum, pid)
            else:
                db_name = 'malcolm_plus_%d_%d' % (momentum, pid)
                
            server = random.choice(servers)
            server = 'http://gnomon:balls@172.16.84.2:8080/'
            couch = couchdb.Server(server)
            print momentum, pid
            filename = tempfile.mkstemp()[1]
            file = open(filename, 'w')

            run = random.randint(1, sys.maxint)

            script = """
source /home/tunnell/env/gnomon/bin/activate
export COUCHDB_URL=%(server_url)s
cd $VIRTUAL_ENV/src/gnomon

time python simulate.py --name %(db_name)s --vertex 2000 -2000 0 -g %(geniename)s --events %(number_of_events)d %(flags)s --run %(run)d --polarity %(polarity)s
time python digitize.py --name %(db_name)s %(flags)s --run %(run)d
#./fit.py --name %(db_name)s %(flags)s --run %(run)d
""" % {'momentum': momentum, 'db_name' : db_name, 'number_of_events' : number_of_events, 'pid' : pid, 'run' : run, 'flags':flags, 'server_url':server, 'polarity' : polarity}
                
            file.write(script)
            file.close()

            print script
            time.sleep(2)
            job_name = '%s_%s' % (db_name, run)
            os.system('qsub -N %s %s' % (job_name, filename))