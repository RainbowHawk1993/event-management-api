from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from .models import Event, EventRegistration
from .forms import EventForm
from .mixins import EventOwnerMixin


class IndexView(generic.ListView):
    template_name = "events/index.html"
    context_object_name = "events_list"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Event.objects.filter(title__icontains=query).order_by("-date")
        else:
            return Event.objects.order_by("-date")

class DetailView(generic.DetailView):
    model = Event
    template_name = "events/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizer'] = self.object.organizer.username
        if self.request.user.is_authenticated:
            context['is_registered'] = EventRegistration.objects.filter(
                user=self.request.user, event=self.object
            ).exists()
        else:
            context['is_registered'] = False
        return context

class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/form.html"

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('events:detail', args=[self.object.pk])

class UpdateView(LoginRequiredMixin, EventOwnerMixin, generic.UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/form.html"
    def get_success_url(self):
        return reverse_lazy('events:detail', args=[self.object.pk])

class DeleteView(LoginRequiredMixin, EventOwnerMixin, generic.DeleteView):
    model = Event
    template_name = "events/confirm_delete.html"
    success_url = reverse_lazy('events:index')

@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "You are already registered for this event.")
    else:
        EventRegistration.objects.create(user=request.user, event=event)
        messages.success(request, f"Successfully registered for {event.title}.")

    return redirect("events:detail", pk=event.id)
