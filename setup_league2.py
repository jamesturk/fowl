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

james = User.objects.create_superuser('james', 'james.p.turk@gmail.com',
                                      'james')
erin = User.objects.create_superuser('erin', 'erin.braswell@gmail.com',
                                     'erin')
kevin = User.objects.create_superuser('kevin', 'kevin.wohlgenant@gmail.com',
                                      'kevin')
patrick = User.objects.create_superuser('patrick', 'patricksimmons85@gmail.com',
                                      'patrick')
league = League.objects.create(name='Fire Pro Wrestling')
gm_punk = Team.objects.create(name='GM Punk', login=james, league=league,
                              color='#1540a4')
awesome = Team.objects.create(name="I'm AWEsome!", login=kevin, league=league,
                              color='#f5a506')
cobra = Team.objects.create(name='COBRA!', login=erin, league=league,
                            color='#05c405')
ruleyou = Team.objects.create(name='I Will Rule You', login=patrick,
                            league=league, color='#a600c9')

for star in ('cmpunk', 'johncena', 'jackswagger',
             'albertodelrio', 'ryback', 'damien-sandow',
             'darrenyoung', 'aj', 'bethphoenix',
             'ricflair', 'hbk'):
    print star
    awesome.add_star(star)

for star in ('santinomarella', 'rtruth', 'brodusclay',
             'dolphziggler', 'thegreatkhali', 'titusoneil',
             'reymysterio', 'kaitlyn', 'natalya',
             'paulheyman', 'mickfoley'):
    print star
    cobra.add_star(star)

for star in ('bigshow', 'davidotunga', 'themiz',
             'danielbryan', 'christian', 'williamregal',
             'zackryder', 'layla', 'eve',
             'roddypiper', 'edge'):
    print star
    ruleyou.add_star(star)

for star in ('kofikingston', 'kane', 'masonryan',
             'sheamus', 'sin-cara', 'codyrhodes',
             'antoniocesaro', 'kharma', 'kellykelly',
             'brock-lesnar', 'jimross'):
    print star
    gm_punk.add_star(star)


# 6/1 Smackdown
event = Event.objects.create(name='Smackdown', date='2012-06-01')
event.add_match('sin-cara', 'heathslater', winner='sin-cara',
                outcome='normal')
event.add_match('damien-sandow', 'ezekieljackson',
                winner='damien-sandow', outcome='normal')
event.add_match('ryback',
                ['nobody1', 'nobody2'], winner='ryback',
                outcome='normal')
event.add_match('dolphziggler', 'sheamus',
                winner='sheamus', outcome='normal')
event.add_match(['titusoneil', 'darrenyoung'],
		['santinomarella', 'zackryder'],
		winner='santinomarella', outcome='normal')
event.add_match('tysonkidd', 'codyrhodes',
		winner='codyrhodes', outcome='normal')
event.add_match('cmpunk', 'kane',
		outcome='no contest', title_at_stake='wwe')
league.score_event(event)

# 6/4 raw
event = Event.objects.create(name='RAW', date='2012-06-04')
event.add_match('sheamus', 'dolphziggler', winner='sheamus', outcome='normal')
event.add_match('sin-cara', 'hunico', winner='sin-cara', outcome='normal')
event.add_match('ryback', ['nobody1', 'nobody2'], winner='ryback',
                outcome='normal',
		notes='arthur rosenberg and stan stanski, names to watch')
event.add_match('cmpunk', 'kane', outcome='normal', winner='kane')
event.add_match(['kofikingston', 'rtruth'], ['tylerreks', 'curthawkins'],
	        winner='kofikingston', outcome='normal')
event.add_match('johncena', 'tensai', winner='johncena', outcome='normal')
event.add_match('johncena', 'michaelcole', winner='johncena', outcome='normal')
league.score_event(event)
