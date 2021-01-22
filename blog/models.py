from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from taggit.managers import TaggableManager

from ckeditor_uploader.fields import RichTextUploadingField



class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category', blank=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('blog:post_list_by_category', args=[self.slug])

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,unique_for_date='publish_date')
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blog_posts')
    introduction = models.TextField(blank=True, null=True )
    body = RichTextUploadingField(blank=True, null=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='blog_category')
    publish_date = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    tags = TaggableManager()
    
    class Meta:
        ordering = ('-publish_date',)
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail',args=[self.publish_date.year,self.publish_date.month,self.publish_date.day, self.slug])

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    commenter = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blog_comments')
    content = RichTextUploadingField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)
    def __str__(self):
        return f'Comment by {self.commenter} on {self.post}'

    def get_absolute_url(self):
        return reverse('blog:comment',args=[self.post.publish_date.year,self.post.publish_date.month,self.post.publish_date.day, self.post.slug, self.id])