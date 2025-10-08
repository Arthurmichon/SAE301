from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import Prise
from .mqtt_client import envoyer_commande_prise
from datetime import time, timedelta,datetime

def is_now_in_range(now: time, start: time, end: time) -> bool:

    if start <= end:
        return start <= now <= end
    else:
        return now >= start or now <= end


scheduler = None

def check_plages(return_changes=False):
    now = timezone.localtime().time()
    changes = []
    print(f"[TACHE_HORAIRE] Vérif plages - maintenant = {now}")

    for prise in Prise.objects.filter(horaire_active=True):
        print(f"[TACHE_HORAIRE] Prise {prise.id} horaires: on={prise.heure_on} off={prise.heure_off} etat={prise.etat}")
        if prise.heure_on and prise.heure_off:
            should_be_on = is_now_in_range(now, prise.heure_on, prise.heure_off)
            if prise.etat != should_be_on:
                prise.etat = should_be_on
                prise.save()
                print(f"[TACHE_HORAIRE] -> changement etat pour prise {prise.id}: {should_be_on}")
                envoyer_commande_prise(should_be_on)
                changes.append({'id': prise.id, 'new': should_be_on})
        else:
            print(f"[TACHE_HORAIRE] Prise {prise.id} active mais heures manquantes")
    if return_changes:
        return {'now': str(now), 'changes': changes}
    return None



def verifier_plages():
    now = datetime.now().time()
    for prise in Prise.objects.filter(horaire_active=True):
        if not prise.heure_on or not prise.heure_off:
            continue

        if prise.heure_on <= now < prise.heure_off:
            if not prise.etat:
                envoyer_commande_prise(prise.id, "on")
                prise.etat = True
                prise.save()
        else:
            if prise.etat:
                envoyer_commande_prise(prise.id, "off")
                prise.etat = False
                prise.save()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(verifier_plages, 'interval', seconds=10)
    scheduler.start()

