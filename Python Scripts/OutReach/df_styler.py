import pandas as pd
import os
import sys
from datetime import datetime

class Df_Styler():
    """
    Styles DF based on requirements by sheet name
    Most of the df's will take a new and old version, dropping columns from the old one and adding the new column to replace the values - this is to keep existing
    """
    def Variables(old_df):
        """
        Styles the Variables sheet
        """
        columns = old_df.columns.tolist()
        old_df[columns[0]].iloc[9] = datetime.now()
        print(old_df[columns[0]].iloc[9])
        return old_df
    
    def WT(new_df):
        """
        Styles the WT sheet
        """
        sorted_df = new_df.sort_values(['Created Date'], ascending=True)

        return sorted_df
    
    def Demo(new_df):
        """
        Styles the Demo sheet
        """
        sorted_df = new_df.sort_values(['Demo Date'], ascending=True)

        return sorted_df
    
    def Demo_30_Days(new_df):
        """
        Styles Demo last 30 days sheet
        """
        sorted_df = new_df.sort_values(['Demo Date'], ascending=True)

        return sorted_df
    
    def Contracts(new_df):
        """
        Styles the Contracts sheet
        """
        sorted_df = new_df.sort_values(['Lead Generator Office', 'Lead Generator: Full Name'], ascending=[True, True])

        return sorted_df
    
    def No_Rep(new_df):
        """
        Styles the No Rep sheet
        """
        sorted_df = new_df.sort_values(['Start'], ascending=True)
        return sorted_df
    
    def SameDay(new_df):
        """
        Styles the SameDay sheet
        """
        return new_df

    def User(new_df):
        """
        Styles the User sheet
        """
        return new_df

    def Contact(new_df): #needs to update info back to sheet then pull and style
        """
        Styles the WT sheet
        """

        sorted_df = new_df.sort_values(['Total Points', 'Sales Office', 'Start Date', 'Name Formula'], ascending=[False, True, True, True])
        return sorted_df
    
    def Office_Sort(new_df=None): #needs to update info back to sheet then pull and style
        """
        Styles the Office Sort sheet
        """
        sorted_df = new_df.sort_values(['Team Average Power Ranking Points', 'Team Power Ranking'], ascending=[False, True])
        
        return sorted_df

    def Skedulo_Data(new_df):#needs to update info back to sheet then pull and style
        """
        Styles the Skedulo Data sheet
        """
        sorted_df = new_df.sort_values(['Resource Name', 'Tag Rank'], ascending=[True, True])

        return sorted_df

