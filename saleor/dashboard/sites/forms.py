from django import forms

from ...site.models import SiteSettings, AuthorizationKey


class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        exclude = []
    def __init__(self, *args, **kwargs):        
        super(SiteSettingForm, self).__init__(*args, **kwargs)        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        field = self.fields['closing_time'] 
        field.widget.attrs['class'] = 'form-control pickatime-editable'
        closing_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M %p'))
        
        field = self.fields['opening_time'] 
        field.widget.attrs['class'] = 'form-control pickatime-editable'
        


class AuthorizationKeyForm(forms.ModelForm):
    class Meta:
        model = AuthorizationKey
        exclude = []
        widgets = {'password': forms.PasswordInput(render_value=True),
                   'key': forms.TextInput(),
                   'site_settings': forms.HiddenInput()}


AuthorizationKeyFormSet = forms.modelformset_factory(
    AuthorizationKey, form=AuthorizationKeyForm, can_delete=True)
