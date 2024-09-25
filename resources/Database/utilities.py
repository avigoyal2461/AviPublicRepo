# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

import Database.models as models
from Database.database import Session, engine

models.Base.metadata.create_all(engine)

db = Session()

# Get DB value from SF utility
utility_conversion = {
    'United Illuminating':'united_illuminating',
    'Eversource (Formerly CL&P)':'eversource',
    'Atlantic City Electric (ACE)':'ace',
    'JCP&L':'jcpl',
    'PSE&G':'pseg',
    'Central Hudson':'central_hudson',
    'ConEdison':'con_ed',
    'Orange & Rockland (ORU)':'or',
    'Met-Ed FirstEnery Corp':'met_ed',
    'PPL Electric Utilities':'ppl',
    'PECO Energy Company':'peco',
    'Penelec':'penelec',
    'Duquesne Light Co.':'duquesne_light'
}

def get_loan_rate(state, utility):
    """Returns a price for a loan in a state with the given utility.
    Args:
        state (str): The state initials.
        utility (str): The utility company as given by Salesforce.
    Returns:
        Int: The price for a given loan. If 0, price was not found.
    """
    state = state.lower()
    if utility in utility_conversion:
        print('Found utility...')
        utility = utility_conversion[utility]
    else:
        utility = 'standard'
    results = db.query(models.Rate).filter(models.Rate.state==state).filter(models.Rate.utility==utility)
    for result in results:
        if result.state == state and result.utility == utility:
            return result.price
    return 0



if __name__ == "__main__":
    test_rate = models.Rate(state='nj', utility='standard', price=300)
    test_rate2 = models.Rate(state='nj', utility='pseg', price=200)
    test_rate3 = models.Rate(state='nj', utility='jcpl', price=100)
    test_rate4 = models.Rate(state='ct', utility='eversource', price=400)
    test_rate5 = models.Rate(state='pa', utility='ppl', price=150)
    print(test_rate)
    print(test_rate2)
    print(test_rate3)
    print(test_rate4)
    print(test_rate5)
    db.add_all([test_rate, test_rate2, test_rate3,test_rate4, test_rate5])
    db.commit()
    print(get_loan_rate('CT', 'Eversource (Formerly CL&P)'))
    get_loan_rate()