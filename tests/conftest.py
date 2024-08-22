import pytest
from epoc import ConfigurationClient, auth_token, redis_host

def pytest_addoption(parser):
    parser.addoption('--with-redis', action='store_true', dest="with_redis",
                 default=False, help="run tests that require a redis server")
    


@pytest.fixture
def cfg():
    #Avoid using the default database in case someone is using it for manual testing
    test_db = 1
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    return cfg