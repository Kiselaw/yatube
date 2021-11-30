import shutil
import tempfile
from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class Fixtures(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Группа',
            slug='group2-slug',
            description='Описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст1984',
            group=cls.group,
            image=cls.image,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Какой-то комментарий',
        )
        cls.user2 = User.objects.create_user(username='auth2')
        cls.post2 = Post.objects.create(
            author=cls.user2,
            text='Тестовый текст1985',
            group=cls.group,
            image=cls.image,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(tempfile.gettempdir(), ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostsFormsTests(Fixtures):
    def test_create_post_form(self):
        """Проверка наличия нового поста в базе после отправки формы"""
        posts_count = Post.objects.count()
        form_data = {
            'author': 'auth',
            'text': 'Тестовый текст1',
            'group': '1',
            'image': self.post.image,
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        created_post = Post.objects.get(pk=1)
        posted_image = created_post.image
        self.assertEqual(posted_image, self.post.image)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth'}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=self.post.text,
                group=self.group,
            ).exists()
        )

    def test_post_edit_form(self):
        """Проверка результата редактирования поста"""
        form_data = {
            'author': 'auth',
            'text': 'Тестовый текст2',
            'group': '1',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        postedit = Post.objects.get(pk=1)
        post = self.post
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}
        ))
        self.assertNotEqual(post.text, postedit.text)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовый текст2',
                group=self.group,
            ).exists()
        )


class CommentFormTest(Fixtures):
    """Проверка создания комментария"""
    def test_comment_creating_form(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Какой-то комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}
        ))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=self.comment.text,
            ).exists()
        )
