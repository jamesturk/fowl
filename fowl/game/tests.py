from django.test import TestCase
from django.core.management import call_command
from .models import Match, Event

class MatchTest(TestCase):
    def setUp(self):
        call_command('loadstars')
        self.wm29 = Event.objects.create(name='Wrestlemania 29', date='2012-04-01')

    def test_basics(self):
        match = Match.objects.create(event=self.wm29)
        match.add_team('tripleh')
        match.add_team('undertaker')
        self.assertEqual(unicode(match), 'Triple H vs. Undertaker')
        match.record_win('undertaker', 'pin')
        self.assertEqual(unicode(match), 'Triple H vs. Undertaker (v)')
        match.points()