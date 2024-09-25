# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
from SolarSystem.config import inverters_url, salesforce_info_url
from SolarSystem.Array import Array
import requests
import re


WATTAGE = 'Wattage__c'
optimizer_wattages = [300, 320, 350, 370, 400, 405, 505]
optimizer_names = ['SolarEdge Optimizer P' + str(wattage) for wattage in optimizer_wattages]

class InvalidModuleSizeError(Exception):
    pass

class SystemDesign:
    def __init__(self, opp_id, arrays, email, module):
        self.opp_id = opp_id
        self.arrays = arrays
        self.total_modules: int = self._get_total_modules()
        self.email = email
        self.module = module
        self.array_count = len(self.arrays)
        self.module_manufacturer = self._get_module_manufacturer()
        self.module_model = self._get_module_model()
        self.name = None
        self.customer_email = None
        self.module_size = self._calculate_module_size()
        self.size = int(self.total_modules) * int(self.module_size)
        self.inverters = self._calculate_inverters()
        self.inverter_quantities = self._calculate_inverter_quantities()
        self.inverter_manufacturer = 'SolarEdge' # TODO: make this dynamic
        self.optimizer = self._get_optimizer_from_inverter()
        self.monitor = self.get_monitor()
        self._set_salesforce_info()

    def get_monitor(self):
        try:
            manufacturer = self.inverters[0]['Name'].lower()
            if 'solar edge' in manufacturer:
                return r'SE-MTR240-0-000-S2 (3G)'
            else:
                return r'ENV-IQ-AMI-240 / CELLMODEM-02 M (4G)'
        except: 
            return None

    def _get_optimizer_from_inverter(self):
        try:
            manufacturer = self.inverters[0]['manufacturer'].lower()
            if 'solar edge' in manufacturer or 'solaredge' in manufacturer:
                return self._get_solaredge_optimizer()
            else:
                return 'Enphase Micro'
        except:
            return None

    def _get_solaredge_optimizer(self):
        """These are currently a constant value"""
        return 'P340-5NM4MRSS'

    def get_arrays(self):
        return self.arrays

    def _get_total_modules(self) -> int:
        total = 0
        for array in self.arrays:
            total += int(array.module_quantity)
        return total

    def _set_salesforce_info(self):
        opp_id = {'opp_id':self.opp_id}
        response = requests.post(salesforce_info_url, json=opp_id)
        response_info = response.json()
        self.name = response_info['name']
        self.customer_email = response_info['email']

    def _calculate_inverters(self) -> list:
        """Calculates the needed inverters for this system."""
        if self.total_modules < 8:
            raise Exception('This should be an enphase system.')
        else:
            return self._calculate_solaredge_inverters_from_chart(int(self.module_size), self.total_modules)

    def _calculate_solaredge_inverters_from_chart(self, module_size, total_module_quantity) -> list:
        """
        Calculates inverters needed based on Sales Ops inverter chart. This needs to be cleaned up a bit.

            Parameters:
                module_size (int): The wattage of the module.
                total_module_quantity (int): The total module quantity on this system.
                
            Returns:
                inverter_data (list): A list of inverters needed for this system.
        """
        inverter_sizes = [3000, 3800, 5000, 6000, 7600, 10000, 11400]
        chart = {
            300: [13, 17, 22, 27, 34, 45, 51],
            305: [13, 16, 22, 26, 33, 44, 50],
            310: [13, 16, 21, 26, 33, 43, 49],
            315: [12, 16, 21, 25, 32, 42, 48],
            320: [12, 16, 21, 25, 32, 42, 48],
            330: [12, 15, 20, 24, 31, 40, 46],
            335: [12, 15, 20, 24, 30, 40, 45],
            340: [11, 15, 19, 23, 30, 39, 45],
            345: [11, 14, 19, 23, 29, 39, 44],
            350: [11, 14, 19, 23, 29, 38, 43],
            355: [11, 14, 19, 22, 28, 38, 43],
            360: [11, 14, 18, 22, 28, 37, 42]
        }
        valid_module_sizes = list(chart.keys())
        if module_size not in valid_module_sizes:
            raise InvalidModuleSizeError(f"Module size invalid: {str(module_size)}")
        available_inverters = self._get_available_inverters()
        inverters = []
        while total_module_quantity > 0:
            for index, inverter in enumerate(inverter_sizes):
                if total_module_quantity < chart[module_size][index]:
                    inverters.append(inverter)
                    total_module_quantity -= chart[module_size][index]
                    break
            if total_module_quantity > chart[module_size][-1]:
                inverters.append(inverter_sizes[-1])
                total_module_quantity -= chart[module_size][-1]
        print(f'Calculated inverters: {inverters}')
        inverter_data = []
        for inverter in inverters:
            for inverter_info in available_inverters:
                if int(inverter_info[WATTAGE]) == inverter:
                    inverter_data.append(inverter_info)
        return inverter_data


        



    def _get_available_inverters(self) -> list:
        """Requests list of inverters from power automate then sorts by wattage."""
        response = requests.get(inverters_url)
        available = response.json()
        sorted_inverters = sorted(available, key=lambda x: x[WATTAGE])
        return sorted_inverters

    def _calculate_inverter_quantities(self):
        quantities = []
        inverters = self.inverters[:]
        for inverter in inverters:
            quantities.append(inverters.count(inverter))
            inverters[:] = [x for x in inverters if x != inverter]
        return quantities

    def get_total_modules(self):
        total = 0
        for array in self.arrays:
            total += int(array.module_quantity)
        return total

    def _calculate_module_size(self):
        size_search = re.search("\d\d\d", self.module)
        return size_search.group()
        

    def _get_module_manufacturer(self):
        # Sample Hanwha - Q.PEAK DUO BLK-G6 340
        split_module = self.module.split('-')
        return split_module[0].rstrip()

    def _get_module_model(self):
        # Sample Canadian Solar - CS6P-265P
        split_module = self.module.split('-')
        del(split_module[0])
        new_module = '-'.join(split_module)
        return new_module



def create_system_from_dict(genesis_design):
    """Creates a system design from the dictionary supplied by Genesis"""
    opp_id = genesis_design['oppID']
    email = genesis_design['email']
    module = genesis_design['module']

    arrays = []
    for array in genesis_design['roofs']:
        quantity = array['modules']['quantity']
        if quantity > 0:
            tilt = array['shade']['tilt']
            azimuth = array['shade']['azimuth']
            availability = array['shade']['availability']
            arrays.append(Array(quantity,tilt,azimuth,availability))

    return SystemDesign(opp_id, arrays, email, module)
    

if __name__ == "__main__":
    sample_data = {
                        "key": "951753",
                        "oppID": "0063200001qCo76AAC",
                        "email": "kevinjanssen@trinity-solar.com",
                        "module": "Hanwha - Q.PEAK DUO BLK-G5 320",
                        "roofs": [
                            {
                                "modules": {
                                    "quantity": 40
                                },
                                "shade": {
                                    "tilt": 33.69,
                                    "azimuth": 169.6,
                                    "availability": 2100
                                }
                            },
                            {
                                "modules": {
                                    "quantity": 40
                                },
                                "shade": {
                                    "tilt": 33.69,
                                    "azimuth": 349.6,
                                    "availability": 177
                                }
                            },
                            {
                                "modules": {
                                    "quantity": 40
                                },
                                "shade": {
                                    "tilt": 33.69,
                                    "azimuth": 349.6,
                                    "availability": 1794
                                }
                            }
                        ]
                    }
    design = create_system_from_dict(sample_data)
    print(design.inverters)
    print(design.inverter_quantities)