from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from misago.apps.threadtype.mixins import ValidateThreadNameMixin, ValidatePostLengthMixin
from misago.forms import Form
from misago.validators import validate_sluggable

class PostingForm(Form, ValidatePostLengthMixin):
    post = forms.CharField(widget=forms.Textarea)

    def __init__(self, data=None, file=None, request=None, forum=None, thread=None, *args, **kwargs):
        self.forum = forum
        self.thread = thread
        super(PostingForm, self).__init__(data, file, request=request, *args, **kwargs)

    def finalize_form(self):
        self.layout = [
                       [
                        None,
                        [
                         ('post', {'label': _("Post Content")}),
                         ]
                        ]
                       ]

        # Can we change threads states?
        if (self.request.acl.threads.can_pin_threads(self.forum) >= self.thread.weight and
                self.request.acl.threads.can_pin_threads(self.forum)):
            thread_weight = []
            if self.request.acl.threads.can_pin_threads(self.forum) == 2:
                thread_weight.append((2, _("Announcement")))
            thread_weight.append((1, _("Sticky")))
            thread_weight.append((0, _("Standard")))
            if thread_weight:
                self.layout[0][1].append(('thread_weight', {'label': _("Thread Importance")}))
                self.fields['thread_weight'] = forms.TypedChoiceField(widget=forms.RadioSelect,
                                                                      choices=thread_weight,
                                                                      required=False,
                                                                      coerce=int,
                                                                      initial=(self.thread.weight if self.thread else 0))

        # Can we lock threads?
        if self.request.acl.threads.can_close(self.forum):
            self.fields['close_thread'] = forms.BooleanField(required=False)
            if self.thread and self.thread.closed:
                self.layout[0][1].append(('close_thread', {'inline': _("Open Thread")}))
            else:
                self.layout[0][1].append(('close_thread', {'inline': _("Close Thread")}))

    def clean_thread_weight(self):
        data = self.cleaned_data['thread_weight']
        if not data:
            if self.thread:
                return self.thread.weight
            return 0
        return data


class NewThreadForm(PostingForm, ValidateThreadNameMixin):
    def finalize_form(self):
        super(NewThreadForm, self).finalize_form()
        self.layout[0][1].append(('thread_name', {'label': _("Thread Name")}))
        self.fields['thread_name'] = forms.CharField(max_length=self.request.settings['thread_name_max'],
                                                     validators=[validate_sluggable(_("Thread name must contain at least one alpha-numeric character."),
                                                                                    _("Thread name is too long. Try shorter name."))])


class EditThreadForm(NewThreadForm, ValidateThreadNameMixin):
    def finalize_form(self):
        super(EditThreadForm, self).finalize_form()
        self.fields['edit_reason'] = forms.CharField(max_length=255, required=False, help_text=_("Optional reason for editing this thread."))
        self.layout[0][1].append(('edit_reason', {'label': _("Edit Reason")}))


class NewReplyForm(PostingForm):
    pass


class EditReplyForm(PostingForm):
    def finalize_form(self):
        super(EditReplyForm, self).finalize_form()
        self.fields['edit_reason'] = forms.CharField(max_length=255, required=False, help_text=_("Optional reason for editing this reply."))
        self.layout[0][1].append(('edit_reason', {'label': _("Edit Reason")}))
