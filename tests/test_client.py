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

    with freeze_time('2020-01-01'):
        assert cfg.fname == f'037_ProjectID_Lysozyme_2020-01-01_master.h5'

@with_redis
def test_construction_of_data_dir(cfg):
    cfg.PI_name = 'PIName'
    cfg.project_id = 'ProjectID'
    cfg.experiment_class = 'UniVie'
    cfg.base_data_dir = '/data/base/path/'

    with freeze_time('1984-07-22'):
        assert cfg.data_dir == Path('/data/base/path/UniVie/PIName/ProjectID/1984-07-22')

@with_redis
def test_fpath(cfg):
    with freeze_time('2024-08-13'):
        assert cfg.fpath == Path(f'/data/base/path/UniVie/PIName/ProjectID/2024-08-13/037_ProjectID_Lysozyme_2024-08-13_master.h5')

@with_redis
def test_loading_from_yaml(cfg):
    cfg.from_yaml('tests/test_epoc_config.yaml', flush_db=True)
    assert cfg.PI_name == 'Erik'
    assert cfg.project_id == 'epoc'
    assert cfg.experiment_class == 'External'
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
    assert cfg.experiment_class == 'External'
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
    cfg.experiment_class = 'UniVie'
    cfg.base_data_dir = '/data/base/path/'
    cfg.measurement_tag = 'Lysozyme'
    cfg.file_id = 7

    with freeze_time('2024-08-13'):
        last = Path('/data/base/path/UniVie/PIName/ProjectID/2024-08-13/007_ProjectID_Lysozyme_2024-08-13_master.h5')
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
def test_experiment_class(cfg):
    cfg.experiment_class = 'UniVie'
    assert cfg.experiment_class == 'UniVie'

    cfg.experiment_class = 'External'
    assert cfg.experiment_class == 'External'

    cfg.experiment_class = 'IP'
    assert cfg.experiment_class == 'IP'

@with_redis
def test_experiment_class_throws_on_not_allowed_value(cfg):
    with pytest.raises(ValueError):
        cfg.experiment_class = 'SomeRandomName'
    