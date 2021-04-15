from .models import Post, Like
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404, redirect
from .forms import SignUpForm, LoginForm, PostForm, CommentForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.generic import (
    ListView
)


# Create your views here.
def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})


def about(request):
    return render(request, 'about,html')


def search(request):
    template = 'home.html'
    query = request.GET.get('q')
    result = Post.objects.filter(
        Q(title__icontains=query) | Q(author__username__icontains=query))
    context = {'posts': result}
    return render(request, template, context)


def post_detail(request, slug):
    template_name = 'post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True)
    new_comment = None

    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form})


def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            posts = Post.objects.all()
        else:
            posts = Post.objects.filter(author=request.user)
        posts = posts
        user = request.user
        full_name = user.get_full_name()
        gps = user.groups.all()
        return render(request, 'dashboard.html', {'posts': posts, 'fname': full_name, 'groups': gps})
    else:
        return HttpResponseRedirect('/login/')


def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulations!! You have become an Author')
            user = form.save()
            group = Group.objects.get(name='Author')
            user.groups.add(group)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = LoginForm(request=request, data=request.POST)
            if form.is_valid():
                uname = form.cleaned_data['username']
                upass = form.cleaned_data['password']
                user = authenticate(username=uname, password=upass)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Logged in Successfully !!')
                    return HttpResponseRedirect('/dashboard/')
                else:
                    return redirect('/login/')
        else:
            form = LoginForm()
        return render(request, 'login.html', {'form': form})
    else:
        return HttpResponseRedirect('/dashboard/')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def add_post(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST or None, request.FILES or None)
            if form.is_valid():
                title = form.cleaned_data['title']
                desc = form.cleaned_data['desc']
                image = form.cleaned_data['image']
                author = request.user
                pst = Post(title=title, desc=desc, author=author, image=image)
                pst.save()
                messages.success(request, 'Congratulations!! YourPost added successfully')
                form = PostForm()
        else:
            form = PostForm()
        return render(request, 'addpost.html', {'form': form})
    else:
        return HttpResponseRedirect('/login/')


def update_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            pi = Post.objects.get(pk=id)
            form = PostForm(request.POST, instance=pi)
            if form.is_valid():
                form.save()
                messages.success(request, 'Congratulations!! Post updated successfully')

        else:
            pi = Post.objects.get(pk=id)
            form = PostForm(instance=pi)
        return render(request, 'updatepost.html', {'form': form})
    else:
        return HttpResponseRedirect('/login/')


def delete_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            pi = Post.objects.get(pk=id)
            pi.delete()
            return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponseRedirect('/login/')


def like_unlike_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        if user in post_obj.likes.all():
            post_obj.likes.remove(user)
        else:
            post_obj.likes.add(user)
        like, created = Like.objects.get_or_create(user=user, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        else:
            like.value = 'Like'
            post_obj.save()
            like.save()

        data = {
            'value': like.value,
            'likes': post_obj.likes.all().count()
        }
        return JsonResponse(data, safe=False)

    return redirect('like_post')

