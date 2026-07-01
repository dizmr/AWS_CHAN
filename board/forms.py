from django import forms

from .models import Confession


class ConfessionForm(forms.ModelForm):
    class Meta:
        model = Confession
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'just type smt...',
                'maxlength': 1000,
                'rows': 5,
            })
        }
        labels = {'text': ''}

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        if len(text) < 3:
            raise forms.ValidationError('short msg')
        return text
