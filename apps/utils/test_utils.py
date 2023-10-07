# --------------------------------------------------------------------------
# TestCase에서 공통적으로 사용되는 메소드들을 모아놓은 클래스입니다.
# 실제 서비스에서는 사용되지 않습니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
import json


class TestUtils:
    @staticmethod
    def add_header(client, uid, role_id):
        client.credentials(HTTP_USER_PK=uid, HTTP_ROLE_PK=role_id)
        return client

    @staticmethod
    def create_test_data(client, url, data):
        client = TestUtils.add_header(client, "test_member_uid_123456789012", 4)

        response = client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        if isinstance(response.json(), list):
            results = []
            for item in response.json():
                results.append(item["id"])

            return results
        else:
            return (
                response.json()[0]["id"]
                if "id" in response.json()
                # else list(response.json().values())[0]
                else list(response.json())
            )

    @staticmethod
    def verify_response_data(response, expected_data):
        for key, value in expected_data.items():
            assert response.data[key] == value

    def make_test_pull_socket(self, host, port):
        import zmq

        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(f"tcp://{host}:{port}")
        print("PULL Socket Connected at:", port)

        return socket

    def get_message_from_push_socket(self, socket):
        received_message = socket.recv_json()
        print("Recieved Message From PUSH Socket:", received_message)
        return received_message

    def send_mail(self, socket):
        from django.core.mail import EmailMessage

        received_message = socket.recv_json()
        print("Recieved Message From PUSH Socket:", received_message)

        received_message = json.loads(received_message)
        to_email = received_message["to"]
        subject = received_message["subject"]
        message = received_message.get("template", "")

        email = EmailMessage(
            subject,  # 이메일 제목
            message,  # 내용
            to=[to_email],  # 받는 이메일
        )
        result = email.send()
        print("Mail Sent status", result)
