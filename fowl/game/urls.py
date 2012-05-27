from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^events/$', 'fowl.game.views.events'),
    url(r'^edit_event/$', 'fowl.game.views.edit_event'),
    url(r'^stables/$', 'fowl.game.views.stables'),
)
