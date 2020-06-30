import abc
import json
from config import BROKER_HOST, BROKER_PORT, BROKER_USERNAME, BROKER_PASSWORD, BROKER_VHOST
from gateway.send_email_gateway import EmailGateway


class AbstractMessageBroker(abc.ABC):

    @abc.abstractmethod
    def send(self, user, email_type, broker_template):
        raise NotImplementedError


class RabbitMessageBroker(AbstractMessageBroker):

    def send(self, user, email_type, broker_template):
        try:
            email_gateway = EmailGateway(BROKER_HOST, BROKER_PORT, BROKER_USERNAME, BROKER_PASSWORD, BROKER_VHOST)

            # To integrate with mailchimp
            name = user.get("name", "")
            province = user.get("province", "")
            users_s3_path = None
            if "s3_path" in user:
                users_s3_path = user.pop("s3_path")
            try:
                f_name = name.split()[0]
                province = province if province else ""
            except Exception as e:
                f_name = ""
                province = ""
            user["FNAME"] = f_name
            user["LNAME"] = ""
            user["PROVINCE"] = province

            users_array = [user]
            message = {
                "owner_hash": user.get("app_id"),
                "users": users_array,
                "subject": email_type,
                "s3_path": users_s3_path
            }
            email_gateway.send(json.dumps(message), broker_template)
            print("***********************")
            print("Send Email")
            print("***********************")
        except Exception as e:
            print(e)
            pass
