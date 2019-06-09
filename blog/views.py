from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render
from blog.models import Post,Comment
from django.contrib.auth.hashers import make_password
from django.urls import reverse_lazy,reverse
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# Create your views here.

NUM_OF_POSTS = 5



def home(request, username=None):
    first_name = ''
    last_name = ''
    if username:
        user = User.objects.get(username=username)
        first_name = user.first_name
        last_name = user.last_name
        post_list = Post.objects.filter(user=user)
    else:
        post_list = Post.objects.all()

    post_list = post_list.order_by('-pub_date')

    paginator = Paginator(post_list, NUM_OF_POSTS)  # Show NUM_OF_PAGES posts per page
    page = request.GET.get('page')

    posts = paginator.get_page(page)

    return render(request, 'blog/home.html', {'posts': posts,
                                              'first_name': first_name,
                                              'last_name': last_name})
    
class RegisterView(CreateView):
    model = User
    fields = ['username', 'password', 'first_name', 'last_name', 'email']
    template_name = 'blog/registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Hash password before sending it to super
        form.instance.password = make_password(form.instance.password)
        return super().form_valid(form)
class PostView(generic.DetailView):
    model = Post
    template_name = 'blog/post.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the username
        comments = Comment.objects.filter(post=self.kwargs['pk'])
        context['comments'] = comments
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'body']
    template_name = 'blog/create_post.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'body']
    template_name = 'blog/create_post.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        return Post.objects.get(id=self.kwargs['pk']).user == self.request.user


class PostDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:home')
    login_url = reverse_lazy('login')

    def test_func(self):
        return Post.objects.get(id=self.kwargs['pk']).user == self.request.user


class CommentCreate(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['body']
    template_name = 'blog/create_comment.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post = Post.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post', kwargs={'pk': self.kwargs['pk']})
