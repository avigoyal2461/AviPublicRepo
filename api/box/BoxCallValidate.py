
from datetime import datetime

def BoxValidate(box_call_location):
    box_Call = open('BoxCallValidate.txt','a')
    box_Call.write('\n')
    box_Call.write(datetime.now().strftime("%d-%m-%Y <Time-%H:%M> "))
    box_Call.write(box_call_location)