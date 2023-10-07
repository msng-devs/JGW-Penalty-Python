# TODO: permission 관련 수정 필요.
import uuid
import json
import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.common.models import Role, Member

from apps.utils.test_utils import TestUtils


class PenaltyApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 테스트케이스 단계에서 로그가 쌓이는지 확인하기 위해 로깅 레벨을 설정
        logging.disable(logging.NOTSET)

        cls.roles = [
            Role.objects.create(id=1, name="ROLE_GUEST"),
            Role.objects.create(id=2, name="ROLE_USER0"),
            Role.objects.create(id=3, name="ROLE_USER1"),
            Role.objects.create(id=4, name="ROLE_ADMIN"),
            Role.objects.create(id=5, name="ROLE_DEV"),
        ]

        cls.members = [
            Member.objects.create(
                id=str(uuid.uuid4()).replace("-", "")[:28],
                name=f"Test User {i}",
                email=f"testuser{i}@example.com",
                role=cls.roles[i],
            )
            for i in range(3)
        ]

        cls.admin_member = Member.objects.create(
            id="test_member_uid_123456789012",
            name="Test Admin",
            email="testadmin@testmail.com",
            role=cls.roles[3],
        )

    def setUp(self):
        self.client = APIClient()
        self.penalty_data = {}

        self.test_member_uid = self.admin_member.id
        self.test_role_id = 4

        self.another_member_uid = self.members[-1].id

        self.penalty_data = [
            {
                "target_member_id": self.test_member_uid,
                "reason": "this is test penalty",
                "type": True,
            }
        ]
        self.penalty_id = TestUtils.create_test_data(
            self.client,
            reverse("penalty_list"),
            self.penalty_data,
        )[0]

    def test_add_penalty(self):
        penalty_url = reverse("penalty_list")

        # given
        self.client = TestUtils.add_header(
            self.client, self.test_member_uid, self.test_role_id
        )

        self.penalty_data = [
            {"target_member_id": self.test_member_uid, "reason": "test", "type": True},
            {"target_member_id": self.test_member_uid, "reason": "test", "type": True},
        ]

        # when
        response = self.client.post(
            penalty_url,
            data=json.dumps(self.penalty_data),
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.json()["message"], "총 (2)개의 Penalty를 성공적으로 추가했습니다!")
        self.assertEqual(len(response.json()), 2)

    def test_get_penalty_by_id_with_admin(self):
        # given
        self.client = TestUtils.add_header(
            self.client, self.test_member_uid, self.test_role_id
        )

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": self.penalty_id})

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())

    def test_get_penalty_by_id_with_no_admin_self(self):
        # given
        penalty_data = [
            {
                "target_member_id": self.another_member_uid,
                "reason": "test 1",
                "type": True,
            }
        ]

        penalty_id = TestUtils.create_test_data(
            self.client, reverse("penalty_list"), penalty_data
        )
        self.client = TestUtils.add_header(self.client, self.another_member_uid, 3)

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": penalty_id[0]})

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())

    def test_get_penalty_by_id_with_no_admin_auth_error(self):
        # given
        self.client = TestUtils.add_header(self.client, self.another_member_uid, 3)

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": self.penalty_id})

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIsNotNone(response.json())
        self.assertEqual(response.json()["code"], "PM-AUTH-001")

    def test_get_penalty_all_with_admin_no_self(self):
        # given
        penalty_data = [
            {
                "target_member_id": self.test_member_uid,
                "reason": "test 1",
                "type": True,
            },
            {
                "target_member_id": self.test_member_uid,
                "reason": "test 2",
                "type": True,
            },
        ]
        TestUtils.create_test_data(self.client, reverse("penalty_list"), penalty_data)
        self.client = TestUtils.add_header(
            self.client, self.test_member_uid, self.test_role_id
        )

        # when
        penalty_url = reverse("penalty_list")

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(len(response.json().get("results")), 3)

    def test_get_penalty_all_with_admin_self(self):
        # given
        self.client = TestUtils.add_header(
            self.client, self.test_member_uid, self.test_role_id
        )

        # when
        penalty_url = reverse("penalty_list")
        penalty_url += "?targetMember={}".format(self.test_member_uid)

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        response_data = response.json().get("results")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0].get("target_member_id"), self.test_member_uid)

    def test_get_penalty_all_with_no_admin_self(self):
        # given
        # self.__add_penalty(target_member_uid=self.members[0].id)
        # self.__add_penalty(
        #     target_member_uid=self.members[1].id, reason="another penalty detail"
        # )
        # self.__add_penalty(target_member_uid=self.members[1].id, reason="hehe")
        penalty_data = [
            {
                "target_member_id": self.another_member_uid,
                "reason": "this is another penalty data",
                "type": True,
            },
        ]
        TestUtils.create_test_data(self.client, reverse("penalty_list"), penalty_data)
        self.client = TestUtils.add_header(self.client, self.another_member_uid, 3)

        # when
        penalty_url = reverse("penalty_list")
        penalty_url += "?targetMember={}".format(self.members[-1].id)

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(len(response.json().get("results")), 1)
        self.assertEqual(
            response.json().get("results")[0].get("target_member_id"),
            self.members[-1].id,
        )

    def test_get_penalty_all_with_no_admin_with_auth_error(self):
        # given
        # self.__add_penalty(target_member_uid=self.members[1].id, reason="hehe")
        self.client = TestUtils.add_header(self.client, self.another_member_uid, 3)

        # when
        penalty_url = reverse("penalty_list")

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIsNotNone(response.json())
        self.assertEqual(response.json()["code"], "PM-AUTH-001")

    def test_delete_penalty(self):
        # given
        # penalty_id = self.__add_penalty(target_member_uid=self.members[0].id)
        self.client = TestUtils.add_header(
            self.client, self.test_member_uid, self.test_role_id
        )

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": self.penalty_id})

        response = self.client.delete(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_penalty_all(self):
        # given
        penalty_data = [
            {
                "target_member_id": self.another_member_uid,
                "reason": "test 1",
                "type": True,
            },
            {
                "target_member_id": self.another_member_uid,
                "reason": "test 2",
                "type": True,
            },
        ]
        data = TestUtils.create_test_data(
            self.client, reverse("penalty_list"), penalty_data
        )

        self.client = TestUtils.add_header(
            self.client, self.test_member_uid, self.test_role_id
        )

        # when
        penalty_url = reverse("penalty_list")

        data = {"penalty_ids": data}

        response = self.client.delete(
            penalty_url,
            data=json.dumps(data),
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(response.data["message"], "총 (2)개의 Penalty를 성공적으로 삭제했습니다!")

    def test_update_penalty(self):
        # given
        # penalty_id = self.__add_penalty(target_member_uid=self.members[0].id)
        self.client = TestUtils.add_header(
            self.client, self.test_member_uid, self.test_role_id
        )

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": self.penalty_id})

        data = {
            "reason": "modified penalty reason",
            "type": True,
        }

        response = self.client.put(
            penalty_url, data=json.dumps(data), content_type="application/json"
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(response.json()["reason"], "modified penalty reason")

    def test_update_penalty_all(self):
        # given
        penalty_data = [
            {
                "target_member_id": self.another_member_uid,
                "reason": "test 1",
                "type": True,
            },
            {
                "target_member_id": self.another_member_uid,
                "reason": "test 2",
                "type": True,
            },
        ]
        data = TestUtils.create_test_data(
            self.client, reverse("penalty_list"), penalty_data
        )
        self.client = TestUtils.add_header(
            self.client, self.test_member_uid, self.test_role_id
        )

        # when
        penalty_url = reverse("penalty_list")

        data = [
            {
                "id": data[0],
                "reason": "new penalty 1 reason",
                "type": True,
            },
            {
                "id": data[1],
                "reason": "new penalty 2 reason",
                "type": True,
            },
        ]

        response = self.client.put(
            penalty_url, data=json.dumps(data), content_type="application/json"
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(len(response.json()), 2)
        # self.assertEqual(response.data["message"], "총 (2)개의 Penalty를 성공적으로 업데이트 했습니다!")

        check_response = self.client.get(
            penalty_url,
            content_type="application/json",
        )
        self.assertEqual(check_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(check_response.json())

        self.assertIn("new penalty 1 reason", response.json()[0].get('reason'))
        self.assertIn("new penalty 2 reason", response.json()[1].get('reason'))

    def tearDown(self):
        # 로그 레벨을 다시 원래대로 돌려놓음
        logging.disable(logging.CRITICAL)
