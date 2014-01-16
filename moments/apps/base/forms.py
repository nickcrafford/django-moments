from django import forms

class UploadZipFileForm(forms.Form):
    file  = forms.FileField(required=True, label="Choose zip file")	
