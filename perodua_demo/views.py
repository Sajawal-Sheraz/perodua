from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render

from app.models import AiImageGen, ImagegenModel

from .openai_client import generate_image
from .settings import FILE_UPLOAD_MAX_MEMORY_SIZE


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = ImagegenModel
        fields = [
            "image",
            "prompt",
            "quality",
            "size",
            "style",
        ]


def imagegen(request):
    if request.method == "POST":
        try:
            img = request.FILES["image"].read()
            images = generate_image(
                img,
                request.POST.get("prompt", ""),
                "hd",
                "1792x1024",
                "natural",
            )
            image_object = images[0]
            url = image_object.url

            return render(request, "home.html", {"images": images, "ai_image_url": url})
        except Exception as e:
            return render(request, "home.html")
    return render(request, "home.html")


def index(request):
    return render(request, "home.html")
