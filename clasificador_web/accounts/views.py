from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    accept_terms = forms.BooleanField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "username", "email")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "register.html", {"form": form})
