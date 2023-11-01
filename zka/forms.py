from django import forms

class CharacterNameForm(forms.Form):
    character_name = forms.CharField(label='character_name')