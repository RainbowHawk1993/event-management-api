Just a small Django REST-Api for Event Management

API Documentation:

**Overview**
The Events API allows users to view, create, update, delete, and register for events. It includes the following views:

- IndexView - List all events.
- DetailView - View details of a specific event.
- CreateView - Create a new event (restricted to authenticated users).
- UpdateView - Update an existing event (restricted to authenticated users).
- DeleteView - Delete an event (restricted to authenticated users).
- register_for_event - Register a user for a specific event (restricted to authenticated users).

1. IndexView
- Description: Retrieves a list of all events, ordered by date (most recent first).
- URL: `/events/`
- HTTP Method: GET
- Authentication: Not required
- Template: events/index.html
- Context Data:
`events_list`: List of events ordered by date.
- Example Response:
Displays a list of all events in events/index.html.

2. DetailView
- Description: Retrieves details for a specific event, including whether the current user is registered.
- URL: `/events/<int:pk>/`
- HTTP Method: GET
- Authentication: Optional (registration status shown if authenticated)
- Template: events/detail.html
- Context Data:
`event`: Event object with full details;
`is_registered`: Boolean indicating if the current user is registered for the event.
- Example Response:
Displays the details of an event in events/detail.html, along with registration status if the user is authenticated.

3. CreateView
- Description: Allows authenticated users to create a new event.
- URL: `/events/create/`
- HTTP Method: POST
- Authentication: Required
- Template: events/form.html
- Form Class: EventForm
- Redirects To: Event detail page on success.
- Example Request:

```
POST /events/create/
Content-Type: application/x-www-form-urlencoded

title=Sample Event&description=Description&date=2024-11-15T10:00:00Z&location=Conference Hall&organizer=John Doe
```

4. UpdateView
- Description: Allows authenticated users to update an existing event they created.
- URL: `/events/<int:pk>/update/`
- HTTP Method: POST
- Authentication: Required
- Template: events/form.html
- Form Class: EventForm
- Redirects To: Event detail page on success.
- Example Request:

```
POST /events/1/update/
Content-Type: application/x-www-form-urlencoded

title=Updated Event Title&description=Updated Description
```

5. DeleteView
- Description: Allows authenticated users to delete an existing event they created.
- URL: `/events/<int:pk>/delete/`
- HTTP Method: POST
- Authentication: Required
- Template: events/confirm_delete.html
- Redirects To: Events index page on success.
- Example Request:

```
POST /events/1/delete/
```

6. `register_for_event`
- Description: Allows authenticated users to register for an event. Checks if the user is already registered and returns an appropriate message.
- URL: `/events/<int:event_id>/register/`
- HTTP Method: POST
- Authentication: Required
- Redirects To: Event detail page with a success or warning message.
- Example Request:

```
POST /events/1/register/
```
- Example Response
If Already Registered: Displays a warning message, "You are already registered for this event."
If Newly Registered: Displays a success message, "Successfully registered for *event title*."
