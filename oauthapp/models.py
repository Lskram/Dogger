from django.db import models


class OwnerToken(models.Model):
    owner_id = models.CharField(max_length=32, unique=True)
    refresh_token = models.CharField(max_length=512)
    access_token = models.CharField(max_length=512, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    scope = models.CharField(max_length=255, null=True, blank=True)
    token_type = models.CharField(max_length=32, null=True, blank=True)
    profile_json = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OwnerToken(owner_id={self.owner_id})"

