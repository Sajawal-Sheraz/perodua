from django.contrib import admin

from .models import AiImageGen, ImagegenModel, Prompt

# @admin.register(ImagegenModel)
# class ImagegenModelAdmin(admin.ModelAdmin):
#     list_display = ("id",)


@admin.register(AiImageGen)
class AiImageGenAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_prompt",
    )
