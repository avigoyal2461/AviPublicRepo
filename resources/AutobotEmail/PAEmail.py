from AutobotEmail.Email import Email
from AutobotEmail.Outlook import Outlook

class PowerAutomateEmail():
    """
    An interactive code to send an email with an option of:
    Path - Attatch a file to the email
    email_subject - Add an subject to the email
    text - specific text to add to the email
    html - html of the text added to the email
    email - email addresses we would like to include to the reciever list
    email_recipient - specific email reciever
    """
    def send(path=None, email_subject=None, text=None, html=None, ccs=None, email_recipient=None):
        
        # sender_email = "powerautomateteam@trinity-solar.com"
        if not ccs:
            ccs = []
        
        if not email_recipient:
            email_recipient = "avigoyal@trinity-solar.com"
        
        if not email_subject:
             email_subject = "Base Email Subject"

        if not text:
            text = """\
            This is the Base Email
            """
            
        if not html:
            html = """
            <html>
                <body>
                    <p>
                    This is the Base Email
                    </p>
                </body>
            </html>
            """
        
        built_email = Email(subject=email_subject,
                      body=text)
                    #   recipient=email_recipient)
        built_email.add_recipients(email_recipient)

        for item in ccs:
            built_email.add_cc(item)
        # for receiver in receiver_email:
        #      email.add_recipient(receiver)
        
        if path:
            built_email.add_attachment_from_path(path)
        
        Outlook().send_email(built_email)
