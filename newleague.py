from django.contrib.auth.models import User
from fowl.game.models import League, Star, Team, Event, Match
from fowl.game.tests import _give_belt

james = User.objects.get(username='james')
erin = User.objects.get(username='erin')
kevin = User.objects.get(username='kevin')
patrick = User.objects.get(username='patrick')

league = League.objects.create(name='Fire Pro Wrestling: Fall Invitational')
gm_punk = Team.objects.create(name='Brocktagon', login=james, league=league,
                              color='#1540a4')
awesome = Team.objects.create(name="I'm AWEsome! [2]", login=kevin, league=league,
                              color='#f5a506')
cobra = Team.objects.create(name='COBRA! [2]', login=erin, league=league,
                            color='#05c405')
ruleyou = Team.objects.create(name='I Will Rule You [2]', login=patrick,
                            league=league, color='#a600c9')

for star in ('christian', 'danielbryan', 'darrenyoung', 'evanbourne',
             'randyorton', 'ryback', 'sheamus', 'bethphoenix', 'tamina-snuka',
             'edge', 'jbl'):
    print star
    awesome.add_star(star)

for star in ('bigshow', 'damien-sandow', 'dolphziggler', 'kofikingston',
             'sin-cara', 'zackryder', 'reymysterio', 'layla', 'natalya',
             'ricflair', 'hacksawjimduggan'):
    print star
    cobra.add_star(star)

for star in ('albertodelrio', 'antoniocesaro', 'johncena', 'kane', 'rtruth',
             'santinomarella', 'davidotunga', 'kellykelly', 'eve',
             'ronsimmons', 'sgtslaughter'):
    print star
    ruleyou.add_star(star)

for star in ('brodusclay', 'cmpunk', 'codyrhodes', 'jindermahal', 'themiz',
             'titusoneil', 'wadebarrett', 'aj', 'kaitlyn', 'paulbearer',
             'themilliondollarman'):
    print star
    gm_punk.add_star(star)
