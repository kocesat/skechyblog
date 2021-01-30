from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from django.db.models import Count


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset()\
                                            .filter(status='published')

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                            choices=STATUS_CHOICES,
                            default='draft')
    tags = TaggableManager()

    class Meta:
        ordering = ('-publish', ) # append ',' to tell Python it's a tuple.

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                        args=[self.publish.year,
                                self.publish.month,
                                self.publish.day, self.slug])


    objects = models.Manager()
    published = PublishedManager()

    def get_similar_posts(self):
        '''
        Given a post object, it returns queryset of 4 posts that have same tags
        '''
        post_tags_ids = self.tags.values_list('id', flat=True) # flat=True makes returning object a list of one values not [( x,y )]
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=self.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
        return similar_posts




class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',) # ascending order (older to newer)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'







