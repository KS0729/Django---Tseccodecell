from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import SettingsForm, ChallengeForm
from django import forms
from django.views import generic
from django.urls import reverse
from .models import CCUser, Challenge, CorrectSubmission
from .constants import getBasePoints, getBonusPointScaling,getRankConstant
import sys

def index(request):
    req_user = None
    if request.user.is_authenticated:
        req_user = CCUser.objects.filter(user = request.user)[0]
        print(req_user)
    return render(request, 'codecell/index.html',{'req_user':req_user})

def error_404_view(request, exception):
    return render(request,'codecell/error_404.html')

#fill in preset values
def init_settings_form(request):
    initial = {}
    if request.user.first_name:
        initial['first_name'] = request.user.first_name
    if request.user.last_name:
        initial['last_name'] = request.user.last_name
    if request.user.profile.year:
        initial['year_choice'] = request.user.profile.year
    if request.user.profile.branch:
        initial['branch_choice'] = request.user.profile.branch
    return initial


@login_required
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.last_name = form.cleaned_data.get('last_name')
            request.user.profile.year = form.cleaned_data.get('year_choice')
            request.user.profile.branch = form.cleaned_data.get('branch_choice')
            request.user.save()
            request.user.profile.save()
            return redirect('index')
        else:
            print('invalid')
    else:
        form = SettingsForm(initial=init_settings_form(request))
    return render(request, 'codecell/settings.html', {'form': form})

# redirect if loggedin
@user_passes_test(lambda u: not u.is_authenticated, redirect_field_name=None, login_url='/')
def login(request):
    # return render(request, 'codecell/login.html')
    return redirect(reverse("social:begin", args=["google-oauth2"]))

def user_detail(request, user_id):
    req_user = get_object_or_404(CCUser, pk=user_id)
    user_submissions = CorrectSubmission.objects.filter(user_id = user_id)
    return render(request, 'codecell/user_detail.html', {'req_user' : req_user, 'user_submissions':user_submissions})

def ranklist(request):
    ranklist = CCUser.objects.order_by('rank')[:100]
    return render(request, 'codecell/ranklist.html',{'ranklist' :ranklist})


def about(request):
    return render(request, 'codecell/about.html')

def challenge_ranklist(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    submissions = CorrectSubmission.objects.filter(challenge_id=challenge_id)
    #Links to solution can be viewed only if user is logged in and has solved the problem
    solution_view = False
    if request.user.is_authenticated:
        if submissions.filter(user__user__username=request.user):
            solution_view = True
    return render(request, 'codecell/challenge_ranklist.html', {'challenge': challenge, 'submissions' : submissions, 'solution_view' : solution_view})

class ChallengeListView(generic.ListView):
    template_name = 'codecell/challenge_list.html'
    context_object_name = 'challenges_list'

    def get_queryset(self):
        return Challenge.objects.order_by('-pub_date')

    def get_context_data(self, *args, **kwargs):
        context = super(ChallengeListView, self).get_context_data(*args, **kwargs)
        if self.request.user.is_authenticated:
            user  = CCUser.objects.filter(user = self.request.user)[0]
            user_submissions =  CorrectSubmission.objects.filter(user = user)
            solved_challenges =  Challenge.objects.filter(id__in=user_submissions.values('challenge_id')).order_by('-pub_date')
            unsolved_challenges =  Challenge.objects.exclude(id__in=user_submissions.values('challenge_id')).order_by('-pub_date')
            context['solved_challenges_list'] = solved_challenges
            context['unsolved_challenges_list'] = unsolved_challenges
        return context

def challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    form = ChallengeForm()
    submission =  ''
    form_error = ''
    base_points = getBasePoints(challenge.difficulty)
    base_points_message = 'This challenge is worth '+str(base_points)+' points.'

    if request.user.is_authenticated:
        user  = CCUser.objects.filter(user = request.user)[0]
        solved = CorrectSubmission.objects.filter(user = user, challenge = challenge)
        if solved.exists():
            form_error = 'You have sucessfully solved the challenge'
            form = ''
        elif request.method == 'POST':
            form =  ChallengeForm(request.POST)

            challenge.total_attempts = challenge.total_attempts + 1
            challenge.save()

            if form.is_valid():
                print(form.cleaned_data.get('solution'))
                print(challenge.solution_text)
                if form.cleaned_data.get('solution') == challenge.solution_text:

                    # save CorrectSubmission
                    n_solved = CorrectSubmission.objects.filter(challenge = challenge).count()
                    base_points = getBasePoints(challenge.difficulty)
                    bonus_points = getBonusPointScaling(n_solved, challenge.difficulty) * base_points
                    points = base_points + bonus_points
                    link = form.cleaned_data.get('solution_link')
                    correct_submission = CorrectSubmission(challenge = challenge, user= user, points = points, solution_link = link)
                    correct_submission.save()

                    # update user stats
                    user.total_points = user.total_points + points
                    user.challenge_points = user.challenge_points + points
                    user.save()
                    update_user_ranks()

                    #update challenge stats
                    challenge.correct_submissions = challenge.correct_submissions + 1
                    challenge.save()
                    if bonus_points == 0:
                        submission = 'Correct! You are awarded '+ str(points) +' points'
                    else:
                        submission = 'Correct! You are awarded '+ str(points) +' points ('+str(bonus_points)+' extra points for being the '+getRankConstant(n_solved+1)+' person to solve it!)'
                    form = ''
                else:
                    #answer is wrong
                    submission = 'That is incorrect, try again'
                    form = ChallengeForm()
            else:
                print('invalid')
    else:
        #not logged in
        form = ''
        form_error = 'You must be logged in to submit a solution'

    return render(request, 'codecell/challenge_detail.html', {'challenge':challenge, 'base_points_message':base_points_message, 'submission':submission, 'form': form, 'form_error':form_error})


def update_user_ranks():
    users_set = CCUser.objects.order_by('-total_points')
    r = 0
    last_total = sys.maxsize
    for user in users_set:
        #In case of tie, rank is not increased
        if user.total_points < last_total:
            last_total = user.total_points
            r = r + 1
        user.rank = r
        user.save()

def privacypolicy(request):
    return render(request, 'codecell/privacypolicy.html')
