# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

from SolarSystem.SystemDesign import SystemDesign
from ContractCreation.Contract import Contract
import requests

class CreateDesignTask:
    def __init__(self, task_id, module_type, opportunity_id, roofs, quote_task):
        self.task_id = task_id
        self.roofs = roofs
        self.module_type = module_type
        self.opportunity_id = opportunity_id
        self.quote_task = quote_task
        self.system_design = SystemDesign(opportunity_id, roofs, None, module_type)
        self.contract = Contract(opportunity_id)

    def complete(self):
        system_name = self.contract.design_name
        data = {
            'sunnovaName':system_name,
            'completed':True
        }
        url = f'http://localhost:6050/api/genesisdesigns/{str(self.task_id)}/task'
        response = requests.put(url, json=data)
        return response.json()
