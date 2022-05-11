from django import forms




class ContactForm(forms.Form):
    subject = forms.CharField(label='Тема', widget=forms.TextInput(attrs={'class': 'input-text input-text--border-radius input-text--primary-style'}))
    content = forms.CharField(label='Текст', widget=forms.Textarea(attrs={'class': 'text-area text-area--border-radius text-area--primary-style', 'id': 'c-message'}))
