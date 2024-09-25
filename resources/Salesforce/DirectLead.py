class DirectLead:
    def __init__(self, path, referral=False):
        self.path = path
        self.referral = referral
        self.name = self._get_name_from_path()

    def get_path(self):
        return self.path

    def is_referral(self):
        return self.referral

    def get_name(self):
        return self.name
    
    def _get_name_from_path(self): 
        if self.path[-13:][:3] == 'DL-':
            file_name = self.path[-13:]
            print('--The old DL digit id: ',file_name)
        else:
            file_name = self.path[-14:]
            print('--The expanded DL digit id: ',file_name)
        return file_name.replace('.txt', '')

    def __str__(self):
        return self.name
        