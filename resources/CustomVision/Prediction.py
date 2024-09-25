MINIMUM_PROBABILITY = .8

class Prediction:
    def __init__(self, data):
        """Takes CustomVision API response data to create a prediction object."""
        self._data = data
        self.labels = data['predictions']

    def best_label(self):
        label = self.labels[0]
        probability = label['probability']
        if probability > MINIMUM_PROBABILITY:
            return label['tagName']
        else:
            return None
    
    def get_labels(self, minimum_probability=0):
        labels = [label for label in self.labels if label['probability'] > minimum_probability]
        return labels

# TEST

def _test_prediction():
    sample_data = {'predictions':
                     [{'probability':99,'tagName':'Tag99'},
                      {'probability':50,'tagName':'Tag50'},
                      {'probability':10,'tagName':'Tag10'}
                     ]}
    test_prediction = Prediction(sample_data)
    results = []
    results.append({'get_labels':test_prediction.get_labels()})
    results.append({'get_labels_min_40':test_prediction.get_labels(40)})
    results.append({'best_labels':test_prediction.best_label()})
    return results


if __name__ == "__main__":
    print(_test_prediction())
