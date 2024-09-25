from AutobotEmail.PAEmail import PowerAutomateEmail

class SunnovaEmail():
    def send(path=None, email_subject=None, text=None, html=None, email=None):
        # paEmail = PowerAutomateEmail()
        # print(path)
        # print(email_subject)
        # print(text)
        # print(html)
        # print(email)
        email = ["jeff.macdonald@trinity-solar.com", "avigoyal@trinity-solar.com"]
        PowerAutomateEmail.send(path=path, email_subject=email_subject, text=text, html=html, email_recipient=email)
        # paEmail.send(path=path, email_subject=email_subject, text=text, html=html, email=email)

