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
def test_construction_of_fname():
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    cfg.measurement_tag = 'Lysozyme'
    cfg.project_id = 'ProjectID'
    cfg.file_id = 37
    assert cfg.fname == f'037_ProjectID_Lysozyme_{datetime.now().strftime("%Y-%m-%d")}_master.h5'

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

@with_redis
def test_last_dataset():
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    cfg.PI_name = 'PIName'
    cfg.project_id = 'ProjectID'
    cfg.experiment_class = 'UniVie'
    cfg.base_data_dir = '/data/base/path/'
    cfg.measurement_tag = 'Lysozyme'
    cfg.file_id = 7

    last = f'/data/base/path/UniVie/PIName/ProjectID/{datetime.now().strftime("%Y-%m-%d")}/007_ProjectID_Lysozyme_{datetime.now().strftime("%Y-%m-%d")}_master.h5'
    cfg.after_write()
    assert cfg.last_dataset.as_posix() == last

@with_redis
def test_set_XDS_template():
    cfg = ConfigurationClient(redis_host(), token=auth_token(), db = test_db)
    cfg.XDS_template = '/path/to/template.INP'
    assert cfg.XDS_template == '/path/to/template.INP'