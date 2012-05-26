from django.contrib.auth.models import User
from fowl.game.models import League, Star, Team, Event, Match

james = User.objects.create_superuser('james', 'james.p.turk@gmail.com', 'james')
erin = User.objects.create_user('erin', 'erin.braswell@gmail.com', 'erin')
kevin = User.objects.create_user('kevin', 'kevin.wohlgenant@gmail.com', 'kevin')
league = League.objects.create(name='Fire Pro Wrestling')
gm_punk = Team.objects.create(name='GM Punk', login=james, league=league)
awesome = Team.objects.create(name="I'm AWEsome!", login=kevin, league=league)
cobra = Team.objects.create(name='COBRA!', login=erin, league=league)


wm = Event.objects.create(name='Wrestlemania XXX', date='2013-01-01')
m1 = Match.objects.create(event=wm)
m1.add_team('dolphziggler')
m1.add_team('randysavage')