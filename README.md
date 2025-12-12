# epoc-utils

Tools related to the running of experiments and organization of data

## ConfigurationClient

To run with the default constructor without supplying extra arguments. Set
```bash
#Where does the redis server run?
export EPICS_REDIS_HOST=localhost

#Optionally
export EPICS_REDIS_TOKEN=yoursupersafepassword
export EPICS_REDIS_PORT=6379 #in case not the default
export EPICS_REDIS_DB=0 #same here
```


```python
from epoc import ConfigurationClient

c = ConfigurationClient()


#Clear the database and populate it from a yaml file. Clears the selected database only, but will affect all users connected to the same machine!
c.from_yaml('epoc-config.yaml', flush_db = True)

#Default is to update just the fields that are in the yaml file
c.from_yaml('minor-config.yaml')

#It is also possible to save the current state to a yaml file
c.to_yaml('my-config.yaml')
```


### Paths


```python
#The location and file name is specified with a series of properties
cfg.PI_name = 'Erik'
cfg.project_id = 'epoc'
cfg.experiment_class = 'UniVie'
cfg.affiliation = 'UniVie'
cfg.base_data_dir = '/data/jungfrau/instruments/jem2100plus'
cfg.measurement_tag = 'Lysozyme'

#Given that the current date is 2024-08-20 at 12:24

#[base_data_dir]/experiment_class]/[project_id]/[date]/
#[base_data_dir]/[affiliation]/[project_id]/[date]/
>>> c.data_dir 
"/data/jungfrau/instruments/jem2100plus/UniVie/epoc/2024-08-20/"


#[file_id]_[project_id]_[measurement_tag]_[date]_[time]_master.h5
>>> c.fname
"000_epoc_Lysozyme_2024-08-20_1224_master.h5"

#Where should we look for the jungfrau_receiver?
>>> c.receiver_endpoint
"tcp://localhost:5555"
```



### Overlays
Overlays to be draw by the GUI can be specified in the yaml file or added directly in the client

```yaml
# Overlays to be drawn in the GUI
overlays:
  - {"type": "circle", "xy": [173,170], "radius": 160,"ec": "r", "fill" : false, "lw": 2}
  - {"type": "circle", "xy": [173,170], "radius": 5,"ec": "g", "fill" : false, "lw": 2}
  - {"type": "rectangle", "xy": [400,400], "width": 10, "height": 5, "angle": 30, "ec":"y"}

```

```python

c = ConfigurationClient(redis_host(), token=auth_token())
c.add_overlay({"type": "circle", "xy": [173,170], "radius": 160,"ec": "r", "fill" : false, "lw": 2})

#or
c.overlays = [overlay1, overlay2, overlay3]
```