import pytest
from epoc import ConfigurationClient, auth_token, redis_host
from datetime import datetime
from pathlib import Path


from freezegun import freeze_time
with_redis = pytest.mark.skipif("not config.getoption('with_redis')")


@with_redis
def test_set_PI_name(cfg):
    cfg.PI_name = 'Erik'
    assert cfg.PI_name == 'Erik'

@with_redis
def test_PI_name_removes_space(cfg):
    cfg.PI_name = 'Some Name'
    assert cfg.PI_name == 'SomeName'



@with_redis
def test_construction_of_fname(cfg):
    cfg.measurement_tag = 'Lysozyme'
    cfg.project_id = 'ProjectID'
    cfg.file_id = 37


    with freeze_time('2020-01-01 11:53:12'):
        assert cfg.fname == f'037_ProjectID_Lysozyme_2020-01-01_1153_master.h5'

    #time is in 24h format
    with freeze_time('2020-01-01 23:12:11'):
        assert cfg.fname == f'037_ProjectID_Lysozyme_2020-01-01_2312_master.h5'

@with_redis
def test_construction_of_data_dir(cfg):
    cfg.PI_name = 'PIName'
    cfg.project_id = 'ProjectID'
    cfg.affiliation = 'UniVie'
    cfg.base_data_dir = '/data/base/path/'

    with freeze_time('1984-07-22'):
        assert cfg.data_dir == Path('/data/base/path/UniVie/PIName/1984/ProjectID/1984-07-22')

@with_redis
def test_construction_of_work_dir(cfg):
    cfg.PI_name = 'PIName'
    cfg.project_id = 'ProjectID'
    cfg.affiliation = 'UniVie'
    cfg.base_data_dir = '/data/base/path/'

    with freeze_time('1984-07-22'):
        # Test the work_dir with the year included
        assert cfg.work_dir == Path('/data/base/path/UniVie/PIName/1984/ProjectID')

@with_redis
def test_fpath(cfg):
    with freeze_time('2024-08-13'):
        assert cfg.fpath == Path(f'/data/base/path/UniVie/PIName/2024/ProjectID/2024-08-13/037_ProjectID_Lysozyme_2024-08-13_0000_master.h5')

@with_redis
def test_loading_from_yaml(cfg):
    cfg.from_yaml('tests/test_epoc_config.yaml', flush_db=True)
    assert cfg.PI_name == 'Erik'
    assert cfg.project_id == 'epoc'
    assert cfg.affiliation == 'External'
    assert cfg.base_data_dir == Path('/some/random/path')
    assert cfg.measurement_tag == 'MySample'
    assert cfg.file_id == 3
    assert cfg.viewer_interval == 200

@with_redis
def test_update_from_yaml(cfg):
    cfg.from_yaml('tests/test_epoc_config_partial.yaml')
    #These fields have changed:
    assert cfg.viewer_interval == 100
    assert cfg.file_id == 7

    #The rest should have stayed the same
    assert cfg.PI_name == 'Erik'
    assert cfg.project_id == 'epoc'
    assert cfg.affiliation == 'External'
    assert cfg.base_data_dir == Path('/some/random/path')
    assert cfg.measurement_tag == 'MySample'



@with_redis
def test_set_project_id(cfg):
    cfg.project_id = 'epoc'
    assert cfg.project_id == 'epoc'

@with_redis
def test_project_id_removes_slash(cfg):
    cfg.project_id = 'epoc/33'
    assert cfg.project_id == 'epoc33'

@with_redis
def test_rotation_speed_idx(cfg):
    cfg.rotation_speed_idx = 1
    assert cfg.rotation_speed_idx == 1

@with_redis
def test_rotation_speed_idx_must_throws_on_other_value(cfg):
    with pytest.raises(ValueError):
        cfg.rotation_speed_idx = 7

@with_redis
def test_not_set_gives_default(cfg):
    cfg.client.delete('rotation_speed_idx')
    assert cfg.rotation_speed_idx == 2

@with_redis
def test_last_dataset(cfg):
    cfg.PI_name = 'PIName'
    cfg.project_id = 'ProjectID'
    cfg.affiliation = 'UniVie'
    cfg.base_data_dir = '/data/base/path/'
    cfg.measurement_tag = 'Lysozyme'
    cfg.file_id = 7

    with freeze_time('2024-08-13'):
        last = Path('/data/base/path/UniVie/PIName/2024/ProjectID/2024-08-13/007_ProjectID_Lysozyme_2024-08-13_0000_master.h5')
        cfg.after_write()
        assert cfg.last_dataset == last

@with_redis
def test_file_id_increments_with_after_write(cfg):
    cfg.file_id = 17
    cfg.after_write()
    assert cfg.file_id == 18

@with_redis
def test_set_XDS_template(cfg):
    cfg.XDS_template = '/path/to/template.INP'
    assert cfg.XDS_template == Path('/path/to/template.INP')

@with_redis
def test_set_rows_and_cols(cfg):
    cfg.nrows = 100
    cfg.ncols = 200
    assert cfg.nrows == 100
    assert cfg.ncols == 200

@with_redis
def test_set_receiver_endpoint(cfg):
    cfg.receiver_endpoint = 'tcp://localhost:5555'
    assert cfg.receiver_endpoint == 'tcp://localhost:5555'  

@with_redis
def test_frames_to_sum(cfg):
    cfg.frames_to_sum = 10
    assert cfg.frames_to_sum == 10

@with_redis
def test_caldir(cfg):
    cfg.cal_dir = '/path/to/caldir'
    assert cfg.cal_dir == Path('/path/to/caldir')


@with_redis
def test_temserver(cfg):
    cfg.temserver = 'tcp://localhost:5555'
    assert cfg.temserver == 'tcp://localhost:5555'

@with_redis
def test_set_jfjoch_host(cfg):
    cfg.jfjoch_host = 'http://localhost:5232'
    assert cfg.jfjoch_host == 'http://localhost:5232'