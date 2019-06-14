from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from blog.models import Post


USERNAME1 = 'user1'
PASSWORD1 = 'user1'
USERNAME2 = 'user2'
PASSWORD2 = 'user2'



class PostViewTest(TestCase):

    def setUp(self):
        self.test_user_1 = User.objects.create_user(
            USERNAME1, 'user1@gmail.com', PASSWORD1)
        self.test_user_2 = User.objects.create_user(
            USERNAME2, 'user2@gmail.com', PASSWORD2)
        self.test_post_1 = Post.objects.create(user=self.test_user_1, title='Title 1', body='Lorem ipsum')
        self.url = reverse('blog:post', kwargs={'pk': self.test_post_1.id})

    def test_viewing_post_by_author(self):
        self.client.login(username=USERNAME1, password=PASSWORD1)
        response = self.client.get(self.url)
        self.assertContains(response, 'Update</button>')
        self.assertContains(response, 'Delete</button>')

    def test_viewing_post_by_non_author(self):
        self.client.login(username=USERNAME2, password=PASSWORD2)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Update</button>')
        self.assertNotContains(response, 'Delete</button>')


class PostCreateTest(TestCase):

    def setUp(self):
        self.test_user_1 = User.objects.create_user(
            USERNAME1, 'user1@gmail.com', PASSWORD1)
        self.url = reverse('blog:create_post')

    def test_create_post_by_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'), self.url))

    def test_create_post_by_logged_user(self):
        self.client.login(username=USERNAME1, password=PASSWORD1)

        # Empty fields in form
        response = self.client.post(self.url, {'title': '', 'body': ''})
        self.assertFormError(response, 'form', 'title', 'This field is required.')
        self.assertFormError(response, 'form', 'body', 'This field is required.')

        # Non-empty fields in form
        response = self.client.post(self.url, {'title': 'Title 3', 'body': 'Lorem ipsum'})
        self.assertRedirects(response, reverse('blog:post', kwargs={'pk': 1}))


class PostUpdateTest(TestCase):

    def setUp(self):
        self.test_user_1 = User.objects.create_user(
            USERNAME1, 'user1@gmail.com', PASSWORD1)
        self.test_user_2 = User.objects.create_user(
            USERNAME2, 'user2@gmail.com', PASSWORD2)
        self.test_post_1 = Post.objects.create(user=self.test_user_1, title='Title 1', body='Lorem ipsum')
        self.url = reverse('blog:update_post', kwargs={'pk': self.test_post_1.id})

    def test_update_post_by_anonymous_user(self):
        response = self.client.post(self.url, {'title': 'Title 3', 'body': 'Lorem ipsum'})
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'), self.url))

    def test_update_post_by_author(self):
        self.client.login(username=USERNAME1, password=PASSWORD1)

        # Empty fields in form
        response = self.client.post(self.url, {'title': '', 'body': ''})
        self.assertFormError(response, 'form', 'title', 'This field is required.')
        self.assertFormError(response, 'form', 'body', 'This field is required.')

        # Non-empty fields in form
        response = self.client.post(self.url, {'title': 'Title 3', 'body': 'Lorem ipsum'})
        self.assertRedirects(response, reverse('blog:post', kwargs={'pk': self.test_post_1.id}))


class PostDeleteTest(TestCase):

    def setUp(self):
        self.test_user_1 = User.objects.create_user(
            USERNAME1, 'user1@gmail.com', PASSWORD1)
        self.test_user_2 = User.objects.create_user(
            USERNAME2, 'user2@gmail.com', PASSWORD2)
        self.test_post_1 = Post.objects.create(user=self.test_user_1, title='Title 1', body='Lorem ipsum')
        self.url = reverse('blog:delete_post', kwargs={'pk': self.test_post_1.id})

    def test_delete_post_by_anonymous_user(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'), self.url))

    def test_delete_post_by_author(self):
        self.client.login(username=USERNAME1, password=PASSWORD1)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('blog:home'))