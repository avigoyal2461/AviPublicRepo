import os
import shutil
from resources.CustomVision.CustomVisionAPI import CustomVisionAPI


cv = CustomVisionAPI()

def sort_images(folder, dst_folder=None):
    """Copies images to subfolder in exports based on their best predicted label."""
    base_folder_name = os.path.basename(folder)
    if not dst_folder:
        dst_folder = os.path.join(os.getcwd(), base_folder_name)
    images = os.listdir(folder)

    for image in images:
        path = os.path.join(folder, image)
        prediction = cv.predict(path)
        subfolder_name = prediction.best_label()
        print(f"Prediction for {path}: {subfolder_name}")
        if not subfolder_name:
            subfolder_name = 'Unidentified'
        dst = os.path.join(dst_folder, subfolder_name)
        if not os.path.exists(dst):
            os.makedirs(dst)
        shutil.copy2(path, dst)

# TEST

def _test_sort_images():
    test_folder = 'C:\\Users\\Kevin\\Desktop\\demo'
    sort_images(test_folder, test_folder)

if __name__ == "__main__":
    _test_sort_images()    
