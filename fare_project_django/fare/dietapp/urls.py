__author__ = 'fady'

from django.conf.urls import patterns, url
from dietapp import views

urlpatterns = patterns('',

    url(r'^diets/', views.diets, name='diets'),
	url(r'^diet/(?P<diet_id>\d+)/$', views.diet, name='diet'),

    url(r'^recipes/', views.recipes, name='recipes'),
	url(r'^recipe/(?P<recipe_id>\d+)/$', views.recipe, name='recipe')
)