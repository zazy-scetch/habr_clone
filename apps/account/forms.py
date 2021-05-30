from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.forms import CharField

from apps.articles.models import Article
from apps.authorization.models import HabrUserProfile, HabrUser

class HabrUserProfileEditForm(forms.ModelForm):
    class Meta:
        model = HabrUserProfile
        fields = (
            "first_name",
            "last_name",
            "place_of_work",
            "specialization",
            "gender",
            "birth_date",
            "country",
            "region",
            "city",
            "avatar",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.help_text = ""


class ArticleCreate(forms.ModelForm):
    body = CharField(
        label="Текст статьи",
        widget=CKEditorUploadingWidget(config_name="for_user"),
    )

    class Meta:
        model = Article
        fields = ("title", "hub", "image", "link_to_original", "body")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.help_text = ""
            field.required = ""

    def clean_title(self):
        data = self.cleaned_data['title']
        if not data:
            raise forms.ValidationError('Заполните заголовок!')
        return data

    def clean_body(self):
        data = self.cleaned_data['body']
        if not data:
            raise forms.ValidationError('Заполните текст!')
        return data

# class ArticleCreate(forms.ModelForm):
#
#     class Meta:
#         model = Article
#         # fields = (
#         #     "title",
#         #     "hubs",
#         #     "body",
#         #     "image",
#         #     "link_to_original"
#         # )
#
# def __init__(self, *args, **kwargs):
#     super().__init__(*args, **kwargs)
#     for field_name, field in self.fields.items():
#         field.widget.attrs["class"] = "form-control"
#         field.help_text = ""


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(), label="введите старый пароль"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(), label="введите новый пароль"
    )
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(), label="повторите пароль"
    )

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.help_text = ""
            field.required = ""


class ArticleEditForm(forms.ModelForm):
    body = CharField(widget=CKEditorUploadingWidget(config_name="for_user"))

    class Meta:
        model = Article
        fields = ("title", "hub", "image", "link_to_original", "body")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.help_text = ""


# class ArticleEditForm(forms.ModelForm):
#     class Meta:
#         model = Article
#         fields = (
#             "title",
#             "hubs",
#             "body",
#             "image",
#             "link_to_original"
#         )
#
#     def __init__(self, *args, **kwargs):
#         super(ArticleEditForm, self).__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs["class"] = "form-control"
#             field.help_text = ""
