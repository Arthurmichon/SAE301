from django.db import models


class Prise(models.Model):
    nom = models.CharField(max_length=100)
    etat = models.BooleanField(default=False)
    horaire_active = models.BooleanField(default=False)
    heure_on = models.TimeField(null=True, blank=True)
    heure_off = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.nom

class Temperature(models.Model):
    value = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.value} °C"
