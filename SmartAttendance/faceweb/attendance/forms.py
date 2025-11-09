# attendance/forms.py
from django import forms

class FaceForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    regd_no = forms.CharField(label='Register Number', max_length=20)
    department = forms.CharField(label='Department', max_length=50)
    image = forms.ImageField(label='Upload Face Image')
