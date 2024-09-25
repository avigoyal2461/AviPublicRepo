
utilities = {
    'ACE':'Atlantic City Electric - New Jersey',
    'JCP&L':'Jersey Central Power',
    'EversourceBill':'Eversource'
}

class ElectricBill:
    """A representation of a basic electric bill."""
    def __init__(self, utility=None, yearly_usage=None, rate=None):
        self.utility = utility
        self.yearly_usage = yearly_usage
        self.rate = rate
        self.proposed_rate = rate

    # Getters and Setters
    # TODO: Need to be modified to get/set Sunnova exclusive strings

    def set_utility(self, utility):
        self.utility = utility

    def set_rate(self, rate):
        self.rate = rate

    def set_yearly_usage(self, yearly_usage):
        self.yearly_usage = yearly_usage

    def get_utility(self):
        """Returns the Sunnova formated string if available, otherwise returns the original string."""
        if self.utility in utilities.keys():
            return utilities[self.utility]
        else:
            return self.utility

    def get_rate(self):
        return self.rate

    def get_yearly_usage(self):
        if self.yearly_usage == 0:
            return ''
        return str(self.yearly_usage)

    def get_proposed_rate(self):
        return self.rate

    def __str__(self):
        return f'{self.utility} bill with yearly usage of {self.yearly_usage} and a rate of {self.rate}.'



if __name__ == "__main__":
    test_bill = ElectricBill('ACE', '12000', 'Residential')
    print(test_bill)