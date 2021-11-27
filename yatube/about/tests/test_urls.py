from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_and_technology(self):
        """Проверка доступности страниц author и technology"""
        page_status_codes = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for address, code in page_status_codes.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)
