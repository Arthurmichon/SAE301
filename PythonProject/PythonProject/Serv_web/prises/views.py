from django.shortcuts import render, redirect, get_object_or_404
from .models import Prise
from .mqtt_client import envoyer_commande_prise
from datetime import datetime, timedelta
from django.contrib import messages
from .tache_horaire import is_now_in_range
from .models import Temperature
from .mqtt_client import envoyer_commande_toutes_les_leds

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "ctla" and password == "akaza":
            request.session["authenticated"] = True
            return redirect("page_accueil")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, "prises/login.html")

def toggle_all_leds(request):
    prises = Prise.objects.all()
    all_on = all(prise.etat for prise in prises)
    new_state = not all_on

    # Met à jour la base de données localement
    for prise in prises:
        prise.etat = new_state
        prise.save()

    # Envoie la commande globale MQTT
    envoyer_commande_toutes_les_leds(new_state)

    return redirect('page_accueil')

def is_now_in_range(now, start, end):

    if start is None or end is None:
        return False
    if start <= end:
        return start <= now < end
    else:
        # plage qui traverse minuit
        return now >= start or now < end


def set_prise_state(request, prise_id, etat):
    prise = get_object_or_404(Prise, id=prise_id)
    prise.etat = (etat == "on")
    prise.save()

    envoyer_commande_prise(prise.id, prise.etat)

    return redirect('page_accueil')


def page_accueil(request):
    if not request.session.get("authenticated"):
        return redirect("login")

    prises = Prise.objects.all()
    all_on = all(prise.etat for prise in prises) if prises else False
    from .models import Temperature
    temp = Temperature.objects.first()
    temperature = temp.value if temp else "--"
    return render(request, 'prises/page_accueil.html', {
        'prises': prises,
        'all_on': all_on,
        'temperature': temperature,
    })

def logout_view(request):
    request.session.flush()
    return redirect("login")


def etat_prise_api(request):
    prise = Prise.objects.first()
    if prise:
        return JsonResponse({'etat': prise.etat})
    return JsonResponse({'etat': None})



def set_horaire(request, prise_id):
    prise = get_object_or_404(Prise, id=prise_id)

    if request.method == "POST":
        heure_on = request.POST.get("heure_on")
        heure_off = request.POST.get("heure_off")

        if not heure_on or not heure_off:
            messages.error(request, "Veuillez renseigner les deux heures.")
            return redirect('page_accueil')

        try:
            h_on = datetime.strptime(heure_on, "%H:%M").time()
            h_off = datetime.strptime(heure_off, "%H:%M").time()
        except ValueError:
            messages.error(request, "Format d'heure invalide.")
            return redirect('page_accueil')

        # Sauvegarde en base
        prise.heure_on = h_on
        prise.heure_off = h_off
        prise.horaire_active = True
        prise.save()

        messages.success(request, f"Plage horaire enregistrée : de {heure_on} à {heure_off}.")

    return redirect('page_accueil')



def toggle_horaire(request, prise_id):
    prise = get_object_or_404(Prise, id=prise_id)
    if request.method == "POST":
        prise.horaire_active = not prise.horaire_active
        prise.save()
        if prise.horaire_active:
            messages.success(request, "Plage horaire activée.")
            # si on l'active, appliquer l'état immédiatement si heures définies
            if prise.heure_on and prise.heure_off:
                now = timezone.localtime().time()
                should_be_on = is_now_in_range(now, prise.heure_on, prise.heure_off)
                if prise.etat != should_be_on:
                    prise.etat = should_be_on
                    prise.save()
                    envoyer_commande_prise(should_be_on)
        else:
            messages.info(request, "Plage horaire désactivée.")
    return redirect('page_accueil')




def debug_check_plages(request):
    # renvoie ce que ferait check_plages sans modifier quoi que ce soit
    from .tache_horaire import check_plages
    result = check_plages(return_changes=True)
    return JsonResponse(result or {"now": "unknown", "changes": []})


def panneau_temperature(request):
    temp = Temperature.objects.first()  # ou get(pk=1)
    return render(request, "prises/panneau_temperature.html", {"temperature": temp.value if temp else "--"})
from django.http import JsonResponse

def temperature_api(request):
    temp_obj = Temperature.objects.first()
    temperature = temp_obj.value if temp_obj else "--"
    return JsonResponse({'temperature': temperature})
