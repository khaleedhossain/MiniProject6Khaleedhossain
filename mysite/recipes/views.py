# INF601 - Advanced Programming in Python
# Khaleed Hossain
# Mini Project 6

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RecipeForm, RegisterForm
from .models import Ingredient, Recipe


def index(request):
    recipes = Recipe.objects.select_related("author").all()
    return render(request, "recipes/index.html", {"recipes": recipes})


@login_required
def mine(request):
    recipes = Recipe.objects.filter(author=request.user)
    return render(request, "recipes/my_recipes.html", {"recipes": recipes})


def detail(request, pk):
    recipe = get_object_or_404(Recipe.objects.select_related("author"), pk=pk)
    return render(request, "recipes/detail.html", {"recipe": recipe})


@login_required
def create(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            Ingredient.objects.bulk_create([
                Ingredient(recipe=recipe, position=i, description=text)
                for i, text in enumerate(form.cleaned_data["ingredients"])
            ])
            return redirect("recipes:detail", pk=recipe.pk)
    else:
        form = RecipeForm()

    return render(request, "recipes/recipe_form.html", {"form": form, "heading": "New Recipe"})


@login_required
def update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author_id != request.user.id:
        return HttpResponseForbidden("You can only edit your own recipes.")

    if request.method == "POST":
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            recipe = form.save()
            recipe.ingredients.all().delete()
            Ingredient.objects.bulk_create([
                Ingredient(recipe=recipe, position=i, description=text)
                for i, text in enumerate(form.cleaned_data["ingredients"])
            ])
            return redirect("recipes:detail", pk=recipe.pk)
    else:
        initial = {"ingredients": "\n".join(i.description for i in recipe.ingredients.all())}
        form = RecipeForm(instance=recipe, initial=initial)

    return render(request, "recipes/recipe_form.html",
                  {"form": form, "heading": f'Edit "{recipe.title}"', "recipe": recipe})


@login_required
def delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author_id != request.user.id:
        return HttpResponseForbidden("You can only delete your own recipes.")
    if request.method == "POST":
        recipe.delete()
        return redirect("recipes:index")
    return redirect("recipes:detail", pk=pk)


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("recipes:index")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})
