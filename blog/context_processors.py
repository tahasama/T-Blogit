from .models import Category
  

def category_choice(request):
    links = Category.objects.all()
    return dict(links=links)
