from connection import SharepointConnection



if __name__ == "__main__":
    a = SharepointConnection()
    # Opportunity = input("Enter a folder to search for / create \n")
    # a.findOpportunity("Goyal, Avi-")
    # a.findOpportunity("Galloni, Ronald-")
    a.findOpportunity("Okafor, Bessem-")
    # a.getOpportunity("Goyal, Avi-")

    # a.searchFolder("Goyal, Avi-", "Archives")
    # a.getFile("Goyal, Avi-", "Archives", "Main_Service_WideShot_Closed_wLabels-30.jpg")
    # a.getFolder("Goyal, Avi-", "Archives")
    # a.getOpportunity("Goyal, Avi-")
    # a.getOpportunity("Goyal, Avi-")
    # a.uploadOpportunity("Goyal, Avi-", r"C:\test\Goyal, Avi-")
    # a.uploadOpportunity("Goyal, Avi-", r"C:\test\Goyal, Avi-")
    a.uploadOpportunity("Okafor, Bessem-", r"C:\test\Okafor, Bessem-")
    # a.uploadOpportunity("Galloni, Ronald-", r"C:\test\Galloni, Ronald-\Galloni, Ronald-")
    # a.uploadFile("Goyal, Avi-", "Archives", "GENESIS - 210 Holman St  Lunenburg  MA.skp", r"C:\test\Galloni, Ronald-\Galloni, Ronald-\Site Info-Designs\Site Info Documents\GENESIS - 210 Holman St  Lunenburg  MA.skp")

    # a.find_files("Goyal, Avi-", "Accounting")
    # a.create_file_structure("Goyal, Avi-")
    # folder_input = input("Enter 1 if you would like to get files by folder, options include: Applications, Sales Documents, Job Photos, Archive, Site Info-Designs, Installation Documents, Miscellaneous Documents, Contract Documents, Accounting, Archives \n")
    # if str(folder_input) == "1":
    #     folder_input = input("Please Enter the Folder you want to search from \n")
    #     print(a.find_files(Opportunity, folder_input))

        # self.dir = os.getcwd()
        # self.local_excel_path = r"C:\Users\dood2\Desktop\AtomPython\SiteCapture\Downloads\temp\project_id.xlsx"
        # #https://us.flow.microsoft.com/manage/environments/Default-f1006ee5-f888-4308-92ea-fcaebe1c0b5e/flows/c79ffe95-526e-4377-bcd5-033f9560be68
        # self.post_to_sharepoint_url = "https://prod-190.westus.logic.azure.com:443/workflows/0249bcde7aaf4db194f5db01f1306d36/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=G8FMDZUvp-WqwkvZihPFLDc-iJC82Gr3bcUsmjsmMNY"
        # # os.remove(self.local_excel_path)
        # self.local_pictures_path = r"C:\Users\dood2\Desktop\AtomPython\SiteCapture\Downloads\tempPics\temp.zip"
        # self.extract_file = r"C:\Users\dood2\Desktop\AtomPython\SiteCapture\Downloads\tempPics\temp"
        # # self.ctx = self.connect()

            # try:
            #     ctx = ClientContext(self.url, ctx_auth)
            #     folder = ctx.web.get_folder_by_server_relative_url(relative_path)
            #     applications = ctx.web.folders.add(f"{relative_path}/Applications")
            #     salesDocuments = ctx.web.folders.add(f"{relative_path}/Sales Documents")
            #     jobPhotos = ctx.web.folders.add(f"{relative_path}/Job Photos")
            #     archive = ctx.web.folders.add(f"{relative_path}/Archive")
            #     siteInfoDesigns = ctx.web.folders.add(f"{relative_path}/Site Info-Designs")
            #     installationDocuments = ctx.web.folders.add(f"{relative_path}/Installation Documents")
            #     miscelleaneousDocuments = ctx.web.folders.add(f"{relative_path}/Miscellaneous Documnets")
            #     contractDocuments = ctx.web.folders.add(f"{relative_path}/Contract Documents")
            #     accounting = ctx.web.folders.add(f"{relative_path}/Accounting")
            #     archives = ctx.web.folders.add(f"{relative_path}/Archives")
            #
            #     ctx.execute_query()
            # except:
            #     return f"Failed to Create File Structure for {relative_path}"
