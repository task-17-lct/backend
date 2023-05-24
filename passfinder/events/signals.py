from django.db.models.signals import pre_save
from django.dispatch import receiver

from passfinder.events.models import Category
from passfinder.utils.generators import generate_charset


@receiver(pre_save, sender=Category)
def create_model_link(sender, instance, created, **kwargs):
    if instance.id is None:
        oid = generate_charset(24)
        while Category.objects.filter(oid=oid).exists():
            oid = generate_charset(24)

        instance.oid = oid
