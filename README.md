# epoc-utils

Tools related to the running of experiments and organization of data

## ConfigurationClient


```python
from epoc import ConfigurationClient, auth_token, redis_host

#auth_token and redis_host are convenient functions that looks for the env variables EPOC_AUTH_TOKEN and EPOC_REDIS_HOST

c = ConfigurationClient(redis_host(), token=auth_token())


#Clear the database and populate it from a yaml file. Note that this affects ALL users on ALL machines connected to the same database
c.from_yaml('epoc-config.yaml')
```

### Paths

```python
#The location and file name is specified with a series of properties
cfg.PI_name = 'Erik'
cfg.project_id = 'epoc'
cfg.experiment_class = 'UniVie'
cfg.base_data_dir = '/data/jungfrau/instruments/jem2100plus'
cfg.measurement_tag = 'Lysozyme'

#Given that the current date is 2024-08-20
>>> c.data_dir 
"/data/jungfrau/instruments/jem2100plus/UniVie/epoc/2024-08-20/"

>>> c.fname
"000_epoc_Lysozyme_2024-08-20_master.h5"

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