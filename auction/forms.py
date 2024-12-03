from django import forms


class TopUpForm(forms.Form):
    amount = forms.DecimalField(max_digits=6, decimal_places=2)


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)