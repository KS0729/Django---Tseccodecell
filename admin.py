from django.contrib import admin

from .models import CCUser, Challenge, CorrectSubmission
# Register your models here.

class CorrectSubmissionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'solution_link']

admin.site.register(CCUser)
admin.site.register(Challenge)
admin.site.register(CorrectSubmission, CorrectSubmissionAdmin)
