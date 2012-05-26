from django.contrib.auth.models import User
from fowl.game.models import League, Star, Team, Event, Match

User.objects.all().delete()
League.objects.all().delete()
Team.objects.all().delete()

james = User.objects.create_superuser('james', 'james.p.turk@gmail.com', 'james')
erin = User.objects.create_user('erin', 'erin.braswell@gmail.com', 'erin')
kevin = User.objects.create_user('kevin', 'kevin.wohlgenant@gmail.com', 'kevin')
league = League.objects.create(name='Fire Pro Wrestling')
gm_punk = Team.objects.create(name='GM Punk', login=james, league=league)
awesome = Team.objects.create(name="I'm AWEsome!", login=kevin, league=league)
cobra = Team.objects.create(name='COBRA!', login=erin, league=league)

punks = ('cmpunk', 'kane', 'rtruth', 'codyrhodes', 'sin-cara', 'antoniocesaro',
         'wadebarrett', 'aj', 'bethphoenix')
for person in punks:
    print person
    gm_punk.add_star(pk=person)

awesomes = ('chrisjericho', 'sheamus', 'danielbryan', 'ryback', 'damien-sandow',
            'kharma', 'kellykelly', 'brodusclay', 'johncena')
for person in awesomes:
    print person
    awesome.add_star(pk=person)

cobras = ('santinomarella', 'dolphziggler', 'kofikingston', 'albertodelrio',
          'randyorton', 'bigshow', 'christian', 'layla', 'natalya')
for person in cobras:
    print person
    cobra.add_star(pk=person)