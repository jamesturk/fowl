from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'league/(?P<league_id>\d+)/$', 'fowl.game.views.league',
        name='league'),
    url(r'league/(?P<league_id>\d+)/events/$', 'fowl.game.views.events',
        name='events'),
    url(r'^league/(?P<league_id>\d+)/roster/$', 'fowl.game.views.roster',
        name='roster'),
    url(r'^edit_event/(?P<event>\d+|new)/$', 'fowl.game.views.edit_event',
        name='edit_event'),
)
