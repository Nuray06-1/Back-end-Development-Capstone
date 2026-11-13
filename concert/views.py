"""Band application views; completed with OpenAI Codex assistance, 2026-11-13."""
import os
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending


def index(request):
    return render(request, 'index.html')


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username, password = form.cleaned_data['username'], form.cleaned_data['password']
        try:
            validate_password(password)
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password)
        except ValidationError as exc:
            form.add_error('password', exc)
        except IntegrityError:
            form.add_error('username', 'This username is already in use.')
        else:
            login(request, user)
            return redirect('index')
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('index')
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


def songs(request):
    try:
        response = requests.get(os.environ.get('SONGS_SERVICE_URL', 'http://127.0.0.1:5082') + '/song', timeout=10)
        response.raise_for_status()
        items = response.json()['songs']
    except (requests.RequestException, ValueError, KeyError):
        return render(request, 'songs.html', {'songs': [], 'service_error':'Songs are temporarily unavailable.'}, status=503)
    return render(request, 'songs.html', {'songs':items})


def photos(request):
    try:
        response = requests.get(os.environ.get('PICTURES_SERVICE_URL', 'http://127.0.0.1:5081') + '/picture', timeout=10)
        response.raise_for_status()
        items = response.json()
    except (requests.RequestException, ValueError):
        return render(request, 'photos.html', {'photos': [], 'service_error':'Photos are temporarily unavailable.'}, status=503)
    return render(request, 'photos.html', {'photos':items})


@login_required(login_url='login')
def concerts(request):
    statuses = dict(ConcertAttending.objects.filter(user=request.user).values_list('concert_id','attending'))
    items = [{'concert':c,'status':statuses.get(c.pk,'-')} for c in Concert.objects.order_by('date')]
    return render(request,'concerts.html',{'concerts':items})


@login_required(login_url='login')
def concert_detail(request,id):
    concert = get_object_or_404(Concert,pk=id)
    attendance = concert.attendee.filter(user=request.user).first()
    return render(request,'concert_detail.html',{'concert_details':concert,'status':attendance.attending if attendance else '-','attending_choices':ConcertAttending.AttendingChoices.choices})


@login_required(login_url='login')
@require_POST
def concert_attendee(request):
    concert = get_object_or_404(Concert,pk=request.POST.get('concert_id'))
    status = request.POST.get('attendee_choice')
    if status not in ConcertAttending.AttendingChoices.values:
        return HttpResponseBadRequest('Invalid attendance choice')
    ConcertAttending.objects.update_or_create(concert=concert,user=request.user,defaults={'attending':status})
    return redirect('concerts')
