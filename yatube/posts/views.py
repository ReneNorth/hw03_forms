from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import PostForm
from yatube.settings import DEF_NUM_POSTS
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model


User = get_user_model()
group_list = Group.objects.all().values_list('title', flat=True).distinct()


def paginator(list_of_posts, request, posts_per_page):
    paginator = Paginator(list_of_posts, posts_per_page)
    page_number = request.GET.get('page')
    pages = paginator.get_page(page_number)
    return pages


def index(request):
    post_list = Post.objects.all()
    page_obj = paginator(post_list, request, DEF_NUM_POSTS)
    context = {
        'page_obj': page_obj,
        'group_list': group_list
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(post_list, request, DEF_NUM_POSTS)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    post_list = Post.objects.filter(
        author__username=username)
    page_obj = paginator(post_list, request, DEF_NUM_POSTS)
    author = get_object_or_404(User, username=username)
    num_of_posts = Post.objects.filter(author__username=username).count()

    context = {
        'page_obj': page_obj,
        'author': author,
        'num_of_posts': num_of_posts,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
        return render(request, 'posts/post_create.html', {'form': form})
    return render(request, 'posts/post_create.html',
                  {'form': form, 'group_list': group_list})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': is_edit,
        'group_list': group_list
    }
    return render(request, 'posts/post_create.html', context)
