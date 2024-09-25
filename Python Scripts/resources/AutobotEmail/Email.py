import os
import base64

class Email:
    """
    An email representation. Subject and body can be set immediately or after
    initialization.
    """
    def __init__(self, subject='', body='', recipient=None, html=True):
        self.to = []
        self.cc = []
        self.bcc = []
        self.subject = subject
        self.body = body
        self.attachments = []
        self.id = None


    def set_subject(self, subject):
        """
        Sets the email subject.
        """
        self.subject = subject

    def set_body(self, body):
        """
        Sets the email body text.
        """
        self.body = body

    def set_id(self, email_id):
        """
        Sets the email id.
        """
        self.id = email_id

    def add_attachment(self, content, name='Attachment'):
        """
        Adds an attachment to the email.
        """
        attachment = {
            "@odata.type": "#microsoft.graph.fileAttachment",
            "contentBytes": content,
            "name": name
        }
        self.attachments.append(attachment)

    def add_recipient(self, email_address):
        """
        Adds a recipent to the email.
        """
        to_json = {
            "emailAddress":{
                "address":email_address
            }
        }
        self.to.append(to_json)
        
    def add_attachment_from_path(self, file_path, name=None):
        """
        Adds an attachment to the email using the file name from the path.
        """
        with open(file_path, 'rb') as file_data:
            encoded_string = base64.b64encode(file_data.read())
            content = encoded_string.decode('utf-8')
            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "contentBytes": content,
                "name": os.path.basename(file_path) if not name else name
            }
        self.attachments.append(attachment)

    def add_recipients(self, email_addresses):
        """
        Adds multiple recipients to the email.
        """
        for email_address in email_addresses:
            self.add_recipient(email_address)

    def add_cc(self, email_address):
        """
        Adds an address cc to the email.
        """
        to_json = {
            "emailAddress":{
                "address":email_address
            }
        }
        self.cc.append(to_json)

    def add_bcc(self, email_address):
        """
        Adds an address bcc to the email.
        """
        to_json = {
            "emailAddress":{
                "address":email_address
            }
        }
        self.bcc.append(to_json)


    def json(self) -> dict:
        """
        Returns the json representation as a dictionary of the email.
        """
        email_json = {
            'subject':self.subject,
            'body': {
                'contentType':'Html',
                'content':self.body
            },
            'toRecipients':self.to,
            'ccRecipients':self.cc,
            'attachments':self.attachments
        }
        return email_json

    def __repr__(self):
        return str(self.json())
