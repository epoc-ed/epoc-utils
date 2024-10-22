from .ConfigurationClient import ConfigurationClient
from .ConfigurationClient import auth_token, redis_host

try: 
    from .JungfraujochWrapper import JungfraujochWrapper
except ImportError:
    print("No JungfrauWrapper found")