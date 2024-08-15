import os
import inspect
import redis
import yaml
import json
from pathlib import Path
from datetime import datetime

from .string_op import sanitize_label

def auth_token():
    try:
        token = os.environ['EPOC_REDIS_TOKEN']
        if token == 'None':
            token = None
    except KeyError:
        raise ValueError('Please set the EPOC_REDIS_TOKEN environment variable')  
    return token

def redis_host():
    try:
        host = os.environ['EPOC_REDIS_HOST']
    except KeyError:
        raise ValueError('Please set the EPOC_REDIS_HOST environment variable')  
    return host

class ConfigurationClient:
    """
    Provides synchronization between PCs and persistent storage of values
    Currently based on Redis but could be extended to other backends
    """
    _experiment_classes = ['UniVie', 'External', 'IP']
    def __init__(self, host, port=6379, token=None, db = 0):
        self.client = redis.Redis(host=host, port=port, password=token, db=db)
        try:
            self.client.ping()
        except redis.exceptions.ConnectionError:
            raise ValueError(f'Could not connect to server: {host}:{port}')


    def from_yaml(self, path: Path):
        """Return to a know state, or populate a new database"""
        self.client.flushall()
        with open(path, 'r') as file:
            res = yaml.safe_load(file)
        for key, value in res.items():
            setattr(self, key, value)



    @property
    def PI_name(self) -> str:
        res = self.client.get('PI_name')
        if res is None:
            raise ValueError('PI_name not set')
        return res.decode('utf-8')
    
    @PI_name.setter
    def PI_name(self, value : str):
        value = sanitize_label(value)
        self.client.set('PI_name', value)

    @property
    def project_id(self) -> str:
        res = self.client.get('project_id')
        if res is None:
            raise ValueError('project_id not set')
        return res.decode('utf-8')

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
        return Path(res.decode('utf-8'))
    
    @last_dataset.setter
    def last_dataset(self, value : Path | str):
        if isinstance(value, Path):
            value = value.as_posix()
        self.client.set('last_dataset', value)

    
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
        return json.loads(res.decode('utf-8'))
    
    @beam_center.setter
    def beam_center(self, value):
        self.client.set('beam_center', json.dumps(value))

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
        return Path(res.decode('utf-8'))
    
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
        path = Path(self.base_data_dir) / self.experiment_class / self.PI_name / self.project_id / self.today
        return path
    

    @property
    def work_dir(self) -> Path:
        """
        Directory where output of data analysis will be stored
        """
        path = Path(self.base_data_dir) / self.experiment_class / self.PI_name / self.project_id
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
        s = f'{self.file_id:03d}_{self.project_id}_{res.decode("utf-8")}_{self.today}.h5'
        return s
    
    @property
    def measurement_tag(self) -> str:
        """
        Tag to identify the current measurement. will be part of the filename
        """
        res = self.client.get('measurement_tag')
        if res is None:
            raise ValueError('measurement_tag not set')
        return res.decode('utf-8')
    
    @measurement_tag.setter
    def measurement_tag(self, value : str):
        value = sanitize_label(value)
        self.client.set('measurement_tag', value)


    @property
    def experiment_class(self) -> str:
        res = self.client.get('experiment_class')
        if res is None:
            raise ValueError('experiment_class not set')
        return res.decode('utf-8')
    
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

    def after_write(self):
        """
        Call after finished an acquisition to update the configuration
        TODO! Find a better name
        """
        self.last_dataset = self.data_dir / self.fname
        self._incr_file_id()

    @property
    def overlays(self):
        return [json.loads(item.decode('utf-8')) for item in self.client.lrange('overlays', 0, -1)]
    
    @overlays.setter
    def overlays(self, value):
        self.client.delete('overlays')
        for item in value:
            self.client.rpush('overlays', json.dumps(item))
    
    def add_overlay(self, value):
        self.client.rpush('overlays', value)

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


