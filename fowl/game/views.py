from collections import defaultdict
from itertools import izip_longest
from django.shortcuts import render, get_object_or_404
from fowl.game.models import Team, TeamPoints


def events(request):
    events = {}
    points = TeamPoints.objects.filter().order_by('match',
                                                  'team').select_related()
    for tp in points:
        event_id = tp.match.event_id
        if event_id not in events:
            events[event_id] = tp.match.event
            events[event_id].scores = {}
            events[event_id].match_list = {}
        events[event_id].match_list.setdefault(tp.match, []
                                               ).append(tp)
        events[event_id].scores.setdefault(tp.team.name, 0)
        events[event_id].scores[tp.team.name] += tp.points
    return render(request, "events.html", {'events': events})

def edit_event(request, event_id=None):
    if event_id:
        event = get_object_or_404(Event, pk=event_id)
    else:
        event = None
    if request.method == 'GET':
        return render(request, "edit_event.html", {"event": event})


def stables(request):
    context = { 'belts': ['ic', 'us', 'heavyweight', 'wwe']
              }
    teams = list(Team.objects.all().prefetch_related('stars'))
    context['teams'] = teams
    context['star_sets'] = izip_longest(*(team.stars.all() for team in teams))
    return render(request, "stables.html", context)
