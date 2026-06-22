from accounts.models import User, Message, Company, Membership, Invitation, Notification

def main():
    try:
        alex = User.objects.get(email="alexvinent@sazed.com")
    except User.DoesNotExist:
        print("ERROR: User alexvinent@sazed.com not found!")
        return

    # Empresa principal d'en Àlex
    sazed = Company.objects.get(name="Sazed")

    # Companys reals de l'empresa Sazed
    laia = User.objects.get(email="laia.martinez@sazed.com")
    joan = User.objects.get(email="joan.vila@sazed.com")
    carlos = User.objects.get(email="carlos.ruiz@sazed.com")
    marta = User.objects.get(email="marta.soler@sazed.com")

    # --- 1. Eliminar missatges i invitacions anteriors de demo ---
    Message.objects.filter(recipient=alex).delete()
    Invitation.objects.filter(invitee=alex).delete()
    Notification.objects.filter(recipient=alex).delete()

    # --- 2. Missatges de tipus correu ---

    # Missatge 1: De la Laia (editora), seguiment d'una reunió
    Message.objects.create(
        sender=laia,
        recipient=alex,
        company=sazed,
        subject="Seguiment reunió — Onboarding Tecnologia Verd S.L.",
        body=(
            "Hola Àlex,\n\n"
            "Et faig el seguiment de la reunió d'ahir amb el client Tecnologia Verd S.L. "
            "Han confirmat que volen activar els mòduls de Facturació i Pressupostos "
            "a partir del proper dilluns.\n\n"
            "He preparat el document d'onboarding i l'he deixat al Drive compartit. "
            "Pots donar-hi un cop d'ull i validar els rols assignats? "
            "Necessiten que l'admin sigui en Jordi Puig (jordi.puig@tecverd.cat).\n\n"
            "Gràcies,\n"
            "Laia Martínez\n"
            "Departament de Comptes — Sazed"
        ),
        read=False
    )

    # Missatge 2: De Joan Vila (admin), urgent sobre una factura
    Message.objects.create(
        sender=joan,
        recipient=alex,
        company=sazed,
        subject="[URGENT] Factura FAC-2026-0087 — Error import IVA",
        body=(
            "Bon dia Àlex,\n\n"
            "Hem detectat un error a la factura FAC-2026-0087 emesa a Distribucions Mas Dorca, S.L. "
            "El tipus d'IVA aplicat és del 10% quan hauria de ser del 21%. "
            "La factura ja s'ha enviat al client però encara no han fet el pagament, "
            "de manera que estaria a temps de rectificar-la i emetre'n una de nova.\n\n"
            "Necessito que ho revisis avui si és possible per evitar problemes de comptabilitat "
            "al tancament del mes.\n\n"
            "Quedo a la teva disposició.\n\n"
            "Joan Vila\n"
            "Administrador — Sazed"
        ),
        read=False
    )

    # Missatge 3: De Carlos Ruiz, sobre un nou proveïdor
    Message.objects.create(
        sender=carlos,
        recipient=alex,
        company=sazed,
        subject="Proposta nou proveïdor: Papelera del Besòs",
        body=(
            "Hola Àlex,\n\n"
            "He estat en contacte amb un nou proveïdor de material d'oficina, "
            "Papelera del Besòs, i sembla que ofereixen millors condicions que el nostre proveïdor actual. "
            "He demanat el catàleg i una proposta econòmica.\n\n"
            "La proposta inclou:\n"
            "  - 15% de descompte en comandes superiors a 500€\n"
            "  - Lliurament en 24h a la zona metropolitana de Barcelona\n"
            "  - Gestor de compte dedicat\n\n"
            "T'ho passo quan el tingui per si vols valorar-ho.\n\n"
            "Salutacions,\n"
            "Carlos Ruiz\n"
            "Equip Operacions — Sazed"
        ),
        read=True  # ja llegit
    )

    # Missatge 4: De Marta Soler, recordatori intern
    Message.objects.create(
        sender=marta,
        recipient=alex,
        company=sazed,
        subject="Recordatori: Validació inventari Q2 (termini 13/06)",
        body=(
            "Hola Àlex,\n\n"
            "Et recordo que el termini per validar l'inventari del segon trimestre és el "
            "proper divendres 13 de juny.\n\n"
            "Pendent de la teva aprovació:\n"
            "  - Ajust estoc referència SKU-4421 (Rotlle tèrmic 80x80)\n"
            "  - Baixa d'articles obsolets (15 referències)\n"
            "  - Entrada de mercaderia del 3/06 (albarà #4892)\n\n"
            "Si necessites qualsevol aclariment, truca'm o escriu-me.\n\n"
            "Gràcies,\n"
            "Marta Soler\n"
            "Logística i Magatzem — Sazed"
        ),
        read=False
    )

    # --- 3. Invitació real d'una empresa real ---
    # Joan Vila (admin de Sazed) convida en Àlex a l'empresa Aeris
    aeris = Company.objects.get(name="Aeris")
    aeris_owner = User.objects.get(email="xelavi123@gmail.com")

    # Assegurem que en Joan no és membre d'Aeris (l'invitant ha de ser membre, usem el propietari)
    Invitation.objects.create(
        company=aeris,
        inviter=aeris_owner,
        invitee=alex,
        role='admin',
        status='pending'
    )

    # --- 4. Notificació del sistema ---
    Notification.objects.create(
        recipient=alex,
        kind='alert',
        title="Manteniment programat: divendres 13 de juny a les 02:00 h",
        body=(
            "La plataforma Sazed estarà en manteniment el divendres 13 de juny "
            "de 02:00 a 04:00 h. Durant aquest temps, l'accés pot quedar interromput. "
            "Si tens alguna tasca urgent, et recomanem completar-la abans d'aquesta franja."
        ),
        read=False
    )

    Notification.objects.create(
        recipient=alex,
        kind='activity',
        title="Marta Soler ha actualitzat l'inventari",
        body="S'han realitzat 3 ajustos d'estoc al magatzem central. Revisa el registre d'activitat per veure els detalls.",
        read=True
    )

    print("Dades de demo creades correctament!")
    print(f"  Missatges rebuts: {Message.objects.filter(recipient=alex).count()}")
    print(f"  Invitacions pendents: {Invitation.objects.filter(invitee=alex, status='pending').count()}")
    print(f"  Notificacions: {Notification.objects.filter(recipient=alex).count()}")

if __name__ == "__main__":
    main()
