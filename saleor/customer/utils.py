from .models import AddressBook
from ..userprofile.models import Address

def store_user_address(customer, address, billing=False, shipping=False):
    data = AddressBook.objects.as_data(address)
    entry = customer.addresses.get_or_create(**data)[0]
    changed = False
    if billing and not customer.default_billing_address_id:
        customer.default_billing_address = entry
        changed = True
    if shipping and not customer.default_shipping_address_id:
        customer.default_shipping_address = entry
        changed = True
    if changed:
        customer.save()
    return entry
