from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
# Create your models here.


class Challenge(models.Model):
    heading_text = models.CharField(max_length=1000)
    question_text = models.CharField(max_length=5000)
    solution_text = models.CharField(max_length=100)
    difficulty = models.IntegerField()
    correct_submissions = models.IntegerField()
    total_attempts = models.IntegerField()
    pub_date = models.DateTimeField('date published')
    hint = models.CharField(max_length=1000, blank=True)
    show_hint = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text[:30]


class CCUser(models.Model):
    YEAR_CHOICES = (
        ('FE', 'FE'),
        ('SE', 'SE'),
        ('TE', 'TE'),
        ('BE', 'BE'),)
    BRANCH_CHOICES = (
        ('IT', 'IT'),
        ('Computer', 'Computer'),
        ('EXTC', 'EXTC'),
        ('Chemical', 'Chemical'),
        ('Biomedical', 'Biomedical'),
        ('Biotech', 'Biotech'),)
    user = models.OneToOneField(
        User, unique=True, null=True, on_delete=models.CASCADE, related_name='profile')
    year = models.CharField(max_length=2, choices=YEAR_CHOICES, blank=True)
    branch = models.CharField(
        max_length=16, choices=BRANCH_CHOICES, blank=True)
    total_points = models.PositiveIntegerField(default=0)
    challenge_points = models.PositiveIntegerField(default=0)
    last_challenge = models.ForeignKey(
        Challenge, on_delete=models.SET_NULL, null=True)
    rank = models.PositiveIntegerField(default = 0)

    def __str__(self):
        return self.user.username


class CorrectSubmission(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    user = models.ForeignKey(CCUser, on_delete=models.CASCADE)
    points = models.IntegerField()
    solution_link = models.CharField(max_length=200, default='')

    def __str__(self):
        return str(self.challenge) + str(self.user)

from .views import update_user_ranks

def post_save_receiver(sender, instance, created, **kwargs):
    if created:
        new_profile = CCUser(user=instance)
        new_profile.save()
        update_user_ranks()

post_save.connect(post_save_receiver, sender=settings.AUTH_USER_MODEL)
