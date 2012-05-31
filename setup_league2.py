from django.contrib.auth.models import User
from fowl.game.models import League, Star, Team, Event, Match
from fowl.game.tests import _give_belt

User.objects.all().delete()
League.objects.all().delete()
Team.objects.all().delete()
Event.objects.all().delete()

Star.objects.get(pk='cmpunk').win_title('wwe', '2011-11-20')
Star.objects.get(pk='santinomarella').win_title('us', '2012-03-05')
Star.objects.get(pk='sheamus').win_title('world', '2012-04-01')
Star.objects.get(pk='layla').win_title('divas', '2012-04-29')
Star.objects.get(pk='kofikingston').win_title('tag', '2012-04-30',
                                  tag_partner=Star.objects.get(pk='rtruth'))
Star.objects.get(pk='christian').win_title('ic', '2011-05-20')

james = User.objects.create_superuser('james', 'james.p.turk@gmail.com', 'james')
erin = User.objects.create_user('erin', 'erin.braswell@gmail.com', 'erin')
kevin = User.objects.create_user('kevin', 'kevin.wohlgenant@gmail.com', 'kevin')
league = League.objects.create(name='Fire Pro Wrestling')
gm_punk = Team.objects.create(name='GM Punk', login=james, league=league,
                              color='#1540a4')
awesome = Team.objects.create(name="I'm AWEsome!", login=kevin, league=league,
                              color='#f5a506')
cobra = Team.objects.create(name='COBRA!', login=erin, league=league,
                            color='#05c405')
