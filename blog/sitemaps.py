from django.contrib.sitemaps import Sitemap
from .models import Category, Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Post.objects.filter(published=True)


    def lastmod(self, obj):
        return obj.publish_date



  

  


