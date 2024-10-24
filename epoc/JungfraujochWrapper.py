import time
from rich import print

import jfjoch_client



class JungfraujochWrapper:
    def __init__(self, host):
        # Defining the host is optional and defaults to http://localhost:5232
        # See configuration.py for a list of all supported configuration parameters.
        self.configuration = jfjoch_client.Configuration(
            host = host
        )

        self.api_client = jfjoch_client.ApiClient(self.configuration)
        self.api_instance = jfjoch_client.DefaultApi(self.api_client)
        self._image_time_us = 50000 #100x500us
        self._lots_of_images = 72000 #1h at 20Hz

    def init(self):
        """Initialize Jungfraujoch. Run once after startup or when restarting the broker"""
        self.api_instance.initialize_post()

    @property
    def image_time_us(self):
        """Total image time in microseconds"""
        return self._image_time_us

    @image_time_us.setter
    def image_time_us(self, value):
        self._image_time_us = value

    def status(self):
        return self.api_instance.status_get()

    def start(self, n_images, fname="", wait = False):
        """Start a measurement. If no filename is given the measurement will not be saved"""
        ds = jfjoch_client.DatasetSettings(
            image_time_us = self._image_time_us,
            images_per_trigger = n_images,
            beam_x_pxl = 1,
            beam_y_pxl = 1,
            detector_distance_mm = 100,
            incident_energy_ke_v = 1,
            pixel_value_low_threshold = 0,
            file_prefix = fname,
            )
        
        self.api_instance.start_post(dataset_settings=ds)
        if wait:
            time.sleep(0.3)
            self.wait_until_idle()

    def cancel(self):
        self.api_instance.cancel_post()

    def collect_pedestal(self, wait = False):
        self.api_instance.pedestal_post()
        if wait:
            time.sleep(0.3)
            self.wait_until_idle()
            stat = self.api_instance.statistics_calibration_get()
            print(stat)

    def wait_until_idle(self, progress=False):
        while True:
            s = self.api_instance.status_get()
            print(s)
            if s.state == 'Idle':
                if progress:
                    print(f'Progress: {100:.0f}%')
                break
            if progress:
                print(f'Progress: {100*s.progress:.0f}%', end = '\r')
            time.sleep(0.1)

    def live(self):
        self.start(self._lots_of_images)

    def collect(self, fname):
        print("Hit enter to start measuring")
        input()
        self.cancel()
        self.wait_until_idle()
        print(f"Starting to record: {fname}")
        self.start(self._lots_of_images, fname = fname)
        print("Hit enter to stop measuring")
        input()
        self.cancel()
        self.wait_until_idle()
        print("Measurement stopped")
        s = self.api_instance.statistics_data_collection_get()
        print(s)
        self.live()
