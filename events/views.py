from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Event


class IndexView(generic.ListView):
    template_name = "events/index.html"
    context_object_name = "events_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Event.objects.order_by("-date")


class DetailView(generic.DetailView):
    model = Event
    template_name = "events/detail.html"

#def detail(request, event_id):
#    event = get_object_or_404(Event, pk=event_id)
#    return render(request, "events/detail.html", {"event": event})
