from resources.Box.BoxAPI import BoxAPI

# box_api = BoxAPI(Application="OneButton")

class BoxAppValidation:
    def __init__(self, app): 
        self.box_api = BoxAPI(access_token=None, application=app)