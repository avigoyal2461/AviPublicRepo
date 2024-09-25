try:
	from SalesforceAPI.SFBoxFolderID import SFBoxID
	from SalesforceAPI.SFQuery import SFQuery
	from SalesforceAPI.SFReportToDF import SFReportDF
	from SalesforceAPI.SFConnection import SFConnection
except:
	from resources.SalesforceAPI.SFBoxFolderID import SFBoxID
	from resources.SalesforceAPI.SFQuery import SFQuery
	from resources.SalesforceAPI.SFReportToDF import SFReportDF
	from resources.SalesforceAPI.SFConnection import SFConnection

class SalesforceAPI():#SFConnection):
	def __init__(self):
#		super().__init__()
#		self.connection = super().connect()

		self.box_id = SFBoxID()
		self.report = SFReportDF()
		self.query = SFQuery()
		self.connection = SFConnection()

	def Update(self, sf_item, update_data, id):
		updater = self.query.Update(sf_item, update_data, id)
		return updater

	def Create(self, sf_item, update_data):
		creator = self.query.Create(sf_item, update_data)
		return creator

	def Select(self, query):
		selection = self.query.Select(query)
		return selection

	def Execute(self, query):
		execution = self.query.Execute(query)
		return execution

	def QueryAll(self, query):
		execution = self.query.QueryAll(query)
		return execution

	def Delete(self, sf_item, id):
		deletion = self.query.Delete(sf_item, id)
		return deletion

	def get_box_folder_id(self, opportunityID):
		folder_id = self.box_id.get_box_folder_id(opportunityID)
		return folder_id

	def get_report(self, reportId):
		report = self.report.get_report(reportId)
		return report
	
	def connect(self):
		connection = self.connection.connect()
		return connection


		
