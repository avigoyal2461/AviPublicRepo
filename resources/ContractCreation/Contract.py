# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])


import requests
import re
from ContractCreation.config import salesforce_info_url, update_url
from Database.utilities import get_loan_rate


empty_dict = {'opportunity_name': '',
              'salesperson': '',
              'email': ''}

class Contract:
    """A represention of a sunnova contract with information on how to build one. Also has a file location for the documents."""
    def __init__(self, opportunity_id, file_path=''):
        self.opportunity_id = opportunity_id
        self.salesforceId = opportunity_id
        self.file_path = file_path
        self.salesforce_information = self.get_salesforce_info_from_id(self.opportunity_id)
        # Salesforce info
        self.salesperson = self.set_salesperson(self.salesforce_information['salesperson'])
        self.opportunity_name = self.salesforce_information['opportunity_name']
        self.opportunity_email = self.salesforce_information['email']
        self.opportunityEmail = self.salesforce_information['email']
        self.street_address = self.salesforce_information['street_address']
        self.streetAddress = self.salesforce_information['street_address']
        self.last_name = self.salesforce_information['last_name']
        self.lastName = self.salesforce_information['last_name']
        self.state_code = self.salesforce_information['state_code']
        self.usage = self.salesforce_information['usage']
        self.loi_rate = self.salesforce_information['loi_rate']
        self.ppa_rate = self.salesforce_information['ppa_rate']
        self.utility = self.salesforce_information['utility']
        self.rate = str(get_loan_rate(self.state_code, self.utility))
        self.size = self.salesforce_information['size']
        self.production = self.salesforce_information['production']
        self.purchase_method = self.salesforce_information['purchase_method']
        self.escalator = self.salesforce_information['escalator']
        try:
            self.ppw = '{0:.3f}'.format(float(self.salesforce_information['ppw']))
        except:
            self.ppw = ''
        self.direct_lead = self.salesforce_information['direct_lead']
        # Quote info
        self.financing_type = self.get_financing_type_for_quote()
        self.pricing_method = None
        self.pricing_method = self.get_pricing_method()
        self.price = self.ppa_rate
        self.system_design = None
        self.final_price = ''

    def set_generated_quote_details(self, quote_details):
        if quote_details:
            details_joined = ''
            for detail in quote_details:
                details_joined += detail

            self.ppw = self.parse_ppw(details_joined)
            self.system_size = self.parse_system_size(details_joined)
            self.production = self.parse_production(details_joined)
            self.loi_rate = self.parse_solar_rate(details_joined)

    def parse_solar_rate(self, detail_string):
        search_pattern = re.compile(r'Solar Rate:\$(\d+\.\d+)')
        match = re.search(search_pattern, detail_string)
        if match:
            return match.group(1)
        else:
            return ''
        
    def parse_system_size(self, detail_string):
        search_pattern = re.compile(r'System Size: (\d+\.\d+)')
        match = re.search(search_pattern, detail_string)
        if match:
            return match.group(1)
        else:
            return ''
        
    def parse_production(self, detail_string):
        search_pattern = re.compile(r'Estimated Production:(\d+.\d+)')
        match = re.search(search_pattern, detail_string)
        if match:
            return match.group(1)
        else:
            return ''

    def parse_ppw(self, detail_string):
        search_pattern = re.compile(r'Dealer EPC Per Watt:\$(\d+.\d+)')
        match = re.search(search_pattern, detail_string)
        if match:
            return match.group(1)
        else:
            return ''

    def get_utility(self):
        utility = self.utility.split(' ')[0]
        return utility.replace('&', '')

    def get_rate(self):
        return input('Please enter rate: ')

    def set_file_path(self, file_path):
        self.file_path = file_path
        
    def set_system_design_name(self, system_design):
        self.system_design = system_design

    def get_opportunity_name(self):
        return self.opportunity_name

    def get_salesperson(self):
        return self.salesperson

    def set_price(self, price):
        if '$' in price:
            price = price.replace('$', '')
        self.price = price

    def set_pricing_method(self, pricing_method):
        if pricing_method[0] != ' ':
            pricing_method = ' ' + pricing_method
        if pricing_method[-1] != ' ':
            pricing_method = pricing_method + ' '
        self.pricing_method = pricing_method
    
    def set_rate(self, rate):
        self.rate = rate

    def set_salesperson(self, salesperson):
            if ',' in salesperson:
                flipped = self.flip_salesperson(salesperson)
                split = flipped.split(' ')
                return split[0] + ' ' + split[-1]
            else:
                split = salesperson.split(' ')
                return split[0] + ' ' + split[-1]

    def get_salesforce_info_from_id(self, salesforce_id):
        """Requests opportunity information from Salesforce"""
        request_obj = {'opportunity_id':salesforce_id}
        try:
            print('Requesting salesforce info...')
            response = requests.post(salesforce_info_url, json=request_obj)
            print('Retrieved salesforce info...')
            print(response.json())
            return response.json()
        except:
            print('Failed to retrieve info...')
            return empty_dict

    def flip_salesperson(self, name):
        name_segments = name.split(', ')
        reversed_name = reversed(name_segments)
        return ' '.join(reversed_name)

    def get_financing_type_for_quote(self):
        """Determines the type of financing based on the purchase method string. Strings have leading and trailing spaces due to Sunnova portal."""
        if 'EZ' in self.purchase_method:
            return ' PPA-EZ '
        elif 'Lease' in self.purchase_method:
            return ' Lease '
        elif 'Loan' in self.purchase_method:
            return ' Loan '
        elif 'PPA' in self.purchase_method:
            return ' PPA '
        else:
            print(f'Sunnova purchase method not found for {self.purchase_method}')
            return None

    def get_pricing_method(self):
        if self.financing_type == ' Loan ':
            return ' Customer Price '
        elif self.pricing_method == 'dealer_epc_per_watt':
            return 'Dealer EPC Per Watt'
        else:
            return ' Solar Rate '

    def update_opportunity(self):
        # TODO: add inverters
        content = {'opp_id':self.opportunity_id,
                   'loi_rate': self.loi_rate,
                   'system_size': self.system_size,
                   'production': self.production,
                   'ppw': self.ppw}
        try:
            requests.post(update_url, json=content)
            print('Salesforce updated')
        except:
            print('Could not update salesforce...')

    def get_escalator(self):
        if self.escalator == "0.0%":
            return "0.00%"
        elif self.escalator == "0.9%":
            return "0.0%"
        elif self.escalator == "1.9%":
            return "1.90%"
        elif self.escalator == "2.9%":
            return "2.90%"
        elif self.escalator == "3.9%":
            return "3.90%"
        elif self.escalator == "4.9%":
            return "4.90%"


if __name__ == "__main__":
    test_contract = Contract('0063200001qCo76AAC')
    print(test_contract.salesperson)
    print(test_contract.opportunity_name)
    print(test_contract.loi_rate)
    print(test_contract.usage)
    print(test_contract.size)
    print(test_contract.production)
    print(test_contract.ppw)
    print(test_contract.financing_type)
    print(test_contract.purchase_method)
    print(test_contract.opportunity_email)
    print(test_contract.escalator)
    print(test_contract.get_utility())