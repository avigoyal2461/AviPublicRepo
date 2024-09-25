# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
import shutil
import pytesseract
from PIL import Image
from CustomVision.CustomVisionAPI import CustomVisionAPI
from SiteCapture.SiteCapturePortal import SiteCapturePortal

export = r'C:\\Users\\RPA_Bot_6\\Desktop\\results'


class Flow:
    """Flow 2.0 Utilities. Mainly consists of OCR functions."""
    def __init__(self):
        self.custom_vision = CustomVisionAPI()
        self.site_capture = SiteCapturePortal()


    def sort_images(self, folder):
        """Copies images to subfolder in exports based on their best predicted label."""
        base_folder_name = os.path.basename(folder)
        dst_folder = os.path.join(export, base_folder_name)
        images = os.listdir(folder)

        for image in images:
            path = os.path.join(folder, image)
            prediction = self.custom_vision.predict(path)
            subfolder = prediction.best_label()
            if not subfolder:
                subfolder = 'Unidentified'
            dst = os.path.join(dst_folder, subfolder)
            if not os.path.exists(dst):
                os.makedirs(dst)
            shutil.copy2(path, dst)
        return dst_folder

    def read_image(self, image_path):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text


if __name__ == "__main__":
    sitecapture_path = r'C:\Users\RPAadmin\Desktop\automation\photo downloads\SiteCapture'
    test = Flow()
    for image in os.listdir(sitecapture_path):
        full_path = os.path.join(sitecapture_path, image)
        print(f'Sorting for {full_path}')
        test.sort_images(full_path)
        print(f'Sorted from {full_path}')
