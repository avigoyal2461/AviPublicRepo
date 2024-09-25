import re

def get_generated_quote_details(quote_details):
    if quote_details:
        details = {}
        details_joined = ''
        for detail in quote_details:
            details_joined += detail

        details['price'] = parse_dealer_epc(details_joined) # First check for EPC, then check for Solar Rate
        details['system_size'] = parse_system_size(details_joined)
        details['monthly_sunnova_payment'] = parse_monthly_sunnova_payment(details_joined)
        details['estimated_production'] = parse_estimated_production(details_joined)
        details['new_utility_bill'] = parse_new_utility_bill(details_joined)
        details['total_monthly_electric_cost'] = parse_total_monthly_electric_cost(details_joined)
        details['utility_rate'] = parse_utility_rate(details_joined)
        details['year_one_savings'] = parse_year_one_savings(details_joined)
        details['savings_over_term_length'] = parse_savings_over_term_length(details_joined)
        details['lifetime_payment'] = parse_lifetime_payment(details_joined)
        details['contract_id'] = parse_contract_id(details_joined)
        details['price_per_watt'] = parse_epc_per_watt(details_joined)
        details['total_epc'] = parse_total_epc(details_joined)
        return details

def parse_lifetime_payment(detail_string):
    search_pattern = re.compile(r'Lifetime Payment:\$([\d+,]+\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_year_one_savings(detail_string):
    search_pattern = re.compile(r'Year-1 Savings:\$(\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_savings_over_term_length(detail_string):
    search_pattern = re.compile(r'Savings over Term Length:\$([\d+,]+\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_utility_rate(detail_string):
    search_pattern = re.compile(r'Utility Rate:(\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_total_monthly_electric_cost(detail_string):
    search_pattern = re.compile(r'Total Monthly Electricity Cost:\$(\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_monthly_sunnova_payment(detail_string):
    search_pattern = re.compile(r'Monthly Sunnova Payment:\$(\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_new_utility_bill(detail_string):
    search_pattern = re.compile(r'New Utility Bill:\$(\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_estimated_production(detail_string):
    search_pattern = re.compile(r'Estimated Production:([\d+,]+\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_solar_rate(detail_string):
    search_pattern = re.compile(r'Solar Rate:\$(\d+\.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''
    
def parse_system_size(detail_string):
    search_pattern = re.compile(r'System Size: (\d+[\.\d+]*)') # Has a space because of layout in sunnova portal
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return parse_system_size_no_space(detail_string)

def parse_system_size_no_space(detail_string):
    search_pattern = re.compile(r'System Size:(\d+[\.\d+]*)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_dealer_epc(detail_string):
    search_pattern = re.compile(r'Dealer EPC Per Watt:\$(\d+.\d+)')
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return parse_solar_rate(detail_string)

def parse_contract_id(detail_string):
    search_pattern = re.compile(r"(\D\D\d{9})")
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_epc_per_watt(detail_string):
    search_pattern = re.compile(r"EPC Per Watt – PV Only:\$(\d+.\d+)")
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return parse_epc_per_watt_spaced(detail_string)

def parse_epc_per_watt_spaced(detail_string):
    search_pattern = re.compile(r"EPC Per Watt – PV Only: \$(\d+.\d+)")
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''

def parse_total_epc(detail_string):
    search_pattern = re.compile(r"Total EPC:\$([\d+,]+\d+\.\d+)")
    match = re.search(search_pattern, detail_string)
    if match:
        return match.group(1)
    else:
        return ''