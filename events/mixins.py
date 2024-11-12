from django.core.exceptions import PermissionDenied
from django.http import Http404

class EventOwnerMixin:
    def get_object(self, queryset=None):
        event = super().get_object(queryset)
        if event.organizer != self.request.user:
            raise PermissionDenied("You do not have permission to modify this event.")
        return event
