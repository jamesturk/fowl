from collections import defaultdict
from django.shortcuts import render
from fowl.game.models import TeamPoints


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


def stables(request):
    return render(request, "stables.html")
