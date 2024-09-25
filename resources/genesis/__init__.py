import datetime
import base64
import os
from resources.customlogging import Logger
from resources.AutobotEmail.Email import Email
from resources.AutobotEmail.Outlook import outlook


class GenesisLogger(Logger):
    QUEUE_PATH = f'./queue.log'

    def __init__(self) -> None:
        super().__init__()
        self.TODAY = datetime.date.today().strftime(f"%m_%d")
        self.OUTPUT_PATH = f'./logs/genesis_completed_{self.TODAY}.log'
        self.outlook = outlook

    def complete(self, opportunity_id):
        """
        Adds an opportunity to the completed log.
        """
        with open(self.OUTPUT_PATH, 'a') as output_file:
            output_file.writelines(opportunity_id + '\n')

    def send(self, address='power.automateteam@trinity-solar.com'):
        """
        Sends the current output to the given email.
        """
        email = Email(subject='Genesis Finalizer Report',
                      body='Please see attached.')
        email.add_recipient(address)
        with open(self.OUTPUT_PATH, 'rb') as output_file:
            encoded_string = base64.b64encode(output_file.read())
            file_content = encoded_string.decode('utf-8')
            email.add_attachment(
                file_content, name=f'Genesis Report {self.TODAY}.txt')
        self.outlook.send_email(email)

    def add_queue(self, opportunity_id) -> None:
        """
        Adds the given id to the logged queue.
        """
        with open(self.QUEUE_PATH, 'a') as queue:
            queue.write(opportunity_id)

    def reset_queue(self) -> None:
        """
        Resets the queue file.
        """
        try:
            os.remove(self.QUEUE_PATH)
            with open(self.QUEUE_PATH, 'a') as q:
                pass
        except FileNotFoundError:
            pass

    def get_queue(self) -> list:
        """
        Gets the opportunity ids from the queue file.
        """
        with open(self.QUEUE_PATH, 'r') as queue_file:
            content = queue_file.readlines()
        return [line.strip() for line in content]