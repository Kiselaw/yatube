from django.contrib.auth import get_user_model

from .test_forms import Fixtures

User = get_user_model()


class PostModelTest(Fixtures):

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_post_text = post.text[:15]
        self.assertEqual(expected_post_text, str(post))

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))
