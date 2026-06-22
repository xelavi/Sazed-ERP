# providers/models.py
#
# El model Provider ha estat fusionat amb customers.Customer.
# Un proveïdor és un Customer amb is_supplier=True.
# Totes les vistes d'aquest app filtren Customer(is_supplier=True).
