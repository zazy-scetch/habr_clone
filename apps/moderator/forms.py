from django import forms

from apps.moderator.models import BannedUser, VerifyArticle, ComplainToComment


class BannedUserForm(forms.ModelForm):
    class Meta:
        model = BannedUser
        exclude = ('offender', 'date_ban', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_forever':
                field.widget.attrs["class"] = "checkbox-field"
            else:
                field.widget.attrs["class"] = "form-control"
            field.help_text = ""


class RemarkCreateForm(forms.ModelForm):
    class Meta:
        model = VerifyArticle
        fields = ('remark',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class ComplainCreateForm(forms.ModelForm):
    class Meta:
        model = ComplainToComment
        fields = ('text_complain',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class ReasonCreateForm(forms.ModelForm):
    class Meta:
        model = ComplainToComment
        fields = ('text_reason',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
