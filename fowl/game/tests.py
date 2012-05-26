from django.test import TestCase
from django.core.management import call_command
from .models import Match, Event

class MatchTest(TestCase):
    def setUp(self):
        call_command('loadstars')
        self.wm29 = Event.objects.create(name='Wrestlemania 29', date='2012-04-01')

    def test_display(self):
        match = Match.objects.create(event=self.wm29)
        match.add_team('tripleh')
        match.add_team('undertaker')
        self.assertEqual(unicode(match), 'Triple H vs. Undertaker')
        match.record_win('undertaker', 'pin')
        self.assertEqual(unicode(match), 'Triple H vs. Undertaker (v)')

        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        self.assertEqual(unicode(match), 'CM Punk (c) vs. Rey Mysterio')
        match.record_win('cmpunk', 'pin')
        self.assertEqual(unicode(match), 'CM Punk (c) (v) vs. Rey Mysterio')


    def test_scoring(self):
        # one on one : 2 points
        match = Match.objects.create(event=self.wm29)
        match.add_team('tripleh')
        match.add_team('undertaker')
        match.record_win('undertaker', 'pin')
        self.assertEqual(match.points(), {'undertaker': 2, 'tripleh': 0})

        # fatal 4 way: 6 points
        match = Match.objects.create(event=self.wm29)
        match.add_team('randyorton')
        match.add_team('albertodelrio')
        match.add_team('sheamus')
        match.add_team('chrisjericho')
        match.record_win('sheamus', 'pin')
        self.assertEqual(match.points(), {'sheamus': 6, 'randyorton': 0,
                                          'albertodelrio': 0, 'chrisjericho': 0}
                                          )

        # win stacked match: 1 point for team (bonuses can apply)
        match = Match.objects.create(event=self.wm29)
        match.add_team('santinomarella')
        match.add_team('markhenry', 'kane')
        match.record_win('markhenry', 'pin')
        self.assertEqual(match.points(), {'markhenry': 2, 'kane': 1,
                                          'santinomarella': 0})

        # DQ : 1 point
        match = Match.objects.create(event=self.wm29)
        match.add_team('kane')
        match.add_team('undertaker')
        match.record_win('undertaker', 'DQ')
        self.assertEqual(match.points(), {'undertaker': 1, 'kane': 0})

        # submission: +1
        match = Match.objects.create(event=self.wm29)
        match.add_team('danielbryan')
        match.add_team('cmpunk')
        match.record_win('danielbryan', 'submission')
        self.assertEqual(match.points(), {'danielbryan': 3, 'cmpunk': 0})

        # complicated one, outnumbered + submission
        match = Match.objects.create(event=self.wm29)
        match.add_team('danielbryan', 'chrisjericho')
        match.add_team('cmpunk')
        match.record_win('cmpunk', 'submission')
        self.assertEqual(match.points(), {'cmpunk': 5, 'chrisjericho': 0,
                                          'danielbryan': 0})

        # tag team: 2 points, +1 for the person who made pin
        match = Match.objects.create(event=self.wm29)
        match.add_team('kofikingston', 'rtruth')
        match.add_team('jackswagger', 'dolphziggler')
        match.record_win('dolphziggler', 'pin')
        self.assertEqual(match.points(), {'jackswagger': 2,
                                          'dolphziggler': 3,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # tag team submission: stacks on ziggler
        match = Match.objects.create(event=self.wm29)
        match.add_team('kofikingston', 'rtruth')
        match.add_team('jackswagger', 'dolphziggler')
        match.record_win('dolphziggler', 'submission')
        self.assertEqual(match.points(), {'jackswagger': 2,
                                          'dolphziggler': 4,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # tag team DQ: 1 point each member
        match = Match.objects.create(event=self.wm29)
        match.add_team('kofikingston', 'rtruth')
        match.add_team('jackswagger', 'dolphziggler')
        match.record_win('dolphziggler', 'DQ')
        self.assertEqual(match.points(), {'jackswagger': 1,
                                          'dolphziggler': 1,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # rumble: participants / 2
        match = Match.objects.create(event=self.wm29)
        match.add_team('kofikingston')
        match.add_team('rtruth')
        match.add_team('themiz')
        match.add_team('dolphziggler')
        match.add_team('johncena')
        match.add_team('jackswagger')
        match.add_team('kharma')
        match.add_team('kane')
        match.add_team('albertodelrio')
        match.add_team('christian')
        match.record_win('christian', 'pin')
        self.assertEqual(match.points(), {'christian': 5,
                                          'kofikingston': 0,
                                          'rtruth': 0,
                                          'themiz': 0,
                                          'dolphziggler': 0,
                                          'johncena': 0,
                                          'jackswagger': 0,
                                          'kharma': 0,
                                          'kane': 0,
                                          'albertodelrio': 0
                         })

    def test_champ_scoring(self):
        # champ doesn't get a bonus just for winning
        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        match.record_win('cmpunk', 'pin')
        self.assertEqual(match.points(), {'cmpunk': 2, 'reymysterio': 0})

        # defending wwe belt is worth +5
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        match.record_win('cmpunk', 'pin')
        self.assertEqual(match.points(), {'cmpunk': 7, 'reymysterio': 0})

        # winning wwe belt
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        match.record_win('reymysterio', 'pin')
        self.assertEqual(match.points(), {'reymysterio': 22, 'cmpunk': 0})

        # defending other belt is worth +3
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('christian', title='ic')
        match.add_team('codyrhodes')
        match.record_win('christian', 'pin')
        self.assertEqual(match.points(), {'christian': 5, 'codyrhodes': 0})

        # winning other belt is worth +3
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('christian', title='ic')
        match.add_team('codyrhodes')
        match.record_win('codyrhodes', 'pin')
        self.assertEqual(match.points(), {'codyrhodes': 12, 'christian': 0})

        # title non-defense (DQ/countout)
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('christian', title='ic')
        match.add_team('codyrhodes')
        match.record_win('codyrhodes', 'DQ')
        self.assertEqual(match.points(), {'codyrhodes': 1, 'christian': 1})

        # +2 bonus for beating a champ in a non-title match
        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        match.record_win('reymysterio', 'pin')
        self.assertEqual(match.points(), {'reymysterio': 4, 'cmpunk': 0})

        # no bonus in a tag match
        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', 'christian', title='wwe')
        match.add_team('reymysterio', 'codyrhodes')
        match.record_win('reymysterio', 'pin')
        self.assertEqual(match.points(), {'codyrhodes': 2, 'reymysterio': 3,
                                          'cmpunk': 0, 'christian': 0})

        # ...unless it is the tag title
        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', 'christian', title='tag')
        match.add_team('reymysterio', 'codyrhodes')
        match.record_win('reymysterio', 'pin')
        self.assertEqual(match.points(), {'codyrhodes': 4, 'reymysterio': 5,
                                          'cmpunk': 0, 'christian': 0})


class EventTest(TestCase):
    def setUp(self):
        call_command('loadstars')

    def test_points(self):
        smackdown = Event.objects.create(name='smackdown', date='2012-01-01')
        match = Match.objects.create(event=smackdown)
        match.add_team('reymysterio')
        match.add_team('sin-cara')
        match.record_win('sin-cara', 'pin')
        match = Match.objects.create(event=smackdown)
        match.add_team('santinomarella', 'mickfoley')
        match.add_team('markhenry')
        match.record_win('mickfoley', 'pin')
        match = Match.objects.create(event=smackdown, title_at_stake=True)
        match.add_team('codyrhodes', title='ic')
        match.add_team('sin-cara')
        match.record_win('sin-cara', 'pin')
        self.assertEqual(smackdown.points(), {'reymysterio': 0,
                                              'sin-cara': 14,
                                              'santinomarella': 1,
                                              'mickfoley': 2,
                                              'markhenry': 0,
                                              'codyrhodes': 0
                                              })

        # exact same matches on a PPV, +1 to everyone
        ppv = Event.objects.create(name='In Your House', date='2012-01-01')
        match = Match.objects.create(event=ppv)
        match.add_team('reymysterio')
        match.add_team('sin-cara')
        match.record_win('sin-cara', 'pin')
        match = Match.objects.create(event=ppv)
        match.add_team('santinomarella', 'mickfoley')
        match.add_team('markhenry')
        match.record_win('mickfoley', 'pin')
        match = Match.objects.create(event=ppv, title_at_stake=True)
        match.add_team('codyrhodes', title='ic')
        match.add_team('sin-cara')
        match.record_win('sin-cara', 'pin')
        self.assertEqual(ppv.points(), {'reymysterio': 1,
                                              'sin-cara': 15,
                                              'santinomarella': 2,
                                              'mickfoley': 3,
                                              'markhenry': 1,
                                              'codyrhodes': 1
                                              })
