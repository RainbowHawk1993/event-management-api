from django.db.models import F
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from .models import Event
from .forms import EventForm


class IndexView(generic.ListView):
    template_name = "events/index.html"
    context_object_name = "events_list"

    def get_queryset(self):
        return Event.objects.order_by("-date")


class DetailView(generic.DetailView):
    model = Event
    template_name = "events/detail.html"

class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/form.html"
    def get_success_url(self):
        return reverse_lazy('events:detail', args=[self.object.pk])

class UpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/form.html"
    def get_success_url(self):
        return reverse_lazy('events:detail', args=[self.object.pk])

class DeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Event
    template_name = "events/confirm_delete.html"
    success_url = reverse_lazy('events:index')
