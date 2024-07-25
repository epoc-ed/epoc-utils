def pytest_addoption(parser):
    parser.addoption('--with-redis', action='store_true', dest="with_redis",
                 default=False, help="run tests that require a redis server")