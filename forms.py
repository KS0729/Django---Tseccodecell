from django import forms


class SettingsForm(forms.Form):
    YEAR_CHOICES = (
        ('', '----'),
        ('FE', 'FE'),
        ('SE', 'SE'),
        ('TE', 'TE'),
        ('BE', 'BE'),)
    BRANCH_CHOICES = (
        ('', '----'),
        ('IT', 'IT'),
        ('Computer', 'Computer'),
        ('EXTC', 'EXTC'),
        ('Chemical', 'Chemical'),
        ('Biomedical', 'Biomedical'),
        ('Biotech', 'Biotech'),)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    year_choice = forms.ChoiceField(label='Year',choices=YEAR_CHOICES)
    branch_choice = forms.ChoiceField(label='Branch', choices=BRANCH_CHOICES)


class ChallengeForm(forms.Form):
    solution = forms.CharField(label='Your answer', max_length=100)
    solution_link = forms.URLField(label='Solution link', help_text='Upload your solution code on ideone, github or other code hosting sites and copy the link here. Your code must be publically viewable.')
