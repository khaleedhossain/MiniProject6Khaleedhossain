# INF601 - Advanced Programming in Python
# Khaleed Hossain
# Mini Project 6

from django.contrib import admin

from .models import Ingredient, Recipe


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created", "ingredient_count")
    list_filter = ("author", "created")
    search_fields = ("title", "instructions")
    date_hierarchy = "created"
    inlines = [IngredientInline]

    @admin.display(description="Ingredients")
    def ingredient_count(self, obj):
        return obj.ingredients.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("description", "recipe", "position")
    list_filter = ("recipe",)
    search_fields = ("description",)
