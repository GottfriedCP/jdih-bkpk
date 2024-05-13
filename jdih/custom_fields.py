from django.db.models import FileField
from django.forms import forms
from django.utils.translation import gettext_lazy as _


class ContentTypeRestrictedFileField(FileField):
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", [])
        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        try:
            file = data.file
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_("Ukuran berkas terlalu besar."))
            else:
                raise forms.ValidationError(_("Tipe berkas tidak memenuhi syarat."))
        except:
            pass

        return data
