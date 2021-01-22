from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    # post views
    path('', views.post_list, name='home'),
    #path('all/', views.post_list, name='post_list'),
    path('writers-space/', views.post_list, name='post_list_author'),
    path('category/<slug:category_slug>/', views.post_list, name='post_list_by_category'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post_slug>/', views.post_detail,name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('<slug:post_slug>/update/', views.update_post, name='update_post'),
    path('<slug:post_slug>/delete/', views.delete_post, name='delete_post'),
    path('<int:year>/<int:month>/<int:day>/<slug:post_slug>/<int:comment_id>', views.post_detail,name='comment'), # added this to be able to use comment get_asolute_url
    path('<int:year>/<int:month>/<int:day>/<slug:post_slug>/<int:comment_id>/update_comment', views.update_comment,name='update_comment'),
    path('<int:year>/<int:month>/<int:day>/<slug:post_slug>/<int:comment_id>/delete_comment', views.delete_comment,name='delete_comment'),
    path('search/', views.search, name='search'),
    path('contact/', views.contact, name='contact'),
    path('edit/', views.edit, name='edit'),


]