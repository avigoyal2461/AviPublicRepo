class Array:
    def __init__(self, module_quantity, tilt, azimuth, availability):
        self.module_quantity = module_quantity
        self.tilt = str(round(tilt))
        self.azimuth = str(round(azimuth))
        self.availability = str(round(float(availability)))
        self.racking = 'Unirac'
        self.verify_data()

    def verify_data(self):
        if int(self.azimuth) < 0 or int(self.azimuth) > 360:
            return False
