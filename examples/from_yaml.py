import yaml
from epoc import ConfigurationClient, auth_token, redis_host
c = ConfigurationClient(redis_host(), token=auth_token())

with open('epoc-config.yaml', 'r') as file:
    res = yaml.safe_load(file)
    
c.from_yaml('epoc-config.yaml')


