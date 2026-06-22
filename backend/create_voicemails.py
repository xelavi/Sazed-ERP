
from accounts.models import User, Message, Company, Membership, Notification

def main():
    try:
        recipient = User.objects.get(email="alexvinent@sazed.com")
    except User.DoesNotExist:
        print("User alexvinent@sazed.com not found!")
        return

    # Try to find the company of the user
    memberships = Membership.objects.filter(user=recipient)
    if not memberships.exists():
        print("User has no company memberships.")
        company = Company.objects.first()
        if not company:
            company = Company.objects.create(name="Sazed", slug="sazed")
        Membership.objects.create(user=recipient, company=company, role='owner')
    else:
        company = memberships.first().company

    # Create dummy sender users if there are none
    sender1, _ = User.objects.get_or_create(email="laia.martinez@sazed.com", defaults={"first_name": "Laia", "last_name": "Martínez"})
    Membership.objects.get_or_create(user=sender1, company=company, defaults={"role": "editor"})

    sender2, _ = User.objects.get_or_create(email="joan.vila@sazed.com", defaults={"first_name": "Joan", "last_name": "Vila"})
    Membership.objects.get_or_create(user=sender2, company=company, defaults={"role": "admin"})

    # Create Voicemails
    m1 = Message.objects.create(
        sender=sender1,
        recipient=recipient,
        company=company,
        subject="📞 Nou missatge de veu de Laia Martínez (0:45)",
        body="Hola Àlex, sóc la Laia. Et trucava per confirmar si la presentació dels nous mòduls està a punt per a la reunió de demà. Truca'm quan puguis, si us plau.\n\n▶ [Reproduir missatge de veu]",
        read=False
    )
    
    m2 = Message.objects.create(
        sender=sender2,
        recipient=recipient,
        company=company,
        subject="📞 Nou missatge de veu de Joan Vila (1:12)",
        body="Bon dia Àlex. He revisat els pressupostos del client X i hi ha algunes discrepàncies que hauríem de comentar abans d'enviar-los. Quan tinguis un forat, en parlem.\n\n▶ [Reproduir missatge de veu]",
        read=False
    )

    # Create his own message (voicemail to himself / general notice)
    m3 = Message.objects.create(
        sender=recipient,
        recipient=recipient,
        company=company,
        subject="📝 Nota de veu personal (0:15)",
        body="Recordatori: Revisar les mètriques d'activitat de la bústia i verificar que tot el disseny està correcte per a la demo.\n\n▶ [Reproduir missatge de veu]",
        read=False
    )
    
    # Create some general notifications
    Notification.objects.create(
        recipient=recipient,
        kind='alert',
        title="Actualització del sistema programada",
        body="Tindrem una aturada de manteniment aquesta nit a les 02:00 h per actualitzar la plataforma.",
        read=False
    )

    print("Created voicemails and notifications successfully.")

if __name__ == "__main__":
    main()
