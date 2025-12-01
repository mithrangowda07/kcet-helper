"""
Quick test script to test registration endpoint
Run: python manage.py shell < test_registration.py
Or: python manage.py shell, then copy-paste this code
"""

from students.serializers import StudentRegisterSerializer

# Test 1: Counselling student registration
print("=" * 50)
print("Test 1: Counselling Student Registration")
print("=" * 50)

counselling_data = {
    'type_of_student': 'counselling',
    'email_id': 'test_counselling@example.com',
    'phone_number': '1234567890',
    'password': 'password123',
    'password_confirm': 'password123',
    'kcet_rank': 5000,
}

serializer = StudentRegisterSerializer(data=counselling_data)
print(f"Valid: {serializer.is_valid()}")
if not serializer.is_valid():
    print(f"Errors: {serializer.errors}")
else:
    print("✓ Validation passed!")

# Test 2: Missing kcet_rank
print("\n" + "=" * 50)
print("Test 2: Missing KCET Rank")
print("=" * 50)

invalid_data = {
    'type_of_student': 'counselling',
    'email_id': 'test2@example.com',
    'phone_number': '1234567890',
    'password': 'password123',
    'password_confirm': 'password123',
}

serializer2 = StudentRegisterSerializer(data=invalid_data)
print(f"Valid: {serializer2.is_valid()}")
if not serializer2.is_valid():
    print(f"Errors: {serializer2.errors}")

# Test 3: Password mismatch
print("\n" + "=" * 50)
print("Test 3: Password Mismatch")
print("=" * 50)

password_mismatch = {
    'type_of_student': 'counselling',
    'email_id': 'test3@example.com',
    'phone_number': '1234567890',
    'password': 'password123',
    'password_confirm': 'different123',
    'kcet_rank': 5000,
}

serializer3 = StudentRegisterSerializer(data=password_mismatch)
print(f"Valid: {serializer3.is_valid()}")
if not serializer3.is_valid():
    print(f"Errors: {serializer3.errors}")

print("\n" + "=" * 50)
print("Testing Complete!")
print("=" * 50)

