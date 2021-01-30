from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger
)
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.contrib import messages
from taggit.models import Tag
from django.db.models import Count
from param.models import IntegerParams


# function-based view of post list
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    BLOG_POSTS_PAGE_SIZE = get_object_or_404(IntegerParams, name='BLOG_POSTS_PAGE_SIZE').value

    paginator = Paginator(object_list, per_page=BLOG_POSTS_PAGE_SIZE)
    page_number = request.GET.get('page_number')
    try:
        posts = paginator.get_page(page_number)
    except  PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.get_page(1)
    except EmptyPage:
        # If page is out of range deliver the last page of results
        posts = paginator.get_page(paginator.num_pages)

    return render(request, 'blog/post/list.html', 
                        {
                            'posts': posts, 
                            'page_number': page_number, 
                            'range': range(1,paginator.num_pages+1),
                            'tag': tag
                        })

# # class-based views of post list
# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 2
#     template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                    status='published',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day)
    
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    
    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but do not save to the database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            comment_form = CommentForm()
            messages.success(request, 'You commented successfully')
    else:
        comment_form = CommentForm()

    # List of similar posts
    similar_posts = post.get_similar_posts()

    return render(request, 'blog/post/detail.html', 
                    {
                        'post': post, 
                        'comments': comments, 
                        'new_comment': new_comment, 
                        'comment_form': comment_form,
                        'similar_posts': similar_posts
                    })


def post_share(request, post_id):
    # Retrieve by post id by giving **kwargs
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Forms field passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            # ..send email
            subject = f'{cd["name"]} recommends you to read {post.title}'
            message = f'Read {post.title} at {post_url} \n {cd["name"]}\s comments: \n {cd["comments"]}'
            messages.success(request, 'Successfully sent')
            sent = send_mail(subject, message, 'admin@myblog.com', [cd["to"]])
            if sent:
                form = EmailPostForm()
    else:
        form = EmailPostForm()
    
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

