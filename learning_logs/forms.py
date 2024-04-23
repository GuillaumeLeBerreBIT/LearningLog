from django import forms
from .models import Topic, Entry

# Nested class to tell Django which model to base the form on and which fields to include in the form
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text', 'public']
        labels = {'text': '', 'public': 'Public'}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}