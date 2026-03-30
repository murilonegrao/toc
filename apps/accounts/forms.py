from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    name = forms.CharField(
        max_length=100,
        label='Nome Completo',
    )

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data['name']
        user.save()
        return user
