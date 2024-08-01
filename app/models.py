from django.db import models

GEN_CHOICES_QUALITY = [
    ("hd", "HD"),
    ("standard", "Standard"),
]

GEN_CHOICES_SIZE = [
    ("1024x1024", "1024x1024"),
    ("1792x1024", "1792x1024"),
    ("1024x1792", "1024x1792"),
]


GEN_CHOICES_STYLE = [("vivid", "Vivid"), ("natural", "Natural")]


# https://stackoverflow.com/a/35321718
# def FileSize(limit):
#     def file_size(value):
#         if value.size > limit * 1024 * 1024:
#             raise ValidationError(
#                 f"File too large. Size should not exceed {limit} MiB."
#             )

#     return file_size


class ImagegenModel(models.Model):
    user_image = models.FileField(name="image", upload_to="uploads/")
    user_prompt = models.TextField(name="prompt", max_length=255)
    user_quality = models.CharField(
        name="quality", choices=GEN_CHOICES_QUALITY, max_length=225
    )
    user_size = models.CharField(name="size", choices=GEN_CHOICES_SIZE, max_length=225)
    user_style = models.CharField(
        name="style", choices=GEN_CHOICES_STYLE, max_length=225
    )


class AiImageGen(models.Model):
    user_image = models.FileField(upload_to="uploads/")
    ai_image_url = models.URLField(blank=True, null=True)
