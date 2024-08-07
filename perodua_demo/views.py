import os

import qrcode
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.shortcuts import render

from app.models import AiImageGen, ImagegenModel, Prompt

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
            if request.POST.get("testInput", False):
                images = generate_image(
                    img,
                    request.POST.get("prompt", ""),
                    "hd",
                    "1792x1024",
                    request.POST.get("style", "").lower(),
                    request.POST.get("style2", "").lower(),
                    request.POST.get("user_prompt", ""),
                )
            else:
                images = generate_image(
                    img,
                    request.POST.get("prompt", ""),
                    "hd",
                    "1792x1024",
                    request.POST.get("style", "").lower(),
                    request.POST.get("style2", "").lower(),
                    Prompt.objects.first().user_prompt,
                )
            image_object = images[0]
            ai_image_url = image_object.url
            url = ai_image_url

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(ai_image_url)
            qr.make(fit=True)

            # Create and save the QR code image
            qr_img = qr.make_image(fill="black", back_color="white")
            qr_img_path = os.path.join(settings.MEDIA_ROOT, "temp_qrcode.png")
            qr_img.save(qr_img_path)

            # Attach QR code image to the model
            with open(qr_img_path, "rb") as f:
                ai_image_qr = File(f, name="temp_qrcode.png")

                obj = AiImageGen.objects.create(
                    user_image=request.FILES["image"],
                    ai_image_url=ai_image_url,
                    ai_image_qr=ai_image_qr,
                )

            # Remove the temporary QR code image file
            os.remove(qr_img_path)

            if request.POST.get("testInput", False):
                return render(
                    request,
                    "dashboard.html",
                    {
                        "images": images,
                        "ai_image_url": url,
                        "obj": obj,
                        "user_prompt": request.POST.get("user_prompt", ""),
                    },
                )
            return render(
                request,
                "home.html",
                {"images": images, "ai_image_url": url, "obj": obj},
            )

        except Exception as e:
            print(f"There is something wrong: {e}")
            return render(request, "home.html")
    return render(request, "home.html")


def index(request):
    return render(request, "home.html")


def dashboard(request):
    return render(request, "dashboard.html")


def save_prompt(request):
    Prompt.objects.all().delete()
    Prompt.objects.create(user_prompt=request.GET.get("user_prompt"))
    return render(request, "dashboard.html")
