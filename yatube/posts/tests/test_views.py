import tempfile

from django import forms
from django.core.cache import cache
from django.test import Client, override_settings
from django.urls import reverse

from posts.models import Follow, Post, User
from posts.views import PAGENUM

from .test_forms import Fixtures


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostsViewsTests(Fixtures):

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                ('posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': 'auth'}):
                ('posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                ('posts/post_detail.html'),
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                ('posts/create_post.html'),
        }
        for reverse_name, url in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, url)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_0 = response.context['page_obj'][1]
        self.assertEqual(post_0, self.post)
        self.assertTrue(post_0.image)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        groupname = response.context['group']
        posts = response.context['page_obj']
        self.assertIn('page_obj', response.context)
        for post in posts:
            self.assertEqual(post.group, self.group)
            self.assertTrue(post.image)
        self.assertEqual(groupname, self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        post_0 = response.context['page_obj'][0]
        author = post_0.author
        num = response.context['num']
        self.assertEqual(author, self.user)
        self.assertEqual(num, 1)
        self.assertTrue(post_0.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        num = response.context['num']
        post = response.context['post']
        self.assertEqual(post, self.post)
        self.assertEqual(num, 1)
        self.assertTrue(post.image)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        post = response.context['post']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(post, self.post)

    def test_post_not_in_wrong_group_list_context(self):
        """Пост не попадает на страницу иной группы"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'group2-slug'})
        )
        posts = response.context['page_obj']
        self.assertNotIn(self.post, posts)

    def test_add_comment(self):
        """Проверка корректности работы комментариев"""
        response = self.guest_client.get(
            reverse('posts:add_comment', kwargs={'post_id': '1'})
        )
        self.assertEqual(len(self.post.comments.all()), 1)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment')

    def test_index_cache_working(self):
        """Проверка, что посты на главной странице кэшируются"""
        response_1 = self.authorized_client.get(reverse('posts:index'))
        context_1 = response_1.context['page_obj']
        Post.objects.filter(pk=0).delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        context_2 = response_2.context['page_obj']
        self.assertEqual(list(context_1), list(context_2))
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        context_3 = response_3.context['page_obj']
        self.assertNotEqual(context_1, context_3)

    def test_profile_follow_working(self):
        """Подписка возможна"""
        author = self.user2
        following_check = Follow.objects.filter(
            user=self.user,
            author=author
        ).exists()
        self.assertEqual(following_check, False)
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'auth2'})
        )
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=author
        ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth2'}
        ))

    def test_follow_index_works_correctly_after_follow(self):
        """Пост появляется у авторизованного
        пользователя на странице /follow"""
        Follow.objects.create(
            user=self.user,
            author=self.user2
        )
        response_index = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        follow_posts = response_index.context['page_obj']
        self.assertIn(self.post2, follow_posts)

    def test_profile_unfollow_working(self):
        """Отписка возможна"""
        Follow.objects.create(
            user=self.user,
            author=self.user2
        )
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.user2
        ).exists()
        )
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'auth2'})
        )
        try:
            following = Follow.objects.get(user=self.user, author=self.user2)
        except Follow.DoesNotExist:
            following = None
        self.assertEqual(following, None)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth2'}
        ))

    def test_follow_index_works_correctly_after_unfollow(self):
        """Пост исчезает у авторизованного пользователя со страницы /follow"""
        unsubscribed_user = User.objects.create_user(
            username='unsubscribed_user'
        )
        authorized_client = Client()
        authorized_client.force_login(unsubscribed_user)
        authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'auth2'})
        )
        response_index = authorized_client.get(
            reverse('posts:follow_index')
        )
        follow_posts = response_index.context['page_obj']
        self.assertNotIn(self.post2, follow_posts)


class PaginatorViewsTest(Fixtures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        posts = [
            Post(
                author=cls.user,
                text=f'Тестовый текст1984№ {i}',
                group=cls.group)
            for i in range(10)
        ]
        Post.objects.bulk_create(posts)

    def test_paginator(self):
        """Проверка работы паджинатора"""
        page_obj_num = {
            reverse('posts:index'): PAGENUM,
            reverse('posts:index') + '?page=2': 2,
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): PAGENUM,
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            + '?page=2': 2,
            reverse('posts:profile', kwargs={'username': 'auth'}): PAGENUM,
            reverse('posts:profile', kwargs={'username': 'auth'})
            + '?page=2': 1,
        }
        for reverse_name, page_num in page_obj_num.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), page_num)
