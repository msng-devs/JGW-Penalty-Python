import uuid
import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.role.models import Role
from apps.member.models import Member
from apps.penalty.models import Penalty


class PenaltyApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.roles = [
            Role.objects.create(name="ROLE_GUEST"),
            Role.objects.create(name="ROLE_USER0"),
            Role.objects.create(name="ROLE_USER1"),
            Role.objects.create(name="ROLE_ADMIN"),
            Role.objects.create(name="ROLE_DEV"),
        ]

    def setUp(self):
        self.client = APIClient()
        self.penalty_data = {}

        self.admin_member = Member.objects.create(
            id=str(uuid.uuid4()).replace("-", "")[:28],
            name="Test Admin",
            email="testadmin@testmail.com",
            role=Role.objects.get(name="ROLE_ADMIN"),
        )

        self.members = [
            Member.objects.create(
                id=str(uuid.uuid4()).replace("-", "")[:28],
                name=f"Test User {i}",
                email=f"testuser{i}@example.com",
                role=self.roles[i],
            )
            for i in range(3)
        ]

        self.test_member_uid = self.admin_member.id

    def __add_header(self, uid, role_id):
        self.client.credentials(HTTP_USER_PK=uid, HTTP_ROLE_PK=role_id)

    def __add_penalty(self, target_member_uid, reason: str = "this is test penalty"):
        """
        Add Penalty for testing
        """
        penalty_url = reverse("add_penalty")

        self.__add_header(self.test_member_uid, 4)

        self.penalty_data = [
            {"target_member_id": target_member_uid, "reason": reason, "type": True},
        ]

        response = self.client.post(
            penalty_url,
            data=json.dumps(self.penalty_data),
            content_type="application/json",
        )

        # print("Penalty 추가 결과:", response.json())
        return Penalty.objects.first().id

    def test_add_penalty(self):
        penalty_url = reverse("add_penalty")

        # given
        self.__add_header(self.test_member_uid, 4)

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
        self.assertEqual(response.json()["message"], "총 (2)개의 Penalty를 성공적으로 추가했습니다!")

    def test_get_penalty_by_id_with_admin(self):
        # given
        penalty_id = self.__add_penalty(target_member_uid=self.test_member_uid)

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": penalty_id})

        self.__add_header(self.test_member_uid, 4)

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())

    def test_get_penalty_by_id_with_no_admin_self(self):
        # given
        penalty_id = self.__add_penalty(target_member_uid=self.members[0].id)

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": penalty_id})

        self.__add_header(self.members[0].id, 3)

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())

    def test_get_penalty_by_id_with_no_admin_auth_error(self):
        # given
        penalty_id = self.__add_penalty(target_member_uid=self.members[1].id)

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": penalty_id})

        self.__add_header(self.members[0].id, 3)

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
        self.__add_penalty(target_member_uid=self.members[0].id)
        self.__add_penalty(
            target_member_uid=self.members[1].id, reason="another penalty detail"
        )
        self.__add_penalty(target_member_uid=self.members[1].id, reason="hehe")

        # when
        penalty_url = reverse("penalty_list")

        self.__add_header(self.test_member_uid, 4)

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(len(response.json()), 3)

    def test_get_penalty_all_with_admin_self(self):
        # given
        self.__add_penalty(target_member_uid=self.members[0].id)
        self.__add_penalty(
            target_member_uid=self.members[1].id, reason="another penalty detail"
        )
        self.__add_penalty(
            target_member_uid=self.test_member_uid, reason="What's wrong admin?"
        )

        # when
        penalty_url = reverse("penalty_list")
        penalty_url += "?targetMember={}".format(self.test_member_uid)

        self.__add_header(self.test_member_uid, 4)

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0].get("target_member_id"), self.test_member_uid
        )

    def test_get_penalty_all_with_no_admin_self(self):
        # given
        self.__add_penalty(target_member_uid=self.members[0].id)
        self.__add_penalty(
            target_member_uid=self.members[1].id, reason="another penalty detail"
        )
        self.__add_penalty(target_member_uid=self.members[1].id, reason="hehe")

        # when
        penalty_url = reverse("penalty_list")
        penalty_url += "?targetMember={}".format(self.members[0].id)

        self.__add_header(self.members[0].id, 3)

        response = self.client.get(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0].get("target_member_id"), self.members[0].id)

    def test_get_penalty_all_with_no_admin_with_auth_error(self):
        # given
        self.__add_penalty(target_member_uid=self.members[1].id, reason="hehe")

        # when
        penalty_url = reverse("penalty_list")

        self.__add_header(self.members[0].id, 3)

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
        penalty_id = self.__add_penalty(target_member_uid=self.members[0].id)

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": penalty_id})

        self.__add_header(self.test_member_uid, 4)

        response = self.client.delete(
            penalty_url,
            content_type="application/json",
        )

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(response.json().get("penalty_id"), penalty_id)

    def test_delete_penalty_all(self):
        # given
        penalty_1 = self.__add_penalty(target_member_uid=self.members[0].id)
        penalty_2 = self.__add_penalty(
            target_member_uid=self.members[1].id, reason="hehe"
        )

        # when
        penalty_url = reverse("penalty_list")

        self.__add_header(self.test_member_uid, 4)

        data = {"penalty_ids": [penalty_1, penalty_2]}

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
        penalty_id = self.__add_penalty(target_member_uid=self.members[0].id)

        # when
        penalty_url = reverse("penalty_detail", kwargs={"penaltyId": penalty_id})

        self.__add_header(self.test_member_uid, 4)

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
        penalty_1 = self.__add_penalty(target_member_uid=self.members[0].id)
        penalty_2 = self.__add_penalty(
            target_member_uid=self.members[1].id, reason="hehe"
        )

        # when
        penalty_url = reverse("penalty_list")

        self.__add_header(self.test_member_uid, 4)

        data = [
            {
                "id": penalty_1,
                "reason": "new penalty 1 reason",
                "type": True,
            },
            {
                "id": penalty_2,
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
        self.assertEqual(response.data["message"], "총 (2)개의 Penalty를 성공적으로 업데이트 했습니다!")

        check_response = self.client.get(
            penalty_url,
            content_type="application/json",
        )
        self.assertEqual(check_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(check_response.json())

        updated_reasons = [item["reason"] for item in check_response.json()]
        self.assertIn("new penalty 1 reason", updated_reasons)
        self.assertIn("new penalty 2 reason", updated_reasons)

    def tearDown(self):
        pass
