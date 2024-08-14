from epoc import ConfigurationClient, auth_token, redis_host


cfg = ConfigurationClient(redis_host(), token=auth_token())

#Clear the database
# cfg.client.flushall()

# cfg.PI_name = 'Erik'
# cfg.project_id = 'epoc'
# cfg.experiment_class = 'UniVie'
# cfg.base_data_dir = '/data/jungfrau/instruments/jem2100plus'
# cfg.measurement_tag = 'Lysozyme'

print(cfg)
