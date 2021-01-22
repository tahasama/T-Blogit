from django.shortcuts import redirect, render, get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post, Comment, Category
from taggit.models import Tag
from .forms import CommentForm, PostForm, UserCreationEmailForm, ContactForm, SearchForm, UserEditForm
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Count
from django.utils.text import slugify
from django.views.generic.edit import CreateView

from django.core.mail import send_mail, EmailMessage

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, permission_required  

from django.contrib import messages




def create_post(request):

    posts = Post.objects.all()
    users_in_group = Group.objects.get(name="writer").user_set.all()
       
    if request.method == 'POST' and  request.user in users_in_group : 
        # A comment was posted
        form = PostForm(data=request.POST)
        if form.is_valid():
            # Create Comment object but don't save to database yet
            posts = form.save(commit=False)
            # Assign the current post to the comment
            
            posts.author = request.user
            posts.slug = slugify(posts.title)
            #posts.tags = request.POST['tags']
            # Save the comment to the database
            
            posts.save()
            form.save_m2m()   # alloow to save the tags added by user
            messages.success(request, 'Post has been created, and will be published after revsion')
            return redirect('blog:post_list_author')
    else:
        form = PostForm()
    return render(request,'blog/create.html',{'posts': posts,'form':form})

def update_post(request,post_slug):
    post = Post.objects.get(slug=post_slug)
    users_in_group = Group.objects.get(name="writer").user_set.all()
    if request.method == 'POST' and  request.user in users_in_group and post.author == request.user:
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            
            
            post.published = False
            post.save()
            messages.success(request, 'Post has been updated, and will be published after revsion')
            
        return redirect('blog:post_list_author')    
    else:
        form = PostForm(instance=post)
    return render(request,'blog/create.html',{'post': post,'form':form})

def delete_post(request,post_slug):
    users_in_group = Group.objects.get(name="writer").user_set.all()
    if request.method == 'POST'and  request.user in users_in_group:
        post = Post.objects.get(slug=post_slug)
        post.delete()
        messages.success(request, 'Post has been updated, and will be published after revsion')
    return redirect('blog:post_list_author')


def post_list(request,tag_slug=None,category_slug=None):
    if 'writer' in request.GET:
        posts = Post.objects.filter(author=request.user)
  
    else:       
        posts = Post.objects.filter(published=True).order_by('-publish_date')
    category_page = None
    if category_slug:
        category_page = get_object_or_404(Category, slug=category_slug)
        posts = Post.objects.filter(category=category_page, published=True)
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    
    
    paginator = Paginator(posts, 3) #  3 posts in each page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
        
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    return render(request,'blog/list.html',{'posts': posts, 'tag':tag, 'category': category_page})



def post_detail(request, year, month, day, post_slug):
    posts = Post.objects.get(slug=post_slug)
    count = Comment.objects.filter(post=posts).count()
    print(count)
    users_in_group = Group.objects.get(name="writer").user_set.all()
    if request.user in users_in_group and posts.author == request.user:
        post = get_object_or_404(Post, slug=post_slug,publish_date__year=year,
                                                            publish_date__month=month,
                                                            publish_date__day=day)
    else:
         post = get_object_or_404(Post, slug=post_slug,published=True,publish_date__year=year,
                                                            publish_date__month=month,
                                                            publish_date__day=day)
    # List of similar posts
    post_tags_ids = post.tags.values_list('id',flat=True)
    #print(post_tags_ids)
    similar_tags = Post.objects.filter(published=True, tags__in=post_tags_ids).exclude(id=post.id)
    #print(similar_tags)
    similar_posts = similar_tags.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish_date')
    #print(similar_posts[0])

    comments = Comment.objects.filter(post=post)

    if request.method == 'POST' and request.user.is_authenticated :
        # A comment was posted
        form = CommentForm(data=request.POST)
        if form.is_valid():
            # Create Comment object but don't save to database yet
            comments = form.save(commit=False)
            # Assign the current post to the comment
            comments.post = post
            comments.commenter = request.user
            # Save the comment to the database
            comments.save()
            print(comments.id)
            return redirect('blog:post_detail',post.publish_date.year,post.publish_date.month,post.publish_date.day, post.slug)
    else:
        form = CommentForm()
    return render(request,'blog/detail.html',{'post': post,'form':form,'comments':comments,'similar_posts':similar_posts,'count':count})


def update_comment(request,year, month, day, post_slug, comment_id):
    post = get_object_or_404(Post, slug=post_slug)
    comment = get_object_or_404(Comment,post=post, id=comment_id)
    #print(reviews)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
        return redirect('blog:post_detail',post.publish_date.year,post.publish_date.month,post.publish_date.day, post.slug)    
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/detail.html', {'form':form,'comment':comment,'post':post})

def delete_comment(request, year, month, day, post_slug, comment_id):
    post = get_object_or_404(Post, slug=post_slug)
    comment = get_object_or_404(Comment,post=post, id=comment_id)
    
    comment.delete()
    return redirect('blog:post_detail',post.publish_date.year,post.publish_date.month,post.publish_date.day, post.slug)



def register(request):
    if request.method == 'POST':
        form = UserCreationEmailForm(data=request.POST)
        if form.is_valid():
            form.save() 
            cd = form.cleaned_data
            # query = data
            # print(query)
            register_user = User.objects.get(username=cd['username'])
            if 'writer' in request.GET:                                
                customer_group = Group.objects.get(name='writer')
                customer_group.user_set.add(register_user)
            else:
                customer_group = Group.objects.get(name='reader')
                customer_group.user_set.add(register_user)
            user = authenticate(username=cd['username'],password=cd['password1'])
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('blog:home')
    else:
        form = UserCreationEmailForm()
    return render(request,'bloggers/registration.html',{'form': form})

# def w_register(request):
#     if request.method == 'POST':
#         form = UserCreationEmailForm(data=request.POST)
#         if form.is_valid():
#             form.save() 
#             cd = form.cleaned_data
#             register_user = User.objects.get(username=cd['username'])
#             customer_group = Group.objects.get(name='writer')
#             customer_group.user_set.add(register_user)
#             user = authenticate(username=cd['username'],password=cd['password1'])
#             login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#             return redirect('blog:post_list')
#     else:
#         form = UserCreationEmailForm()
#     return render(request,'bloggers/registration.html',{'form': form})

@login_required
def edit(request):
    if request.method == 'POST':
        form = UserEditForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
        return redirect('home')
    else:
        form = UserEditForm(instance=request.user)
    return render(request,'bloggers/edit.html',{'form': form})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            from_email = form.cleaned_data.get('from_email')
            message = form.cleaned_data.get('message')
            name = form.cleaned_data.get('name')

            message_format = f"client :{name} \n\n with e-mail: {from_email} has sent you a new message:\n\n{message}"
            msg = EmailMessage(
                subject,
                message_format,
                to=['serertei@gmail.com'],
                from_email=from_email
            )
            msg.send()
            return render(request, 'blog/contact_success.html')
    else:
        form = ContactForm()
    return render(request, 'blog/contact.html', {'form': form})

def search(request):   
    query = None
    results = []
    if request.method == "GET":
        query = request.GET.get("query")
        search_vector = SearchVector('title', 'body','tags')
        search_query = SearchQuery(query)
        results = Post.objects.annotate(search=search_vector,
                    rank=SearchRank(search_vector, search_query)).filter(
                                        search=search_query).order_by('-rank')
        return render(request,'blog/search.html',{'query': query,'results': results})
        