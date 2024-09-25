# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
from Flow.FlowUtilities import Flow

flow = Flow()


# Tests
def run_all():
    results = []
    results.append(_test_sort_images())
    return results


def _test_sort_images():
    test_folder = 'C:\\Users\\RPA_Bot_6\\Desktop\\demo 8.18.20'
    flow.sort_images(test_folder)
    return True

# Demo 8.19
def _demo819():
    demo_download = flow.site_capture.download_pictures('Heather Diberardino')
    flow.sort_images(demo_download)


if __name__ == "__main__":
    _demo819()
