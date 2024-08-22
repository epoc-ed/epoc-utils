import yaml
from epoc import ConfigurationClient, auth_token, redis_host


c = ConfigurationClient(redis_host(), token=auth_token())
c.from_yaml('../etc/epoc-config.yaml')


