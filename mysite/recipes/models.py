# INF601 - Advanced Programming in Python
# Khaleed Hossain
# Mini Project 6

from django.conf import settings
from django.db import models


class Recipe(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="recipes")
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                                related_name="ingredients")
    position = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=200)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.description
