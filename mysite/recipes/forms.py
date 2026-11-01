# INF601 - Advanced Programming in Python
# Khaleed Hossain
# Mini Project 6

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Recipe


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RecipeForm(forms.ModelForm):
    # Ingredients aren't a model field: the view splits this textarea, one
    # line per Ingredient row, and links each to the saved Recipe.
    ingredients = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 6, "class": "form-control",
            "placeholder": "2 cups flour\n1 tsp salt\n3 eggs",
        }),
        help_text="One ingredient per line.",
    )

    class Meta:
        model = Recipe
        fields = ["title", "instructions", "ingredients"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "instructions": forms.Textarea(attrs={"rows": 8, "class": "form-control"}),
        }

    def clean_ingredients(self):
        lines = [line.strip() for line in self.cleaned_data["ingredients"].splitlines()]
        lines = [line for line in lines if line]
        if not lines:
            raise forms.ValidationError("At least one ingredient is required.")
        return lines
