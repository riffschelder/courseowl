from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       url(r'^subjects', views.json_subjects, name='api_subjects'),
                       url(r'^courses', views.json_courses, name='api_courses')
                       )
