import os
import shutil

from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZipInfo
from io import BytesIO

from fastai.learner import load_learner
from flask import request,Flask
from flask_restful import Resource, reqparse, Api
from werkzeug.utils import secure_filename
from fastai.vision.utils import resize_images
import pathlib
from contextlib import contextmanager
import sys

sys.path.append(os.environ["autobot_modules"])

app = Flask(__name__)
api = Api(app)
@contextmanager
def set_posix_windows():
    posix_backup = pathlib.PosixPath
    try:
        pathlib.PosixPath = pathlib.WindowsPath
        yield
    finally:
        pathlib.PosixPath = posix_backup

class ImageClassifier(Resource):
    def __init__(self) -> None:
        print("start")
        with set_posix_windows():
            self.model = load_learner(
                # r"C:\Dev\AutoBot\api\models\imageclasification\export_101.pkl"
                r"C:\Users\Rishan\Downloads\AutoBot-master 3\AutoBot-master\api\imageclasification\export_101.pkl"
            )

    # @token_required
    def post(self):
        "Receives a ZipFile and returns the file names which are underlayment pics"

        if "file" not in request.files:
            return "No file part in the request.", 400
        zip_file = request.files["file"]

        if zip_file.filename == "":
            return "No selected file.", 400

        if zip_file:
            filename = secure_filename(zip_file.filename)

        if not filename.endswith(".zip"):
            return "File is not a zip file.", 400
        
        def calculate_occurrence_percentages(my_list):
                count_dict = {}
                total_elements = len(my_list)

                for element in my_list:
                    count_dict[element] = count_dict.get(element, 0) + 1

                percentage_dict = {}
                for element, count in count_dict.items():
                    percentage = (count / total_elements) * 100
                    percentage_dict[element] = percentage

                return percentage_dict
        
        with TemporaryDirectory(dir=r"C:\Users\Rishan\Downloads\AutoBot-master 3\AutoBot-master\temp") as temp_dir:
            zip_file_path = os.path.join(temp_dir, filename)
            zip_file.save(zip_file_path)

            extracted_dir = os.path.join(temp_dir, "extracted")
            with ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(extracted_dir)

            image_list = []
            for root, dirs, files in os.walk(extracted_dir):
                for file in files:
                    if (
                        file.endswith(".png")
                        or file.endswith(".jpg")
                        or file.endswith(".jpeg")
                    ):
                        image_list.append(os.path.join(root, file))       
            model_output = []
            for image in image_list:
                prediction, _, _ = self.model.predict(image)
                model_output.append(prediction)
            print(model_output)
            model_analysis = calculate_occurrence_percentages(model_output)
            return model_analysis

