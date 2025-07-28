import os
import inspect
import redis
import yaml
import json
from pathlib import Path
from datetime import datetime

from .utils import freeze
from .string_op import sanitize_label

def auth_token():
    """
    Try to read the token from the environment variable. If not token is available
    return None. This allows for unauthenticated access to the redis server.
    """
    token = os.getenv('EPOC_REDIS_TOKEN')
    #Allow for it to be set to None as a string
    if token == 'None':
        token = None
    return token

def redis_port():
    port = os.getenv('EPOC_REDIS_PORT')
    if port is None:
        return 6379
    return int(port)

def redis_host():
    try:
        host = os.environ['EPOC_REDIS_HOST']
    except KeyError:
        raise ValueError('Please set the EPOC_REDIS_HOST environment variable')  
    return host

def redis_db():
    db = os.getenv('EPOC_REDIS_DB')
    if db is None:
        return 0
    return int(db)


@freeze
class ConfigurationClient:
    """
    Provides synchronization between PCs and persistent storage of values
    Currently based on Redis but could be extended to other backends
    """
    _experiment_classes = ['UniVie', 'External', 'IP']
    _encoding = 'utf-8'
    _default_rotation_speed_idx = 2
    def __init__(self, host = None, port=redis_port(), token=auth_token(), db = redis_db()):

        #Avoid placing in constructor due to import error
        if host is None:
            host = redis_host()
        

        self.client = redis.Redis(host=host, port=port, password=token, db=db)
        try:
            self.client.ping()
        except redis.exceptions.ConnectionError:
            raise ValueError(f'Could not connect to server: {host}:{port}')


    def from_yaml(self, path: Path, flush_db = False):
        """
        Return to a know state, or populate a new database
        args: path to the yaml file flush: if True, clear the database before loading
        """
        if flush_db:
            self.client.flushdb()
        with open(path, 'r') as file:
            res = yaml.safe_load(file)
        for key, value in res.items():
            setattr(self, key, value)

    def to_yaml(self, path: Path):
        """
        Save the current configuration to a yaml file
        """
        res = {}
        non_writable = {}
        #Find the keys
        for key, item in vars(ConfigurationClient).items():
            if isinstance(item, property):
                # It could be that some values are not set
                # and in this case we ignore them
                try:
                    value = getattr(self, key)
                    if isinstance(value, Path):
                        value = value.as_posix()
                    if item.fset is None:
                        non_writable[key] = value
                    else:
                        res[key] = value
                except ValueError:
                    pass
                
        with open(path, 'w') as file:
            file.write('# Configuration file for EPOC\n')
            file.write(f'# Saved: {datetime.now()}\n\n')
            file.write('# Generated value at time of saving\n')
            for key, value in non_writable.items():
                file.write(f'# {key}: {value}\n')
            file.write('\n')
            yaml.safe_dump(res, file, sort_keys=False)

    @property
    def affiliation(self) -> str:
        res = self.client.get('affiliation')
        if res is None:
            raise ValueError('affiliation not set')
        return res.decode(ConfigurationClient._encoding)
    
    @affiliation.setter
    def affiliation(self, value : str):
        value = sanitize_label(value)
        self.client.set('affiliation', value)

    @property
    def usedAffiliations(self):
        res = self.client.get('usedAffiliations')
        if res is None:
            raise ValueError('usedAffiliations not set')
        return json.loads(res.decode(ConfigurationClient._encoding))
    
    @usedAffiliations.setter
    def usedAffiliations(self, value):
        self.client.set('usedAffiliations', json.dumps(value))
            
    # def add_affiliation(self, value):
    #     self.client.rpush('usedAffiliations', value)            

    @property
    def PI_name(self) -> str:
        res = self.client.get('PI_name')
        if res is None:
            raise ValueError('PI_name not set')
        return res.decode(ConfigurationClient._encoding)
    
    @PI_name.setter
    def PI_name(self, value : str):
        value = sanitize_label(value)
        self.client.set('PI_name', value)
        
    @property
    def project_id(self) -> str:
        res = self.client.get('project_id')
        if res is None:
            raise ValueError('project_id not set')
        return res.decode(ConfigurationClient._encoding)

    @project_id.setter
    def project_id(self, value : str):
        value = sanitize_label(value)
        self.client.set('project_id', value)

    @property
    def last_dataset(self) -> Path | None:
        """
        Path to the last dataset that was recorded.
        Can be used to trigger processing
        """
        res = self.client.get('last_dataset')
        if res is None:
            return None
        return Path(res.decode(ConfigurationClient._encoding))
    
    @last_dataset.setter
    def last_dataset(self, value : Path | str):
        if isinstance(value, Path):
            value = value.as_posix()
        self.client.set('last_dataset', value)

    @property
    def XDS_template(self) -> Path:
        res = self.client.get('XDS_template')
        if res is None:
            raise ValueError('XDS_template not set')
        return Path(res.decode(ConfigurationClient._encoding))
    
    @XDS_template.setter
    def XDS_template(self, value : Path | str):
        if isinstance(value, Path):
            value = value.as_posix()
        self.client.set('XDS_template', value)
    
    @property
    def rotation_speed_idx(self) -> int:
        res = self.client.get('rotation_speed_idx')
        #If the value was not set then go to the default (2==1deg/s)
        if res is None:
            self.rotation_speed_idx = ConfigurationClient._default_rotation_speed_idx
            res = self.client.get('rotation_speed_idx')
        return int(res)
    
    @rotation_speed_idx.setter
    def rotation_speed_idx(self, value : int):
        value = int(value)
        if value not in [0, 1, 2, 3]:
            raise ValueError('Invalid rotation speed. Possible values are 0, 1, 2, 3')
        self.client.set('rotation_speed_idx', value)

    @property
    def file_id(self):
        """
        Unique identifier for the current dataset
        """
        res = self.client.get('file_id')

        #if not set we set it to 0
        if res is None:
            self.client.set('file_id', 0)
            return 0
        return int(res)
    
    @file_id.setter
    def file_id(self, value):
        self.client.set('file_id', value)

    @property
    def nrows(self):
        res = self.client.get('nrows')
        if res is None:
            raise ValueError('nrows not set')
        return int(res)
    
    @property
    def beam_center(self):
        res = self.client.get('beam_center')
        if res is None:
            raise ValueError('beam_center not set')
        return json.loads(res.decode(ConfigurationClient._encoding))
    
    @beam_center.setter
    def beam_center(self, value):
        self.client.set('beam_center', json.dumps(value))

    @property
    def threshold(self) -> int:
        """Threshold that is applied after conversion but before summing of images."""
        res = self.client.get('threshold')
        if res is None:
            raise ValueError('threshold not set')
        return int(res)
    
    @threshold.setter
    def threshold(self, value) -> None:
        self.client.set('threshold', value)

    @property
    def viewer_interval(self):
        res = self.client.get('viewer_interval')
        if res is None:
            raise ValueError('viewer_interval not set')
        return float(res)
    
    @property
    def viewer_cmin(self):
        res = self.client.get('viewer_cmin')
        if res is None:
            raise ValueError('viewer_cmin not set')
        return float(res)
    
    @viewer_cmin.setter
    def viewer_cmin(self, value):
        self.client.set('viewer_cmin', value)

    @property
    def viewer_cmax(self):
        res = self.client.get('viewer_cmax')
        if res is None:
            raise ValueError('viewer_cmax not set')
        return float(res)
    
    @viewer_cmax.setter
    def viewer_cmax(self, value):
        self.client.set('viewer_cmax', value)

    @viewer_interval.setter
    def viewer_interval(self, value):
        self.client.set('viewer_interval', value)
    
    @nrows.setter
    def nrows(self, value):
        self.client.set('nrows', value)

    @property
    def ncols(self):
        res = self.client.get('ncols')
        if res is None:
            raise ValueError('ncols not set')
        return int(res)
    
    @ncols.setter
    def ncols(self, value):
        self.client.set('ncols', value)

    def _incr_file_id(self):
        self.client.incr('file_id')

    @property
    def base_data_dir(self) -> Path:
        res = self.client.get('base_data_dir')
        if res is None:
            raise ValueError('base_data_dir not set')
        return Path(res.decode(ConfigurationClient._encoding))
    
    @base_data_dir.setter
    def base_data_dir(self, value: Path|str):
        value = Path(value)
        self.client.set('base_data_dir', value.as_posix())
    
    @property
    def data_dir(self) -> Path:
        """
        Directory where the current experiment will be stored.
        Computed from the configured experiment
        TODO! Do we need the support for a custom directory
        """
#        path = Path(self.base_data_dir) / self.experiment_class / self.PI_name / self.year / self.project_id / self.today
        path = Path(self.base_data_dir) / self.affiliation / self.PI_name / self.year / self.project_id / self.today
        return path
    

    @property
    def work_dir(self) -> Path:
        """
        Directory where output of data analysis will be stored
        """
#        path = Path(self.base_data_dir) / self.experiment_class / self.PI_name / self.year / self.project_id
        path = Path(self.base_data_dir) / self.affiliation / self.PI_name / self.year / self.project_id
        return path

    @property
    def fname(self) -> str:
        """
        Filename for the current dataset
        generated from the configured experiment and the current date
        """
        res = self.client.get('measurement_tag')
        if res is None:
            raise ValueError('fname not set')
        s = f'{self.file_id:03d}_{self.project_id}_{res.decode(ConfigurationClient._encoding)}_{self.timestamp}_master.h5'
        return s
    
    @property
    def fpath(self) -> Path:
        return self.data_dir / self.fname
    
    @property
    def log_fpath(self) -> Path:
        return (self.data_dir / self.fname).with_suffix('.log')
    
    @property
    def measurement_tag(self) -> str:
        """
        Tag to identify the current measurement. will be part of the filename
        """
        res = self.client.get('measurement_tag')
        if res is None:
            raise ValueError('measurement_tag not set')
        return res.decode(ConfigurationClient._encoding)
    
    @measurement_tag.setter
    def measurement_tag(self, value : str):
        value = sanitize_label(value)
        self.client.set('measurement_tag', value)


    @property
    def experiment_class(self) -> str:
        res = self.client.get('experiment_class')
        if res is None:
            raise ValueError('experiment_class not set')
        return res.decode(ConfigurationClient._encoding)
    
    @experiment_class.setter
    def experiment_class(self, value : str):
        if value not in ConfigurationClient._experiment_classes:
            raise ValueError(f'Invalid experiment class. Possible values are: {ConfigurationClient._experiment_classes}. Got: {value}')
        self.client.set('experiment_class', value)

    @property
    def today(self) -> str:
        """
        Returns the current date in the format YYYY-MM-DD
        #TODO! should we set this manually instead for experiments crossing over midnight?
        """
        return datetime.now().strftime('%Y-%m-%d')
    
    @property
    def year(self) -> str:
        """
        Returns the current year in the format YYYY
        """
        return datetime.now().strftime('%Y')

    @property
    def timestamp(self) -> str:
        """
        Returns the current date in the format YYYY-MM-DD
        #TODO! should we set this manually instead for experiments crossing over midnight?
        """
        return datetime.now().strftime('%Y-%m-%d_%H%M')

    def after_write(self):
        """
        Call after finished an acquisition to update the configuration
        TODO! Find a better name
        """
        self.last_dataset = self.data_dir / self.fname
        self._incr_file_id()

    @property
    def overlays(self):
        return [json.loads(item.decode(ConfigurationClient._encoding)) for item in self.client.lrange('overlays', 0, -1)]
    
    @overlays.setter
    def overlays(self, value):
        self.client.delete('overlays')
        for item in value:
            self.client.rpush('overlays', json.dumps(item))
    
    def add_overlay(self, value):
        self.client.rpush('overlays', value)

    @property
    def mag_value_diff(self):
        res = self.client.get('mag_value_diff')
        if res is None:
            raise ValueError('mag_value_diff not set')
        return float(res)

    @mag_value_diff.setter
    def mag_value_diff(self, value):
        self.client.set('mag_value_diff', value)

    @property
    def mag_value_img(self):
        res = self.client.get('mag_value_img')
        if res is None:
            raise ValueError('mag_value_img not set')
        return float(res)
    
    @mag_value_img.setter
    def mag_value_img(self, value):
        self.client.set('mag_value_img', value)

    @property
    def receiver_endpoint(self):
        res = self.client.get('receiver_endpoint')
        if res is None:
            raise ValueError('receiver_endpoint not set')
        return res.decode(ConfigurationClient._encoding)
    
    @receiver_endpoint.setter
    def receiver_endpoint(self, value):
        self.client.set('receiver_endpoint', value)

    @property
    def cal_dir(self):
        res = self.client.get('cal_dir')
        if res is None:
            raise ValueError('cal_dir not set')
        return Path(res.decode(ConfigurationClient._encoding))
    
    @cal_dir.setter
    def cal_dir(self, value):
        self.client.set('cal_dir', value)

    @property
    def frames_to_sum(self):
        res = self.client.get('frames_to_sum')
        if res is None:
            raise ValueError('frames_to_sum not set')
        return int(res)
    
    @frames_to_sum.setter
    def frames_to_sum(self, value):
        self.client.set('frames_to_sum', value)

    @property
    def temserver(self):
        """
        ZMQ Endpoint for the TEM server
        For example: tcp://TEM-pc:5555
        """
        res = self.client.get('temserver')
        if res is None:
            raise ValueError('temserver not set')
        return res.decode(ConfigurationClient._encoding)
    
    @temserver.setter
    def temserver(self, value):
        self.client.set('temserver', value)

    @property
    def jfjoch_host(self):
        res = self.client.get('jfjoch_host')
        if res is None:
            raise ValueError('jfjoch_host not set')
        return res.decode(ConfigurationClient._encoding)
    
    @jfjoch_host.setter
    def jfjoch_host(self, value):
        self.client.set('jfjoch_host', value)


    def __repr__(self) -> str:
        s = f"""
        Configuration:
        \tPI_name: {self.PI_name}
        \tproject_id: {self.project_id}
        \texperiment_class: {self.experiment_class}
        \tdata_dir: {self.data_dir}
        \twork_dir: {self.work_dir}
        \tfname: {self.fname}

        \tlast_dataset: {self.last_dataset}
        """
        return inspect.cleandoc(s)


