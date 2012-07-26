import couchdb
import urlparse
import os


master_url = 'http://gnomon:balls@tasd.fnal.gov:5984/'
master_couch = couchdb.Server(master_url)

slave_url = 'http://gnomon:balls@nustorm.physics.ox.ac.uk:5984/'
slave_couch = couchdb.Server(slave_url)

be_continous = False

for dbname in master_couch:
    if dbname[0] != '_':
        slave_link = urlparse.urljoin(slave_url, dbname)
        master_link = urlparse.urljoin(master_url, dbname)

        print dbname
        print '\tmaster:', master_link
        print '\tslave:', slave_link

        slave_couch.replicate(master_link, slave_link,
                              continous=be_continous, create_target=True)