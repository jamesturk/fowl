from itertools import izip_longest
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from fowl.game.models import Team, TeamPoints, Star, Event, OUTCOMES, TITLES


def events(request, league_id):
    events = {}
    points = TeamPoints.objects.filter(team__league_id=league_id).order_by(
        'match', 'team').select_related()
    for tp in points:
        event_id = tp.match.event_id
        if event_id not in events:
            events[event_id] = tp.match.event
            events[event_id].scores = {}
            events[event_id].match_list = {}
        events[event_id].match_list.setdefault(tp.match, []
                                               ).append(tp)
        events[event_id].scores.setdefault(tp.team, 0)
        events[event_id].scores[tp.team] += tp.points
    events = sorted(events.values(), key=lambda x: x.date, reverse=True)
    return render(request, "events.html", {'events': events, 'view': 'events'})


def edit_event(request, event):
    if event == 'new':
        event = None
    else:
        event = get_object_or_404(Event, pk=event).to_dict()

    if request.method == 'POST':
        edict = {}
        edict['id'] = request.POST.get('id')
        edict['name'] = request.POST.get('name')
        edict['date'] = request.POST.get('date')
        edict['matches'] = []

        outcomes = request.POST.getlist('outcome')
        winners = request.POST.getlist('winner')
        titles = request.POST.getlist('title')
        notes = request.POST.getlist('notes')
        for i, note in enumerate(notes):
            edict['matches'].append({'outcome': outcomes[i],
                                     'winner': winners[i],
                                     'title_at_stake': titles[i],
                                     'notes': notes[i],
                                     'teams': [],
                                    })

        for k,v in request.POST.iterlists():
            if k.startswith('members'):
                _, match, team = k.split('-')
                edict['matches'][int(match)-1]['teams'].append(v)

        event = Event.from_dict(edict)

    return render(request, "edit_event.html",
                  {'event': event,
                   'OUTCOMES': OUTCOMES,
                   'TITLES': TITLES}
                 )

def league(request, league_id):
    context = {
        'view': 'league',
        'belts': ['ic', 'us', 'heavyweight', 'wwe']
    }
    teams = list(Team.objects.filter(league__id=league_id)
                 .prefetch_related('stars'))
    context['teams'] = teams
    context['star_sets'] = izip_longest(*(team.stars.all().order_by("division")
                                          for team in teams))
    return render(request, "stables.html", context)


def roster(request):
    context = {
        'stars': Star.objects.all(),
        'view': 'roster'
    }
    return render(request, "roster.html", context)
