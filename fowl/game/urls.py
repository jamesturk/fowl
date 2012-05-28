from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'events/(?P<league_id>\d+)/$', 'fowl.game.views.events',
        name='events'),
    url(r'league/(?P<league_id>\d+)/$', 'fowl.game.views.league',
        name='league'),
    url(r'^edit_event/$', 'fowl.game.views.edit_event', name='edit_event'),
    url(r'^roster/$', 'fowl.game.views.roster', name='roster'),
)
