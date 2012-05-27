from django.contrib.auth.models import User
from fowl.game.models import League, Star, Team, Event, Match
from fowl.game.tests import _give_belt

User.objects.all().delete()
League.objects.all().delete()
Team.objects.all().delete()
Event.objects.all().delete()

_give_belt('cmpunk', 'wwe')
_give_belt('sheamus', 'heavyweight')
_give_belt('kofikingston', 'tag')
_give_belt('rtruth', 'tag')
_give_belt('layla', 'diva')
_give_belt('codyrhodes', 'ic')
_give_belt('santinomarella', 'us')

james = User.objects.create_superuser('james', 'james.p.turk@gmail.com', 'james')
erin = User.objects.create_user('erin', 'erin.braswell@gmail.com', 'erin')
kevin = User.objects.create_user('kevin', 'kevin.wohlgenant@gmail.com', 'kevin')
league = League.objects.create(name='Fire Pro Wrestling')
gm_punk = Team.objects.create(name='GM Punk', login=james, league=league)
awesome = Team.objects.create(name="I'm AWEsome!", login=kevin, league=league)
cobra = Team.objects.create(name='COBRA!', login=erin, league=league)

punks = ('cmpunk', 'markhenry', 'rtruth', 'codyrhodes', 'tensai', 'antoniocesaro',
         'wadebarrett', 'aj', 'bethphoenix')
for person in punks:
    gm_punk.add_star(pk=person)

awesomes = ('chrisjericho', 'sheamus', 'danielbryan', 'ryback', 'damien-sandow',
            'kharma', 'kellykelly', 'brodusclay', 'johncena')
for person in awesomes:
    awesome.add_star(pk=person)

cobras = ('santinomarella', 'dolphziggler', 'kofikingston', 'albertodelrio',
          'randyorton', 'bigshow', 'titusoneil', 'layla', 'natalya')
for person in cobras:
    cobra.add_star(pk=person)

# RAW 5/14
event = Event.objects.create(name='RAW', date='2012-05-14')
event.add_match(['cmpunk', 'santinomarella'], ['codyrhodes', 'danielbryan'],
                winner='cmpunk', win_type='pin')
event.add_match('aliciafox', 'bethphoenix', winner='bethphoenix',
                win_type='pin')
event.add_match('bigshow', 'kane', winner='kane', win_type='pin')
event.add_match(['brodusclay', 'kofikingston', 'rtruth'],
                ['themiz', 'jackswagger', 'dolphziggler'],
                winner='brodusclay', win_type='pin')
event.add_match('chrisjericho', 'randyorton',
                winner='chrisjericho', win_type='DQ',
                note='Sheamus interfered, giving Jericho the win')
# MISSING heyman's appearance
league.score_event(event)

# Smackdown 5/18
event = Event.objects.create(name='Smackdown', date='2012-05-18')
event.add_match(['kofikingston', 'rtruth'], ['darrenyoung', 'titusoneil'],
                winner='rtruth', win_type='pin')
event.add_match('damien-sandow', 'yoshitatsu', notes='sandow refuses to fight')
event.add_match('zackryder', 'danielbryan', winner='danielbryan',
                win_type='submission')
event.add_match('cmpunk', 'kane', winner='kane', win_type='dq',
                notes='bryan hits kane with a chair, kane wins by DQ')
event.add_match('santinomarella', 'codyrhodes', winner='santinomarella',
                win_type='pin')
event.add_match('randyorton', 'sheamus', winner='sheamus', win_type='pin')
# MISSING sandow brawl points
league.score_event(event)

# Over the Limit 5/20
event = Event.objects.create(name='Over the Limit', date='2012-05-20')
event.add_match('zackryder', 'kane', winner='kane', win_type='pin')
event.add_match('alexriley', 'christian', 'curthawkins', 'darrenyoung',
                'davidotunga', 'drewmcintyre', 'ezekieljackson',
                'thegreatkhali', 'heathslater', 'jeyuso', 'jimmyuso', 'jindermahal',
                'jtg', 'michaelmcgillicutty', 'themiz', 'titusoneil',
                'tylerreks', 'tysonkidd', 'williamregal', 'yoshitatsu',
                winner='christian', win_type='pin')
event.add_match(['kofikingston', 'rtruth'], ['dolphziggler', 'jackswagger'],
                winner='kofikingston', win_type='pin', title_at_stake=True)
event.add_match('layla', 'bethphoenix', winner='layla',
                win_type='pin', title_at_stake=True)
event.add_match('sheamus', 'randyorton', 'chrisjericho', 'albertodelrio',
                winner='sheamus', win_type='pin', title_at_stake=True)
event.add_match('brodusclay', 'themiz', winner='brodusclay', win_type='pin')
event.add_match('christian', 'codyrhodes', winner='christian', win_type='pin',
                title_at_stake=True)
_give_belt('christian', 'ic')
event.add_match('cmpunk', 'danielbryan', winner='cmpunk', win_type='pin',
                title_at_stake=True)
event.add_match('ryback', 'camacho', winner='ryback', win_type='pin')
event.add_match('john-laurinaitis', 'johncena', 'bigshow',
                winner='johnlaurinaitis',
                win_type='pin', notes='Big Show interferes in a big way')
league.score_event(event)

# 5/21 RAW
event = Event.objects.create(name='RAW', date='2012-05-21')
event.add_match('davidotunga', 'johncena', winner='johncena',
                win_type='submission')
# Brawl: Tyler Reks & Curt Hawkins & Titus O'Neil & Daren Young & Sheamus
# Brawl: Santino vs. Ricardo
event.add_match('albertodelrio', 'randyorton', winner='randyorton',
                win_type='DQ', notes='Jericho codebreaks RKO, Orton wins')
event.add_match('danielbryan', 'kane', winner='danielbryan', win_type='DQ',
                notes='Kane uses chair, Bryan wins')
event.add_match('christian', 'jindermahal', winner='christian', win_type='pin')
event.add_match('bethphoenix', 'kellykelly', winner='bethphoenix',
                win_type='pin')
event.add_match(['johncena', 'sheamus'],
                ['tensai', 'jackswagger', 'dolphziggler'],
                notes='Lumberjacks rush ring, no contest')
league.score_event(event)

# COBRA! draft actions
cobra.drop_star('titusoneil')
cobra.add_star('christian')
# GM Punk draft actions
gm_punk.drop_star('markhenry')
gm_punk.add_star('sin-cara')
gm_punk.drop_star('tensai')
gm_punk.add_star('kane')

# 5/25 Smackdown
event = Event.objects.create(name='Smackdown', date='2012-05-25')
event.add_match('christian', 'hunico', winner='christian',
                win_type='pin')
event.add_match(['titusoneil', 'darrenyoung'],
                ['jimmyuso', 'jeyuso'],
                winner='titusoneil', win_type='pin')
Star.objects.create(name='Nobody One', pk='nobody1')
Star.objects.create(name='Nobody Two', pk='nobody2')
event.add_match('ryback',
                ['nobody1', 'nobody2'], winner='ryback',
                win_type='pin')
event.add_match('santinomarella', 'ricardorodriguez',
                winner='santinomarella', win_type='pin')
event.add_match('sheamus', 'jackswagger', winner='sheamus',
                win_type='pin')
event.add_match('damien-sandow', 'yoshitatsu',
                winner='damien-sandow', win_type='pin')
# daniel bryan vs kane brawl
event.add_match('randyorton', 'kane', 'albertodelrio',
                winner='albertodelrio', win_type='pin')
league.score_event(event)

