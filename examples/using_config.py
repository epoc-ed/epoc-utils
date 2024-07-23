import os
from epoc import ConfigurationClient


#Get the password for the Redis server
try:
    token = os.environ['EPOC_REDIS_TOKEN']
except KeyError:
    raise ValueError('Please set the EPOC_REDIS_TOKEN environment variable')    
    exit(1)
    
host = 'detpi02'

cfg = ConfigurationClient(host, token=token)

#Clear the database
cfg.client.flushall()

cfg.PI_name = 'Erik'
cfg.project_id = 'epoc'
cfg.experiment_class = 'UniVie'
cfg.base_data_dir = '/data/jungfrau/instruments/jem2100plus'
cfg.measurement_tag = 'Lysozyme'

print(cfg)
