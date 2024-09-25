import pandas as pd
import numpy as np
import pyodbc
from datetime import date

def Pipeline():
    # df = pd.read_excel('DATA+-+PIPELINE+-+August+2021.xlsx', sheet_name='TI - PIPELINE')
    df = pd.read_excel('C:\Hold\DATA+-+PIPELINE+-+August+2021.xlsx', sheet_name='TI - PIPELINE' )
    df.columns = ['TI_Application_Number', 'Registration_Number', 'Program', 'Premise_Last_Name', 'Premise_Company', 'Premise_Installation_Address_Commercial_Only', 'Premise_City', 'Premise_Zip', 'County_Code', 'Calculated_Total_System_Size', 'Customer_Type', 'Third_Party_Ownership', 'Grid_BTM', 'Project_Type', 'Subsection', 'EDC_Program', 'Contractor_Company', 'Electric_Utility_Name', 'Status', 'Registration_Received_Date', 'Acceptance_Date', 'Expiration_Date']
    df['Installs'] = 1


    contractor_companies = {
        'Absolutely Energized': 'Absolutely Energized Solar',
        'Trinity Hea': 'Trinity Solar',
        'Trinity Services': 'Trinity Services',
        'Geogenix': 'Geogenix',
        '1st light': '1st Light Energy',
        'Mak': 'Mak Technologies',
        'BP': 'BP Solar International',
        'SunPower Capital': 'SunPower Capital',
        'SunPower Corp': 'SunPower Corporation',
        'Solar Landscape': 'Solar Landscape',
        'RCL Solar': 'RCL Solar',
        'Paladin Solar': 'Paladin Solar',
        'Orbit Energy': 'Orbit Energy',
        'Onforce': 'Onforce Solar',
        'National Energy P': 'National Energy Partners',
        'Morgan Solar': 'Morgan & Morgan Solar',
        'Lucent': 'Lucent Energy Management',
        'Independence': 'Independence Solar',
        'Independent': 'Independent Solar',
        'HESP C': 'HESP Construction',
        'HESP S': 'HESP Solar',
        'Heat Shed': 'Heat Shed',
        'Group Solar': 'Group Solar',
        'Grid Alternative': 'Grid Alternatives',
        'Grid Rev': 'Grid Revolution Solar',
        'Gridpoint': 'Gridpoint Services',
        'Grid Holding': 'Urban Grid Holdings',
        'Green Hybrid': 'Green Hybrid Energy Solutions',
        'Green Energy Con': 'Green Energy Construction & Consulting',
        'Evergreen Energy': 'Evergreen Energy',
        'First Power': 'First Power & Light',
        'Eastern Energy': 'Eastern Energy Services',
        'Dynamic Energy': 'Dynamic Energy',
        'Tesla': 'Tesla',
        'Vivint': 'Vivint',
        'Sunrun': 'Sunrun',
        'NRG': 'NRG',
        'Acos': 'ACOS',
        'Advanced Solar Product': 'Advanced Solar Products',
        'Advanced Renew': 'Advanced Renewable Solutions',
        'Ecological': 'Ecological Systems',
        'Alteris': 'Alteris Renewables',
        'Surewave': 'Surewave Solar',
        'Whitman': 'Whitman Construction',
        'Amergy': 'Amergy Solar',
        'Aston Solar': 'Aston Solar',
        'Bowman Walker': 'Bowman Walker Construction',
        'Castle Energy': 'Castle Energy',
        'Ad Energy': 'Ad Energy',
        'Amberjack': 'Amberjack Solar',
        'Aztec': 'Aztec Solar',
        'Bap': 'BAP Power Corporation',
        '1st US': '1st US Energy',
        'Adema': 'Adema Technologies',
        'Allied Con': 'Allied Construction',
        'Momentum Solar': 'Momentum Solar',
        'My NJ Solar': 'NJ Solar Power',
        'NJ Solar Solutions': 'NJ Solar Solutions',
        'Powerlution': 'Powerlutions',
        'R U Bright': 'R U Bright',
        'Ray Angelini': 'Ray Angelini',
        'Arosa' : 'Arosa Solar',
        'Breaker Electric': 'Breaker Electric',
        'Code Green': 'Code Green',
        'Sunvest Solar': 'SunVest Solar',
        'Sungevity': 'Sungevity',
        'The Solar Center': 'Solar Center',
        'Samba Energy': 'Samba Energy',
        'Tonetta Electrical': 'Tonetta Electrical Contractor',
        'US Clean Energy': 'US Clean Energy',
        'Spectrum Energy': 'Spectrum Energy',
        'Solar Spectrum': 'Solar Spectrum',
        'Solar Home': 'Solar Home',
        'Skyline Solar': 'Skyline Solar',
        'Statewide Solar': 'Statewide Solar',
        'Astrum': 'Astrum Solar',
        'Eznergy': 'Eznergy',
        'Four Point': 'Four Point',
        'Geoscape': 'Geoscape',
        'Green Power Energy': 'Green Power Energy',
        'Green Power Solution': 'Green Power Solution',
        'Jersey Solar': 'Jersey Solar',
        'Kaitanna': 'Kaitanna Solar',
        'Kopp Electric': 'Kopp Electric',
        'Mercury Solar System': 'Mercury Solar Systems',
        'NJR Home': 'NJR Home Services',
        'NJRClean': 'NJRClean Energy Ventures Corp',
        'Rec Solar': 'Rec Solar',
        'Reliable Power': 'Reliable Power & Solar',
        'Roof Diagnostics': 'Roof Diagnostics',
        'Solar Energy World': 'Solar Energy World',
        'Helios Solar Energy': 'Helios Solar Energy',
        'Solular': 'Solular',
        'Sun Up': 'Sun Up Zero Down',
        'Moore Energy': 'Moore Energy',
        'Meridian Property': 'Meridian Property Services',
        'Kiss': 'Kiss Electric',
        'JRC Construction': 'JRC Construction',
        'ASC Solar': 'ASC Solar Solutions',
        'Alien Fuel': 'Alien Fuel',
        'Dobtol': 'Dobtol Construction',
        'ECS': 'ECS Energy',
        'Energy Solutions of New Jersey': 'Energy Solutions of New Jersey',
        'Evoke': 'Evoke Solar',
        'Green Cities': 'Green Cities Energy',
        'Green Sun': 'Green Sun Energy',
        'Ocean Solar': 'Ocean Solar',
        'P3 Integration': 'P3 Integration',
        'Purharvest Energy': 'Purharvest Energy',
        'Power Installs': 'Power Installs',
        'Ryan Inc': 'Ryan Inc',
        'Safari Energy': 'Safari Energy',
        'Shore Green Energy': 'Shore Green Energy',
        'ISI Solar': 'ISI Solar',
        'Solar Energy Is Power': 'Solar Energy Is Power',
        'Sun Saver': 'Sun Saver Solar Systems',
        'Sundurance': 'Sundurance Energy',
        'Sunshine Solar': 'Sunshine Solar Systems',
        'Solar Advantage': 'Solar Advantage',
        'Accord Power': 'Accord Power',
        'Geopeak': 'GeoPeak Energy',
        'Go Solar Electric': 'Go Solar Electric',
        'Suntuity': 'Suntuity',
        'Infinity Solar': 'Infinity Solar Systems',
        'Vanguard': 'Vanguard Energy Partners',
        'Genrenew': 'GenRenew LLC',
        'Direct Energy Solar': 'Direct Energy Solar',
        'Powell Energy': 'Powell Energy and Solar',
        'Sundial Solar': 'Sundial Solar Innovations',
        'Impact': 'Impact Solar',
        'Greentech': 'Greentech Solar USA LLC',
        'Grid Revolu': 'Grid Revolution Solar',
        'Panatec': 'Panatech Corporation',
        'Azimuth': 'Azimuth Renewable Energy'
    }
    for contractor_company in contractor_companies:
        df.loc[df['Contractor_Company'].str.contains(contractor_company, na=False, case=False), 'Contractor_Company'] = contractor_companies[contractor_company]

    and_contractor_companies = {
        'Patel Builders': ['Patel', 'Builder'],
        'RCL Enterprises': ['RCL', 'terprise'],
        'Morgan Associates': ['Morgan', 'Associates'],
        'George J Keller & Sons': ['Keller', 'Son'],
        'Trinity Solar': ['Trinity', 'Solar'],
        'Tesla': ['Sola', 'City'],
        'All Season Solar': ['All', 'Season'],
        'Sea Bright Solar': ['Sea', 'Bright'],
        'Advanced Solar & Energy Solutions': ['Advanced Solar', 'Solution'],
        'East Coast Solar': ['East', 'Coast'],
        'Paradise Solar': ['Paradise', 'Solar'],
        'Paradise Energy Solutions': ['Paradise', 'Energy'],
        'Amped On Solar': ['Amped', 'Solar'],
        'Nova Alternative Energy Solutions': ['Nova', 'Alternative'],
        'Alternative Electric': ['Alternative', 'Electric'],
        'A Clear Alternative': ['Clear', 'Alternative'],
        'Clear Skies Solar': ['Clear', 'Ski'],
        'NJ Solar Power': ['NJ Solar', 'Power'],
        'American Renewable Energy': ['American', 'Renewable'],
        'Momentum Solar': ['Momentum', 'Solar'],
        'Self Install': ['Self', 'Install'],
        'LB Electric': ['LB', 'Electric'],
        'KG Solar & Renewable Energy': ['KG Solar', 'Renewable'],
        'Enter Solar': ['Enter', 'Solar'],
        'Green Point Energy': ['Green', 'Point'],
        'OneRoof Energy': ['One', 'Roof'],
        'Pro-Tech Energy Solutions': ['Pro', 'Tech'],
        'Pfister Energy': ['Pfister', 'Energy'],
        'Pfister Maintenance': ['Pfister', 'Maintenance'],
        'SunnyMac': ['Sunny', 'Mac'],
        'Greenhouse Solar': ['Green', 'House']
    }

    df.loc[(df['Contractor_Company'].str.contains('Solar Energy Systems', na=False, case=False)) & (~df['Contractor_Company'].str.contains('Arosa', na=False, case=False)), 'Contractor_Company'] = 'Solar Energy Systems'
    df.loc[(df['Contractor_Company'].str.contains('Pro Custom', na=False, case=False)) & (~df['Contractor_Company'].str.contains('Momentum', na=False, case=False)), 'Contractor_Company'] = 'Pro Custom Solar'
    df.loc[(df['Contractor_Company'].str.contains('Solar Me', na=False, case=False)) & (~df['Contractor_Company'].str.contains('Medix', na=False, case=False)), 'Contractor_Company'] = 'Solar Me'
    df.loc[(df['Contractor_Company'].str.contains('DC Solar', na=False, case=False)) & (~df['Contractor_Company'].str.contains('AC', na=False, case=False)), 'Contractor_Company'] = 'DC Solar'
    df.loc[(df['Contractor_Company'].str.contains('SI Solar', na=False, case=False)) & (~df['Contractor_Company'].str.contains('ISI', na=False, case=False)), 'Contractor_Company'] = 'SI Solar'
    df.loc[(df['Contractor_Company'].str.contains('Smart Energy', na=False, case=False)) & (~df['Contractor_Company'].str.contains('Northeast', na=False, case=False)), 'Contractor_Company'] = 'Smart Energy Group'

    for and_contractor_company in and_contractor_companies:
        first_query = and_contractor_companies[and_contractor_company][0]
        second_query = and_contractor_companies[and_contractor_company][1]
        search_query = (df['Contractor_Company'].str.contains(first_query, na=False, case=False)) & (df['Contractor_Company'].str.contains(second_query, na=False, case=False))
        df.loc[search_query, 'Contractor_Company'] = and_contractor_company

    or_contractor_companies = {
        'G&S Solar Installers': ['G \+ S', 'G&S'],
        'Miller Brothers': ['301 Al', 'Miller Bro'],
        'ACE Solar': ['Alliance Coop', 'Ace Solar']
    }
    for or_contractor_company in or_contractor_companies:
        first_query = or_contractor_companies[or_contractor_company][0]
        second_query = or_contractor_companies[or_contractor_company][1]
        search_query = (df['Contractor_Company'].str.contains(first_query, na=False, case=False)) | (df['Contractor_Company'].str.contains(second_query, na=False, case=False))
        df.loc[search_query, 'Contractor_Company'] = or_contractor_company

    writer = pd.ExcelWriter('Cleaned_NJ_Pipeline_Data_August21.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Data')
    writer.save()

def Full_Install():
    # df = pd.read_excel('DATA+-+INSTALLED+-+August+2021.xlsx', sheet_name='TI - INSTALLED')
    df = pd.read_excel('C:\Hold\DATA+-+INSTALLED+-+August+2021.xlsx', sheet_name='TI - INSTALLED')
    df.columns = ['TI_Application_Number', 'SRP_Registration_Number', 'Program', 'Premise_Last_Name', 'Premise_Company', 'Premise_Installation_Address_Commercial_Only', 'Premise_City', 'Premise_Zip', 'County_Code', 'PTO_Date_Interconnection_Date', 'Calculated_Total_System_Size', 'Customer_Type', 'Third_Party_Ownership', 'Grid_BTM', 'Project_Type', 'Subsection', 'EDC_Program', 'Contractor_Company', 'Electric_Utility_Name', 'Status', 'Registration_Received_Date', 'Acceptance_Date', 'Completion_Date']
    df['Installs'] = 1


    contractor_companies = {
        'Absolutely Energized': 'Absolutely Energized Solar',
        'Trinity Hea': 'Trinity Solar',
        'Trinity Services': 'Trinity Services',
        'Geogenix': 'Geogenix',
        '1st light': '1st Light Energy',
        'Mak': 'Mak Technologies',
        'BP': 'BP Solar International',
        'SunPower Capital': 'SunPower Capital',
        'SunPower Corp': 'SunPower Corporation',
        'Solar Landscape': 'Solar Landscape',
        'RCL Solar': 'RCL Solar',
        'Paladin Solar': 'Paladin Solar',
        'Orbit Energy': 'Orbit Energy',
        'Onforce': 'Onforce Solar',
        'National Energy P': 'National Energy Partners',
        'Morgan Solar': 'Morgan & Morgan Solar',
        'Lucent': 'Lucent Energy Management',
        'Independence': 'Independence Solar',
        'Independent': 'Independent Solar',
        'HESP C': 'HESP Construction',
        'HESP S': 'HESP Solar',
        'Heat Shed': 'Heat Shed',
        'Group Solar': 'Group Solar',
        'Grid Alternative': 'Grid Alternatives',
        'Grid Rev': 'Grid Revolution Solar',
        'Gridpoint': 'Gridpoint Services',
        'Grid Holding': 'Urban Grid Holdings',
        'Green Hybrid': 'Green Hybrid Energy Solutions',
        'Green Energy Con': 'Green Energy Construction & Consulting',
        'Evergreen Energy': 'Evergreen Energy',
        'First Power': 'First Power & Light',
        'Eastern Energy': 'Eastern Energy Services',
        'Dynamic Energy': 'Dynamic Energy',
        'Tesla': 'Tesla',
        'Vivint': 'Vivint',
        'Sunrun': 'Sunrun',
        'NRG': 'NRG',
        'Acos': 'ACOS',
        'Advanced Solar Product': 'Advanced Solar Products',
        'Advanced Renew': 'Advanced Renewable Solutions',
        'Ecological': 'Ecological Systems',
        'Alteris': 'Alteris Renewables',
        'Surewave': 'Surewave Solar',
        'Whitman': 'Whitman Construction',
        'Amergy': 'Amergy Solar',
        'Aston Solar': 'Aston Solar',
        'Bowman Walker': 'Bowman Walker Construction',
        'Castle Energy': 'Castle Energy',
        'Ad Energy': 'Ad Energy',
        'Amberjack': 'Amberjack Solar',
        'Aztec': 'Aztec Solar',
        'Bap': 'BAP Power Corporation',
        '1st US': '1st US Energy',
        'Adema': 'Adema Technologies',
        'Allied Con': 'Allied Construction',
        'Momentum Solar': 'Momentum Solar',
        'My NJ Solar': 'NJ Solar Power',
        'NJ Solar Solutions': 'NJ Solar Solutions',
        'Powerlution': 'Powerlutions',
        'R U Bright': 'R U Bright',
        'Ray Angelini': 'Ray Angelini',
        'Arosa' : 'Arosa Solar',
        'Breaker Electric': 'Breaker Electric',
        'Code Green': 'Code Green',
        'Sunvest Solar': 'SunVest Solar',
        'Sungevity': 'Sungevity',
        'The Solar Center': 'Solar Center',
        'Samba Energy': 'Samba Energy',
        'Tonetta Electrical': 'Tonetta Electrical Contractor',
        'US Clean Energy': 'US Clean Energy',
        'Spectrum Energy': 'Spectrum Energy',
        'Solar Spectrum': 'Solar Spectrum',
        'Solar Home': 'Solar Home',
        'Skyline Solar': 'Skyline Solar',
        'Statewide Solar': 'Statewide Solar',
        'Astrum': 'Astrum Solar',
        'Eznergy': 'Eznergy',
        'Four Point': 'Four Point',
        'Geoscape': 'Geoscape',
        'Green Power Energy': 'Green Power Energy',
        'Green Power Solution': 'Green Power Solution',
        'Jersey Solar': 'Jersey Solar',
        'Kaitanna': 'Kaitanna Solar',
        'Kopp Electric': 'Kopp Electric',
        'Mercury Solar System': 'Mercury Solar Systems',
        'NJR Home': 'NJR Home Services',
        'NJRClean': 'NJRClean Energy Ventures Corp',
        'Rec Solar': 'Rec Solar',
        'Reliable Power': 'Reliable Power & Solar',
        'Roof Diagnostics': 'Roof Diagnostics',
        'Solar Energy World': 'Solar Energy World',
        'Helios Solar Energy': 'Helios Solar Energy',
        'Solular': 'Solular',
        'Sun Up': 'Sun Up Zero Down',
        'Moore Energy': 'Moore Energy',
        'Meridian Property': 'Meridian Property Services',
        'Kiss': 'Kiss Electric',
        'JRC Construction': 'JRC Construction',
        'ASC Solar': 'ASC Solar Solutions',
        'Alien Fuel': 'Alien Fuel',
        'Dobtol': 'Dobtol Construction',
        'ECS': 'ECS Energy',
        'Energy Solutions of New Jersey': 'Energy Solutions of New Jersey',
        'Evoke': 'Evoke Solar',
        'Green Cities': 'Green Cities Energy',
        'Green Sun': 'Green Sun Energy',
        'Ocean Solar': 'Ocean Solar',
        'P3 Integration': 'P3 Integration',
        'Purharvest Energy': 'Purharvest Energy',
        'Power Installs': 'Power Installs',
        'Ryan Inc': 'Ryan Inc',
        'Safari Energy': 'Safari Energy',
        'Shore Green Energy': 'Shore Green Energy',
        'ISI Solar': 'ISI Solar',
        'Solar Energy Is Power': 'Solar Energy Is Power',
        'Sun Saver': 'Sun Saver Solar Systems',
        'Sundurance': 'Sundurance Energy',
        'Sunshine Solar': 'Sunshine Solar Systems',
        'Solar Advantage': 'Solar Advantage',
        'Accord Power': 'Accord Power',
        'Geopeak': 'GeoPeak Energy',
        'Go Solar Electric': 'Go Solar Electric',
        'Suntuity': 'Suntuity',
        'Infinity Solar': 'Infinity Solar Systems',
        'Vanguard': 'Vanguard Energy Partners',
        'Genrenew': 'GenRenew LLC',
        'Direct Energy Solar': 'Direct Energy Solar',
        'Powell Energy': 'Powell Energy and Solar',
        'Sundial Solar': 'Sundial Solar Innovations',
        'Impact': 'Impact Solar',
        'Greentech': 'Greentech Solar USA LLC',
        'Grid Revolu': 'Grid Revolution Solar',
        'Panatec': 'Panatech Corporation',
        'Azimuth': 'Azimuth Renewable Energy'
    }
    for contractor_company in contractor_companies:
        df.loc[df['Contractor_Company'].str.contains(contractor_company, na=False, case=False), 'Contractor_Company'] = contractor_companies[contractor_company]

    and_contractor_companies = {
        'Patel Builders': ['Patel', 'Builder'],
        'RCL Enterprises': ['RCL', 'terprise'],
        'Morgan Associates': ['Morgan', 'Associates'],
        'George J Keller & Sons': ['Keller', 'Son'],
        'Trinity Solar': ['Trinity', 'Solar'],
        'Tesla': ['Sola', 'City'],
        'All Season Solar': ['All', 'Season'],
        'Sea Bright Solar': ['Sea', 'Bright'],
        'Advanced Solar & Energy Solutions': ['Advanced Solar', 'Solution'],
        'East Coast Solar': ['East', 'Coast'],
        'Paradise Solar': ['Paradise', 'Solar'],
        'Paradise Energy Solutions': ['Paradise', 'Energy'],
        'Amped On Solar': ['Amped', 'Solar'],
        'Nova Alternative Energy Solutions': ['Nova', 'Alternative'],
        'Alternative Electric': ['Alternative', 'Electric'],
        'A Clear Alternative': ['Clear', 'Alternative'],
        'Clear Skies Solar': ['Clear', 'Ski'],
        'NJ Solar Power': ['NJ Solar', 'Power'],
        'American Renewable Energy': ['American', 'Renewable'],
        'Momentum Solar': ['Momentum', 'Solar'],
        'Self Install': ['Self', 'Install'],
        'LB Electric': ['LB', 'Electric'],
        'KG Solar & Renewable Energy': ['KG Solar', 'Renewable'],
        'Enter Solar': ['Enter', 'Solar'],
        'Green Point Energy': ['Green', 'Point'],
        'OneRoof Energy': ['One', 'Roof'],
        'Pro-Tech Energy Solutions': ['Pro', 'Tech'],
        'Pfister Energy': ['Pfister', 'Energy'],
        'Pfister Maintenance': ['Pfister', 'Maintenance'],
        'SunnyMac': ['Sunny', 'Mac'],
        'Greenhouse Solar': ['Green', 'House']
    }

    df.loc[(df['Contractor_Company'].str.contains('Solar Energy Systems', na=False, case=False)) & (~df['Contractor_Company'].str.contains('Arosa', na=False, case=False)), 'Contractor_Company'] = 'Solar Energy Systems'
    df.loc[(df['Contractor_Company'].str.contains('Pro Custom', na=False, case=False)) & (~df['Contractor_Company'].str.contains('Momentum', na=False, case=False)), 'Contractor_Company'] = 'Pro Custom Solar'
    df.loc[(df['Contractor_Company'].str.contains('Solar Me', na=False, case=False)) & (~df['Contractor_Company'].str.contains('Medix', na=False, case=False)), 'Contractor_Company'] = 'Solar Me'
    df.loc[(df['Contractor_Company'].str.contains('DC Solar', na=False, case=False)) & (~df['Contractor_Company'].str.contains('AC', na=False, case=False)), 'Contractor_Company'] = 'DC Solar'
    df.loc[(df['Contractor_Company'].str.contains('SI Solar', na=False, case=False)) & (~df['Contractor_Company'].str.contains('ISI', na=False, case=False)), 'Contractor_Company'] = 'SI Solar'
    df.loc[(df['Contractor_Company'].str.contains('Smart Energy', na=False, case=False)) & (~df['Contractor_Company'].str.contains('Northeast', na=False, case=False)), 'Contractor_Company'] = 'Smart Energy Group'

    for and_contractor_company in and_contractor_companies:
        first_query = and_contractor_companies[and_contractor_company][0]
        second_query = and_contractor_companies[and_contractor_company][1]
        search_query = (df['Contractor_Company'].str.contains(first_query, na=False, case=False)) & (df['Contractor_Company'].str.contains(second_query, na=False, case=False))
        df.loc[search_query, 'Contractor_Company'] = and_contractor_company

    or_contractor_companies = {
        'G&S Solar Installers': ['G \+ S', 'G&S'],
        'Miller Brothers': ['301 Al', 'Miller Bro'],
        'ACE Solar': ['Alliance Coop', 'Ace Solar']
    }
    for or_contractor_company in or_contractor_companies:
        first_query = or_contractor_companies[or_contractor_company][0]
        second_query = or_contractor_companies[or_contractor_company][1]
        search_query = (df['Contractor_Company'].str.contains(first_query, na=False, case=False)) | (df['Contractor_Company'].str.contains(second_query, na=False, case=False))
        df.loc[search_query, 'Contractor_Company'] = or_contractor_company

    writer = pd.ExcelWriter('Cleaned_NJ_Full_Install_August21.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Data')
    writer.save()
def run():
    Pipeline()
    Full_Install()

if __name__ == '__main__': #runs when python "name of file" is input
    Pipeline()
    Full_Install()
