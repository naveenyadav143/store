from django.test import TestCase
from django.urls import reverse
from .models import Store, Product

class StoreModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            store_name="Test Store",
            address="123 Test St",
            owner_name="Owner",
            contact_number="1234567890"
        )

    def test_store_str(self):
        self.assertEqual(str(self.store), "Test Store")

class ProductModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            store_name="Test Store",
            address="123 Test St",
            owner_name="Owner",
            contact_number="1234567890"
        )
        self.product = Product.objects.create(
            store=self.store,
            name="Test Product",
            price=9.99,
            quantity=10
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")

class HomeViewTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            store_name="Test Store",
            address="123 Test St",
            owner_name="Owner",
            contact_number="1234567890"
        )

    def test_home_view_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_context(self):
        response = self.client.get(reverse('home'))
        self.assertIn('stores', response.context)
        self.assertIn('selected_store', response.context)
        self.assertIn('products', response.context)
