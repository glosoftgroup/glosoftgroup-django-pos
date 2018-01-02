from __future__ import absolute_import
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from ...orders.models import Orders
import json

# initialize the APIClient app
client = APIClient()


class CreateOrderTest(TestCase):
    """ Test module for updating order record """

    def setUp(self):
        self.casper = Orders.objects.get(pk=62)
        self.muffin = Orders.objects.get(pk=62)
        self.valid_payload = {
            "id": 62,
            "invoice_number": "RET#kampya",
            "total_net": "223.29",
            "sub_total": "223.29",
            "balance": "223.29",
            "terminal": 1,
            "amount_paid": "0.00",
            "status": "payment-pending",
            "total_tax": "0.00",
            "discount_amount": "0.00",
            "debt": "223.29",
            "ordered_items": [
                {
                    "id": 201,
                    "sale_point": 1,
                    "sku": "2-1337",
                    "quantity": 1,
                    "unit_cost": "99.88",
                    "total_cost": "99.88",
                    "product_name": "Davis-Wilson (Box Size: 1kg)",
                    "product_category": "Groceries",
                    "tax": 0,
                    "discount": "0.00"
                },
                {
                    "id": 200,
                    "sale_point": 1,
                    "sku": "2-1338",
                    "quantity": 1,
                    "unit_cost": "87.79",
                    "total_cost": "87.79",
                    "product_name": "Davis-Wilson (Box Size: 500g)",
                    "product_category": "Groceries",
                    "tax": 0,
                    "discount": "0.00"
                },
                {
                    "id": 199,
                    "sale_point": 1,
                    "sku": "2-1340",
                    "quantity": 1,
                    "unit_cost": "35.62",
                    "total_cost": "35.62",
                    "product_name": "Davis-Wilson (Box Size: 100g)",
                    "product_category": "Groceries",
                    "tax": 0,
                    "discount": "0.00"
                }
            ]
        }

        self.invalid_payload = {
            'name': '',
            'age': 4,
            'breed': 'Pamerion',
            'color': 'White'
        }

    def test_valid_update_order(self):
        response = client.put(
            reverse('update-order', kwargs={'pk': self.muffin.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_update_order(self):
        response = client.put(
            reverse('update-order', kwargs={'pk': self.muffin.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
