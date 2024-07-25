import pytest
from epoc import ConfigurationClient, auth_token, redis_host
from datetime import datetime
with_redis = pytest.mark.skipif("not config.getoption('with_redis')")

#Avoid using the default database in case someone is using it for manual testing
test_db = 1

@with_redis
def test_set_PI_name():
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    cfg.PI_name = 'Erik'
    assert cfg.PI_name == 'Erik'


@with_redis
def test_PI_name_removes_space():
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    cfg.PI_name = 'Some Name'
    assert cfg.PI_name == 'SomeName'

@with_redis
def test_set_project_id():
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    cfg.project_id = 'epoc'
    assert cfg.project_id == 'epoc'

@with_redis
def test_project_id_removes_slash():
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    cfg.project_id = 'epoc/33'
    assert cfg.project_id == 'epoc33'

@with_redis
def test_construction_of_data_dir():
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    cfg.PI_name = 'PIName'
    cfg.project_id = 'ProjectID'
    cfg.experiment_class = 'UniVie'
    cfg.base_data_dir = '/data/base/path/'
    assert cfg.data_dir.as_posix() == f'/data/base/path/UniVie/PIName/ProjectID/{datetime.now().strftime("%Y-%m-%d")}'