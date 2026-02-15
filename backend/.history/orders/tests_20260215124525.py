from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from accounts.models import User
from pharmacy.models import Product, Category
from labs.models import LabResult
from consultations.models import Diagnosis

class CareNovaIntegrationTest(APITestCase):
    def setUp(self):
        # 1. Setup Category and Restricted Product
        self.category = Category.objects.create(name="Antibiotics", slug="antibiotics")
        self.medicine = Product.objects.create(
            name="Amoxicillin",
            category=self.category,
            price=Decimal("50.00"),
            stock=10,
            requires_prescription=True
        )

        
        self.patient = User.objects.create_user(email="patient@test.com", username="patient", password="password123", role="PATIENT", balance=Decimal("100.00"))
        self.doctor = User.objects.create_user(email="doctor@test.com", username="doctor", password="password123", role="DOCTOR")

    def test_complete_medical_to_purchase_flow(self):
        
        self.client.force_authenticate(user=self.patient)
        order_data = {"items": [{"product_id": self.medicine.id, "quantity": 1}]}
        response = self.client.post(reverse('checkout'), order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("prescription", response.data['error'].lower())

        
        lab = LabResult.objects.create(patient=self.patient, title="Blood Test")

       
        self.client.force_authenticate(user=self.doctor)
        diagnosis = Diagnosis.objects.create(
            doctor=self.doctor, 
            patient=self.patient, 
            lab_result=lab, 
            medical_opinion="Infection detected"
        )
       
        
        from consultations.models import Prescription
        Prescription.objects.create(diagnosis=diagnosis, medicine_name="Amoxicillin", dosage="500mg")

        
        self.client.force_authenticate(user=self.patient)
        response = self.client.post(reverse('checkout'), order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.balance, Decimal("50.00")) 
        
       
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.stock, 9)