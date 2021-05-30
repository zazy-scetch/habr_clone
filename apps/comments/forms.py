from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.forms import CharField

from apps.comments.models import Comment


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)


# class CommentCreateForm(forms.ModelForm):
#     body = CharField(label='Комментарий', widget=CKEditorUploadingWidget(config_name="for_user"))
#
#     class Meta:
#         model = Comment
#         fields = ("body",)
