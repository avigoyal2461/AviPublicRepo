# from OpenAI.chatgpt import openAI, ChatGPT_API
from api.Dashboard.routes import getDashboard, getTSA  # , Dashboard, TSADash
from api.Email import VerificationCode

# from api.genesis import GenesisFinalizerTasks
from resources.Configs.app_config import ConfigClass
from api.box.getToken import GetToken
from api.box.file import BoxFile, BoxFilePreFlight, BoxSearchFile, BoxImageFile, BoxFileByFolderID
from api.box.folder import (
    BoxFolderItems,
    BoxOpportunityFolderItems,
    BoxOpportunitySharedLink,
    GetBoxContractFolderId,
    GetBoxApplicationFolderId,
    GetBoxBaseFolder
)
#LEAD SCORE
from api.LeadScore.LeadScoreV2 import LeadScoreV2
#PV WATTS
from api.pv_watts import pv_watts

from api.spotio import SpotioCreateRequest
from api.models.binary_classifier import BinaryClassifier
from api.RoofSquares.process_singlerow import AuroraSingleRowExecution
from resources.customlogging import logger
from api.imageClassification.image_clasification import ImageClassifier
import resources.Validation.api as validation
import json
import datetime

# Flask Imports #
from flask_minify import Minify
from flask_session import Session
from flask_restful import Api  # Resource, Api, #reqparse
from flask_cors import CORS
from flask import Flask
from importlib import import_module
import os

# from resources.Box.CacheClear import CacheClear
from resources.Box.SingleOpportunityBox import SingleOpportunityBox
from resources.Sunnova.SunnovaExcelService import SunnovaExcelService
from RoofSquares.MultiAccountProcess import MultipleAccountProcess
from RoofSquares.SingleAccountProcess import SingleAccountProcess
from RoofingBOM.BOMGeneration import BOMGeneration

# Mapbox #
from Mapbox.MapboxRoofClusterMapping import RoofMapping, StateRoofMapping
from Mapbox.RegionalOfficeMapping_V2 import RegionalOfficeMapping
from Mapbox.OfficeMapping import mapbox_mapping

# from Mapbox.mapbox import RoofMapping, StateCode_PN, StateCode_NJ, StateCode_MA

# Highcharts #
from Highcharts.HighmapsRoofing import ClusterRoofMapping, MappingStateCodes

# sunnova invoice
from SunnovaSystemProject.sunnovaServer import SunnovaSystemProject
from SunnovaSystemProject.sunnovaServer import SunnovaTrueUp

# Swagger-UI Settings #
from flask_apispec.extension import FlaskApiSpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec

# import atexit
# from apscheduler.schedulers.background import BackgroundScheduler
# SECURITY
from resources.Token import token_required

TEMP_DOWNLOADS_FOLDER = os.path.join(os.getcwd(), "temp")
DATETIME_FORMAT = "%b %d %H:%M"
initial_time = datetime.datetime.now().strftime(DATETIME_FORMAT)

# app = Flask(__name__, static_folder='static', template_folder='RPA-Templates')
app = Flask(__name__, static_folder="./client/build", template_folder="RPA-Templates")
CORS(app)
app.config.from_object(ConfigClass)
app.url_map.strict_slashes = False

for module_name in ("authentication", "home"):
    # print(f"apps.{module_name}.routes")
    module = import_module("apps.{}.routes".format(module_name))
    app.register_blueprint(module.blueprint)

module = import_module("api.{}.routes".format("Dashboard"))
app.register_blueprint(module.blueprint)
api = Api(app)
# queue = MasterQueue()

# db.init_app(app)
api.init_app(app)
app.app_context().push()
Session(app)
Minify(app=app, html=True, js=False, cssless=False)
# db.create_all()

logger.info("API Initialized...")

app.config["SWAGGER_UI_JSONEDITOR"] = True
app.config["JSON_SORT_KEYS"] = False
app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024

app.config.update(
    {
        "APISPEC_SPEC": APISpec(
            title="Swagger - BOX Services",
            version="v1",
            plugins=[MarshmallowPlugin()],
            openapi_version="2.0.0",
        ),
        "APISPEC_SWAGGER_URL": "/swagger/",  # URL to access API Doc JSON
        "APISPEC_SWAGGER_UI_URL": "/swagger-ui/",  # URL to access UI of API Doc
    }
)
docs = FlaskApiSpec(app)

# API

# Serve React Webpage


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return app.send_static_file(path)
    else:
        return app.send_static_file("index.html")


# def cache():
#     cache_clear = CacheClear()
#     cache_clear.clear()

# scheduler = BackgroundScheduler()
# #3 hour wait
# scheduler.add_job(func=cache, trigger='interval', seconds=10800)

# scheduler.start()

# atexit.register(lambda: scheduler.shutdown())

# API Declarations

# -------------------------------------- LEAD SCORE 
api.add_resource(LeadScoreV2, '/leadscore')

# -------------------------------------- PV WATTS
api.add_resource(pv_watts, "/api/pvwatts")

# -------------------------------------- Swagger for Box services
api.add_resource(GetToken, "/api/box/getToken")
# docs.register(GetToken)

api.add_resource(BoxFile, "/api/box/file")
# docs.register(BoxFile)

api.add_resource(BoxFileByFolderID, "/api/box/filebyfolderID")
# docs.register(BoxFileByFolderID)

api.add_resource(BoxFilePreFlight, "/api/box/file/preflight")
# docs.register(BoxFilePreFlight)

api.add_resource(
    GetBoxBaseFolder,
    "/api/box/folderid/<string:opportunity_id>/app/<string:app>"
)
docs.register(GetBoxBaseFolder)

api.add_resource(
    BoxFolderItems,
    "/api/box/folder/<string:folder_id>/items",
    "/api/box/folder/<string:folder_id>/items/app/<string:app>",
)
docs.register(BoxFolderItems)

api.add_resource(
    BoxOpportunityFolderItems,
    "/api/box/opportunity/<string:opportunity_id>/<string:folder_name>/items",
    "/api/box/opportunity/<string:opportunity_id>/<string:folder_name>/items/app/<string:app>",
)
docs.register(BoxOpportunityFolderItems)

api.add_resource(
    SingleOpportunityBox,
    "/opportunityboxfetch/<string:box_folder_id>",
    "/opportunityboxfetch/<string:box_folder_id>/app/<string:app>",
)
docs.register(SingleOpportunityBox)

api.add_resource(
    BoxOpportunitySharedLink,
    "/boxSharedLink/<string:box_id>/<string:box_type>/<string:user>",
    "/boxSharedLink/<string:box_id>/<string:box_type>/<string:user>/app/<string:app>",
)
docs.register(BoxOpportunitySharedLink)

api.add_resource(
    GetBoxContractFolderId,
    "/boxContractFolder/<string:parent_folder_id>",
    "/boxContractFolder/<string:parent_folder_id>/app/<string:app>",
)
docs.register(GetBoxContractFolderId)

api.add_resource(
    GetBoxApplicationFolderId,
    "/boxApplicationFolder/<string:opportunity_id>",
    "/boxApplicationFolder/<string:opportunity_id>/app/<string:app>",
)
docs.register(GetBoxApplicationFolderId)

api.add_resource(
    BoxSearchFile,
    "/boxsearchfile/<string:file_name>",
    "/boxsearchfile/<string:file_name>/app/<string:app>",
)
docs.register(BoxSearchFile)

api.add_resource(
    BoxImageFile,
    "/getboximage/<string:file_name>",
    "/getboximage/<string:file_name>/app/<string:app>",
)
docs.register(BoxImageFile)
# ----------------------------------------------------------------

api.add_resource(SpotioCreateRequest, "/api/spotio/createrequest")

# api.add_resource(FBtoSQLServer, '/api/sql/fb')

api.add_resource(MultipleAccountProcess, "/multiaccountprocess/<string:process_date>")
api.add_resource(
    SingleAccountProcess,
    "/singleaccountprocess/<string:account_id>",
    "/singleaccountprocess/<string:account_id>/<int:percentage>",
    "/singleaccountprocess/<string:account_id>/<int:percentage>/<int:force_rerun>"
)
api.add_resource(BOMGeneration, "/getbom/<string:OpportunityId>")

# Mapbox #
api.add_resource(RoofMapping, "/getmaps")
api.add_resource(StateRoofMapping, "/StateCode/<string:state>")
api.add_resource(RegionalOfficeMapping, "/getregionalmaps")
api.add_resource(mapbox_mapping, "/getofficemaps")
# api.add_resource(StateCode_PN,'/StateCode_PN')
# api.add_resource(StateCode_NJ,'/StateCode_NJ')
# api.add_resource(StateCode_MA,'/StateCode_MA')

# Highcharts #
api.add_resource(ClusterRoofMapping, "/getclustermaps")
api.add_resource(MappingStateCodes, "/StateCode/<string:state>")

# OneDocFieldMapping #
# api.add_resource(FormFieldMapping,'/onedocfieldmapping/')
# api.add_resource(DocumateFormFields,'/onedocdocumate')

# sunnova invoices
api.add_resource(SunnovaSystemProject, "/sunnovasysteminvoice")
api.add_resource(SunnovaTrueUp, "/sunnovatrueup")

# OpenAI
# api.add_resource(openAI, '/openAI')
# api.add_resource(ChatGPT_API, '/openAPI')

# Dashboard
api.add_resource(getDashboard, "/processes")
# api.add_resource(Dashboard, '/dashboard')

# TSA dashboard
api.add_resource(getTSA, "/tsaDash")
# api.add_resource(TSADash, '/tsa')

# Sunnova Verification
api.add_resource(VerificationCode, "/sunnovacode")

# Roofing Binary Classifier
api.add_resource(BinaryClassifier, "/api/roofing/BinaryClassifier")

api.add_resource(AuroraSingleRowExecution, '/aurora_singlerow_execution')

api.add_resource(ImageClassifier, '/ImageClassifier')

if __name__ == "__main__":
    app.run(port=6050, host="0.0.0.0", debug=True)


# GRAVEYARD #


# api.add_resource(AccountCreationQueue, '/accountcreation')
# api.add_resource(AccountCreationReferral, '/accountcreationreferral')
# api.add_resource(SolarEdgeSystemBuilder, '/systembuilder')

# api.add_resource(GenesisDesigns, '/salesforce/contract/sunnova')

# api.add_resource(EnphaseSiteRegistration, '/enphase/register')
# prod CC bot
# api.add_resource(ContractCreationSunnovaPreliminary,
#                 '/salesforce/contract/sunnova/new')
# api.add_resource(ContractCreationNonSunnovaPreliminary,
#                 '/salesforce/contract/other/new')

# api.add_resource(Root, '/api/')

# api.add_resource(Login, '/api/login')
# api.add_resource(Register, '/api/register')
# api.add_resource(ChangePassword, '/api/changepassword')

# api.add_resource(BotStatuses, '/api/bots')
# api.add_resource(BotStatus, '/api/bots/<string:bot_name>')

# api.add_resource(BotHistory, '/api/bots/<string:bot_name>/history')
# api.add_resource(BotQueue, '/api/bots/<string:bot_name>/queue')
# api.add_resource(SunnovaExcelService, '/SunnovaExcelOperations/EvaluateFormula')

# api.add_resource(Rates, '/api/rates')
# api.add_resource(RatesSunnova, '/api/rates/sunnova')
# api.add_resource(RatesSunnovaBatch, '/api/rates/sunnova/batch')

# api.add_resource(GenesisFinalizerTasks, '/api/genesis/finalize')

# api.add_resource(GenesisDesigns, '/api/genesisdesigns')
# api.add_resource(GenesisDesign, '/api/genesisdesigns/<int:design_id>')

# api.add_resource(GenesisDesignTask, '/api/genesisdesigns/<int:design_id>/task')
# api.add_resource(GenesisDesignRoofs,
#                 '/api/genesisdesigns/<int:design_id>/roofs')
# api.add_resource(GenesisDesignQuotes,
#                 '/api/genesisdesigns/<int:design_id>/quote')

# api.add_resource(OpenCreateSunnovaDesignTask, '/api/genesisdesigns/open')

# api.add_resource(ContractCreationSunnovaQuote, '/api/contractcreation/quote')
# api.add_resource(ContractCreationSunnovaQuotes,
#                 '/api/contractcreation/quote/<int:quote_id>')
# api.add_resource(FinalizeSunnovaQuote, '/api/contractcreation/quote/finalize')

# api.add_resource(FinalizeOnlyTasks, '/api/contractcreation/finalize')
# api.add_resource(FinalizeTask, '/api/contractcreation/finalize/<int:id>')

# api.add_resource(SiteCaptureTasks, '/api/contractcreation/sitecapture')

# api.add_resource(Disqualify, '/api/contractcreation/disqualify')

# ACCOUNT CREATION
"""
class AccountCreationQueue(Resource):
    @token_required
    def post(self):
        # Set up request parser
        parser = reqparse.RequestParser()
        parser.add_argument('lead', required=True, type=str, location='json')
        parser.add_argument('key', required=True, type=str, location='json')
        args = parser.parse_args()
        # Check for valid api key
        if not validation.is_valid(args['key']):
            return {'status': 'Invalid API Key!'}
        # Add lead to queue
        status = queue.account_creation.add(args['lead'])
        if status == 'success':
            logger.info(f'{args["lead"]} added to Account Creation Queue')
            return {'status': f'Adding {args["lead"]} to Account Creation Queue'}
        else:
            return {'status': f'{status}'}, 400

    def get(self):
        current_queue = queue.account_creation.get_queue()
        return {'Queue': f'{current_queue}'}
"""
"""
class AccountCreationReferral(Resource):
    @token_required
    def post(self):
        # Set up request parser
        parser = reqparse.RequestParser()
        parser.add_argument('lead', required=True, type=str, location='json')
        parser.add_argument('key', required=True, type=str, location='json')
        args = parser.parse_args()
        # Check for valid api key
        if not validation.is_valid(args['key']):
            return {'status': 'Invalid API Key!'}, 403
        # Add lead to queue
        status = queue.account_creation.add(args['lead'], referral=True)
        if status == 'success':
            logger.info(
                f'{args["lead"]} added to Account Creation Referral Queue')
            return {'status': f'Adding {args["lead"]} to Account Creation Referral Queue'}
        else:
            return {'status': f'{status}'}, 400

    def get(self):
        current_queue = queue.account_creation.get_referral_queue()
        return {'Queue': f'{current_queue}'}
"""
"""
class SolarEdgeSystemBuilder(Resource): #to be depricated, unused?
    "POST adds site to queue, GET gets queue"
    @token_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', required=True, type=str, location='json')
        parser.add_argument('site_info', required=True, location='json')
        args = parser.parse_args()
        # Check api key
        #if not validation.is_valid(args["key"]):
        #    return {'status': 'Invalid API Key'}, 403
        # Add system builder to queue
        fixed_arg = args['site_info'].replace(
            r"'", r'"')  # Json loads fails with ticks
        build_json = json.loads(fixed_arg)
        status = queue.system_builder.add(build_json)
        if status == 'success':
            return {'status': f'Adding item to System Builder Queue'}
        else:
            return {'status': f'{status}'}, 400
"""
"""
    def get(self):
        current_queue = queue.system_builder.get_queue_names()
        return {'queue': f'{current_queue}'}
"""
"""
class EnphaseSiteRegistration(Resource):
    "POST adds site to queue, GET gets queue"
    @token_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('key', required=True, type=str, location='json')
        parser.add_argument('site_name', required=True,
                            type=str, location='json')
        parser.add_argument('installer_state', required=True,
                            type=str, location='json')
        parser.add_argument('first_name', required=True,
                            type=str, location='json')
        parser.add_argument('last_name', required=True,
                            type=str, location='json')
        parser.add_argument('email', required=True, type=str, location='json')
        parser.add_argument('street_address', required=True,
                            type=str, location='json')
        parser.add_argument('city_address', required=True,
                            type=str, location='json')
        parser.add_argument('state_address', required=True,
                            type=str, location='json')
        parser.add_argument('zip_address', required=True,
                            type=str, location='json')
        parser.add_argument('finance_partner_email',
                            required=True, type=str, location='json')
        parser.add_argument('micro_count', required=True,
                            type=str, location='json')
        parser.add_argument('finance', required=True,
                            type=str, location='json')
        args = parser.parse_args()
        # Check api key
        #if not validation.is_valid(args["key"]):
        #    return {'status': 'Invalid API Key'}, 403
        # Add system builder to queue
        status = queue.enphase.add(args)
        if status == 'success':
            return {'status': f'Adding item to Enphase Site Registration Queue'}
        else:
            return {'status': f'{status}'}, 400
"""
"""
    def get(self):
        current_queue = queue.enphase.get_queue()
        return {'queue': f'{current_queue}'}
"""
# CONTRACT CREATION PT2, not in use
"""Receives genesis design data for contract creation
class ContractCreationSunnovaDesign(Resource):

    def post(self):
        # Set up request parser
        parser = reqparse.RequestParser()
        parser.add_argument('oppID', required=True, type=str, location='json')
        parser.add_argument('email', required=True, type=str, location='json')
        parser.add_argument('roofs', required=True, type=list, location='json')
        parser.add_argument('key', required=True, type=str, location='json')
        parser.add_argument('module', required=True, type=str, location='json')
        args = parser.parse_args()
        # Check for valid api key
        if not validation.is_valid(args['key']):
            return {'status': 'Invalid API Key!'}, 403
        # Add to contract creation queue
        status = queue.contract_creation.add(args, 'design')
        if status:
            return {'status': status}, 202
        else:
            return {'status': f'Transaction Failed'}, 400

    def get(self):
        return {'queue': queue.contract_creation.get_queue()}
"""
"""Receives genesis design data for contract creation

class ContractCreationSunnovaDesignTest(Resource):

    def post(self):
        # Set up request parser
        parser = reqparse.RequestParser()
        parser.add_argument('oppID', required=True, type=str, location='json')
        parser.add_argument('email', required=True, type=str, location='json')
        parser.add_argument('roofs', required=True, type=list, location='json')
        parser.add_argument('key', required=True, type=str, location='json')
        parser.add_argument('module', required=True, type=str, location='json')
        args = parser.parse_args()
        # Check for valid api key
        if not validation.is_valid(args['key']):
            return {'status': 'Invalid API Key!'}, 403
        # Add to contract creation queue
        status = queue.contract_creation.add_test(args, 'design')
        if status:
            return {'status': status}, 202
        else:
            return {'status': f'Transaction Failed'}, 400

    def get(self):
        return {'queue': queue.contract_creation.get_queue()}
"""
"""
class ContractCreationSunnovaPreliminary(Resource):
    "Endpoint to submit a new Opp that needs photo transfer and usage set."
    @token_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('oppID', required=True, type=str)
        parser.add_argument('key', required=True, type=str)
        parser.add_argument('priority', type=bool)
        args = parser.parse_args()
        priority = False
        # Check for valid api key
        if not validation.is_valid(args['key']):
            return {'status': 'Invalid API Key!'}
        if args['priority']:
            priority = True
        queue.contract_creation.add(args, 'preliminary', priority=priority)
        return {'status': 'OK'}, 202
"""
"""
class ContractCreationNonSunnovaPreliminary(Resource):
    "Endpoint to submit a new Opp that needs photo transfer and usage set that is not Sunnova."
    @token_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('oppID', required=True, type=str)
        parser.add_argument('key', required=True, type=str)
        args = parser.parse_args()
        # Check for valid api key
        if not validation.is_valid(args['key']):
            return {'status': 'Invalid API Key!'}

        queue.contract_creation.add(args, 'non_sunnova_preliminary')
        return {'status': 'OK'}, 202
"""
"""
class Alert(Resource):
    def post(self):
        "Sends an alert to RPA admins."
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, type=str)
        parser.add_argument('message', required=True, type=str)
        parser.add_argument('key', required=True, type=str)
        args = parser.parse_args()
        title = args['title']
        message = args['message']
        if not validation.is_valid(args['key']):
            return {'status': 'Invalid API Key!'}, 401
        # Send email with alert info.
"""
"""
class ContractCreationSunnovaQuotes(Resource):
    def get(self, quote_id):
        result = db.session.query(SunnovaQuote).filter_by(id=quote_id).first()
        if result:
            return result.json()
        else:
            return {'status': 'resource not found'}
"""
"""
    New user submitted quote for an existing genesis design.
    
class ContractCreationSunnovaQuote(Resource):


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('design_id', required=True, type=int)
        parser.add_argument('salesforce_purchase_method', type=str)
        parser.add_argument('sunnova_purchase_method', type=str)
        parser.add_argument('price', type=str)
        parser.add_argument('salesforce_escalator', type=str)
        args = parser.parse_args()
        # Check if system design exist.
        design_id = args['design_id']
        if not args['price']:
            price = None
        else:
            price = int(args['price'].replace('.', ''))
        design = db.session.query(
            GenesisSystemDesign).filter_by(id=design_id).first()
        if design:
            if not args['salesforce_purchase_method']:
                sf_purchase_method = design.opportunity.purchaseMethod
            else:
                sf_purchase_method = args['salesforce_purchase_method']
            quote = SunnovaQuote(price=price,
                                 financingType=sf_purchase_method,
                                 purchaseMethod=args['sunnova_purchase_method'],
                                 escalator=args['salesforce_escalator'],
                                 genesisSystemDesignId=design_id
                                 )
            db.session.add(quote)
            db.session.commit()
            return quote.json(), 201
        else:
            return {'status': 'resource not found'}, 404

"""
"""
class FinalizeSunnovaQuote(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('quote_id', required=True, type=int)
        args = parser.parse_args()
        task = (db.session.query(FinalizeSunnovaQuoteTask, FinalizeTaskInstallationType)
                          .filter(FinalizeSunnovaQuoteTask.quoteId == args['quote_id'])
                          .first())
        if task:
            data = join_json(task)
            installation_types = [
                install_type.installationType for install_type in task[0].installationType]
            data['installationType'] = installation_types
            return data
        else:
            return {'status': 'resource not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('installation_type',
                            required=True, action='append')
        parser.add_argument('quote_notes', type=str)
        parser.add_argument('salesperson_notes', type=str)
        parser.add_argument('permit_payer', type=str)
        parser.add_argument('loi_rate_change_reason', type=str)
        parser.add_argument('quote_id', required=True, type=int)
        args = parser.parse_args()
        task = FinalizeSunnovaQuoteTask(quoteId=args['quote_id'],
                                        loiRateChangeReason=args['loi_rate_change_reason'],
                                        notes=args['quote_notes'],
                                        salespersonNotes=args['salesperson_notes'],
                                        permitPayer=args['permit_payer'])
        db.session.add(task)
        db.session.flush()
        for type in args['installation_type']:
            installation_type = FinalizeTaskInstallationType(installationType=type,
                                                             quoteId=task.id)
            db.session.add(installation_type)
        # Set quote to finalized
        quote = db.session.query(SunnovaQuote).filter_by(
            id=args['quote_id']).first()
        quote.finalized = True
        db.session.commit()
        return task.json(), 201

"""
"""
class OpenCreateSunnovaDesignTask(Resource):
    def get(self):
        open_tasks = db.session.query(
            ContractCreationDesignTask).filter_by(completed=False).all()
        tasks_response = [task.json() for task in open_tasks]
        return tasks_response
"""
"""
class GenesisDesignTask(Resource):
    def put(self, design_id):
        parser = reqparse.RequestParser()
        parser.add_argument('sunnovaName', type=str)
        parser.add_argument('completed', type=bool)
        args = parser.parse_args()
        result = db.session.query(ContractCreationDesignTask).filter_by(
            genesisSystemDesignId=design_id).first()
        if result:
            result.completed = args['completed']
            result.sunnovaName = args['sunnovaName']
            db.session.add(result)
            db.session.commit()
            return result.json()
        else:
            return {'status': 'resource not found'}, 404
"""
"""
class GenesisDesignQuotes(Resource):
    def get(self, design_id):
        result = db.session.query(SunnovaQuote).filter_by(
            genesisSystemDesignId=design_id).first()
        if result:
            return result.json()
        else:
            return {'status': 'resource not found'}, 404
"""
# from api.login import Login, Register, ChangePassword
# from api.contractcreation import FinalizeTask, FinalizeOnlyTasks, SiteCaptureTasks, Disqualify
# from api.genesisDesigns import GenesisDesign, GenesisDesigns, GenesisDesignRoofs
# from api.rates.sunnova import RatesSunnova, RatesSunnovaBatch
# from api.rates import Rates
# from models.contract_creation_models import (GenesisSystemDesign,
#                                             ContractCreationDesignTask,
#                                             SunnovaQuote,
#                                             FinalizeSunnovaQuoteTask,
#                                             FinalizeTaskInstallationType)
# from models import db, join_json
# from api.bots import BotStatus, BotStatuses, BotHistory, BotQueue
# from api import Root
# OneDocFieldMapping #
# from OneDocFieldMapping.OneDocFieldMapping import FormFieldMapping
# from OneDocFieldMapping.OneDocDocumate import DocumateFormFields
