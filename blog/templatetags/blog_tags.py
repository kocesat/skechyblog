from django import template
from ..models import Post
from django.db.models import Count
import markdown
from django.utils.safestring import mark_safe


# create an instance of Library class
register = template.Library()

# use simple_tag decorator to register your function as template tag
# simple_tag: Process the data and returns a string.
# inclusion_tag: Processes the data and returns a rendered template
@register.simple_tag
def total_posts():
    return Post.published.count()

# custom template tag that shows latest posts
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


# custom template tag that gives most commented posts
@register.simple_tag
def get_most_commented_posts(count=5):
    # for each context(post) get the count of comments by annotate method.
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

