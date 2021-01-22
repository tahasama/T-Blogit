from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from .models import Post


class PostFeed(Feed):
    title = 'posts'
    link = reverse_lazy('blog:home')
    description = 'New posts on the platform.'

    def items(self):
        return Post.objects.filter(published=True)[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return f" from {item.category} that say {truncatewords(item.introduction, 30)}"


    