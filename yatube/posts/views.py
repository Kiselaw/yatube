from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

PAGENUM = 10


def paginator(page_number, posts):
    paginator = Paginator(posts, PAGENUM)
    page_obj = paginator.get_page(page_number)
    # Тут почему-то Flake выдает ошибку R504
    # Почитал в интернете - вроде бы это баг
    return page_obj


def index(request):
    title = 'Последние обновления на сайте'
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_number = request.GET.get('page')
    page_obj = paginator(page_number, posts)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_list(request, slug):
    title = 'Записи сообщества'
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_post.all()
    page_number = request.GET.get('page')
    page_obj = paginator(page_number, posts)
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    title = 'Профайл пользователя'
    template = 'posts/profile.html'
    client = get_object_or_404(User, username=username)
    posts = client.posts.all()
    page_number = request.GET.get('page')
    page_obj = paginator(page_number, posts)
    num = len(posts)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=client
        ).exists()
        context = {
            'title': title,
            'client': client,
            'num': num,
            'page_obj': page_obj,
            'following': following,
        }
        return render(request, template, context)
    context = {
        'title': title,
        'client': client,
        'num': num,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    title = post.text
    user = post.author
    num = user.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'title': title,
        'post': post,
        'num': num,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def create_post(request):
    template = 'posts/create_post.html'
    user = request.user
    form = PostForm(request.POST or None, files=request.FILES or None)
    context = {
        'form': form,
    }
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            return redirect('posts:profile', username=post.author.username)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    context = {
        'form': form,
        'post': post,
    }
    if request.method == 'POST':
        if user == post.author:
            if form.is_valid():
                form.save()
                return redirect('posts:post_detail', post_id)
        return redirect('posts:post_detail', post_id)
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    user = request.user
    title = user
    follow_posts = Post.objects.filter(
        author__following__user__id=request.user.id
    )
    page_number = request.GET.get('page')
    page_obj = paginator(page_number, follow_posts)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follower = request.user
    if follower == author:
        return redirect('posts:profile', username=username)
    obj, created = Follow.objects.get_or_create(user=follower, author=author)
    # Страшно ли, что одну из переменных я не использую?
    # flake не ругается, но тем не менее
    if obj:
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    unfollower = request.user
    Follow.objects.filter(user=unfollower, author=author).delete()
    return redirect('posts:profile', username=username)
