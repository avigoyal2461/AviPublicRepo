import sys
import os
sys.path.append(os.environ['autobot_modules'])
model = os.path.dirname(os.path.abspath(__file__))
model = "\\".join([model,"Lead Score V2.pkl"])
import pandas as pd
import joblib
from textblob import TextBlob
from flask_restful import Resource, reqparse
from flask import request, jsonify
from Token import token_required
from datetime import datetime


class LeadScoreV2(Resource):
    def __init__(self):
        self.features = ['TotalMaxModulesPerOpportunity',
        'WeightedShade','WeightedTSRF','TotalDefaultProductionPVWatts',
        'TotalActualProductionPVWatts',	'WeightedProductionMultiplier',	'WarmTransfers',
        'Direct_Additional_Notes__c_sentiment',	'Direct_Additional_Notes__c_subjectivity',
        'knock_to_conversation','knocks_to_not_interested',	'has_battery',
        'has_solar','Connecticut','Massachusetts','New Jersey',	'1','2','Rating 1',	'Rating 2']     
        with open(model, 'rb') as file:
            self.model = joblib.load(file)

    def preprocess(self,json):
        print("loaded model")
        DL = pd.DataFrame(json['DL'])
        OPP = pd.DataFrame(json['OPP'])
        ROOF = pd.DataFrame(json['ROOF'])
        SPOTIO = pd.DataFrame(json['SPOTIO'])
        holding = pd.merge(left=DL,right=OPP, left_on='Id',right_on='Direct_Lead__c', how = 'left')
        holding = pd.merge(left = holding, right = ROOF,left_on='Opportunity__c',right_on='Opportunity__c', how = 'left')
        self.data = pd.merge(left = holding, right = SPOTIO,left_on='OwnerId',right_on='OwnerId', how = 'left')
        print('initialized')
        
    def analyze(self, col='Direct_Additional_Notes__c'):
        # Fill NA/NaN values with empty strings
        self.data[col].fillna('', inplace=True)
        
        # Define a function that applies both sentiment and subjectivity analysis
        def apply_analysis(text):
            analysis = TextBlob(text)
            return analysis.sentiment.polarity, analysis.sentiment.subjectivity
        
        # Apply analysis to the entire column and create new columns for sentiment and subjectivity
        analysis_results = self.data[col].apply(apply_analysis)
        self.data[col + '_sentiment'] = analysis_results.apply(lambda x: x[0]).astype(float)
        self.data[col + '_subjectivity'] = analysis_results.apply(lambda x: x[1]).astype(float)
    
    # Print completion messages
    print('Analyzed sentiment')
    print('Analyzed subjectivity')

    def predict(self):
        """
        Establishes features and target variable, and runs loaded pkl file to make predictions.
        """
        features = self.features
        # establish X an y
        self.X = self.data[features]
        #self.y = self.data[self.target]
        # predict on test data
        self.predictions = self.model.predict(self.X)
        self.probabilities = self.model.predict_proba(self.X)[:, 1]
        self.data['Prediction'] = self.predictions
        self.data['Probability'] = self.probabilities
        print('prediction made')
        # Bin probabilities using the custom bin edges
        # score = pd.cut(self.data['Probability'], bins= bin_edges, labels=bin_labels, right=False)
        # self.data['Lead Score'] = score
    @token_required
    def post(self):   
        try:
            json_data = request.json['json']
        except Exception as e:
            return {"Message", "Please input JSON in the following format: {\"DL\":\"DL JSON\",\"OPP\":\"OPP JSON\",\"ROOF\":\"ROOF JSON\",\"SPOTIO\":\"SPOTIO JSON\"}"}
        try:
            self.preprocess(json_data)
            self.analyze()
            self.predict()
        except Exception as e:
            print(e)
            return { "Message", "Failed to make predictions with given input." }

        columns = ['Prediction', 'Probability', 'Direct_Lead__c']
        data = self.data[columns]
        
        data = data.fillna(-1)
        response = data.to_dict('records')
        return jsonify(response)
