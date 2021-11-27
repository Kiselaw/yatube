from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from .test_forms import Fixtures


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_technology(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(Fixtures):

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_posts_pages(self):
        """Проверка общедоступных страниц приложения posts"""
        page_status_codes = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/auth/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
        }
        for adress, code in page_status_codes.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, code)

    def test_author_can_post_edit(self):
        """Проверка доступности редактирования поста автору"""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404(self):
        """При переходе на несуществующую страницу появляется ошибка - 404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_redirect_anonymous_on_admin_login(self):
        """Редирект анонимного пользователя на страницу авторизации при попытке
        создать пост"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_post_edit_redirect_anonymous_on_admin_login(self):
        """Редирект анонимного пользователя на страницу авторизации при попытке
        редактировать пост"""
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/'
        )

    def test_add_comment(self):
        """Проверка, что комментировать посты может только
        авторизованный пользователь"""
        response = self.guest_client.get(
            reverse('posts:add_comment', kwargs={'post_id': '1'})
        )
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/comment'
        )
