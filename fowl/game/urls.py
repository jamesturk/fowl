from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^events/$', 'fowl.game.views.events'),
    url(r'^stables/$', 'fowl.game.views.stables'),
)
