# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
import requests
from CustomVision.Prediction import Prediction
from CustomVision.config import IMAGE_FILE_URL, IMAGE_FILE_HEADERS



class CustomVisionAPI:
    """Custom Vision API Integration"""
    def __init__(self):
        pass

    def request_image_prediction_data(self, image_path) -> requests.Response:
        with open(image_path, 'rb') as file_data:
            data = file_data.read()
        response = requests.post(IMAGE_FILE_URL,
                                data=data,
                                headers=IMAGE_FILE_HEADERS)
        return response

    def predict(self, image_path) -> Prediction:
        """Creates a new prediction from an image location."""
        try:
            response = self.request_image_prediction_data(image_path)
            return Prediction(response.json())
        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    test_img = r'C:\\Users\\RPA_Bot_6\\Desktop\\demo\\2507.JPG'
    cv = CustomVisionAPI()
    test_prediction = cv.predict(test_img)
    print(test_prediction.best_label())
    print(test_prediction._data)