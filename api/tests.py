from django.test import TestCase,Client
from api.models import *
from api.serializers import *
from datetime import datetime
# Create your tests here.

class test1(TestCase):

	def setUp(self):
		add1 = address.objects.create(street="street name",city="city",state="state",postal_code = 10000)
		q1 = qualification.objects.create(name="name of institute",year_of_passing=2000,percentage = 80.9)
		b1 = bank.objects.create(account_no="account_no",bank_name="bank name",ifsc_code="ifsc00000")
		e1 = past_job_experience.objects.create(company_name="company name",job_role="role",duration=2)
		u1 = user.objects.create_user(username="aadhar_no",password="password",is_staff=True)
		a1 = aadhar.objects.create(aadhar_no="aadhar_no",is_active=True)
		dob1 = datetime(2000,10,22)
		pd1 = personal_detail.objects.create(full_name="full name",date_of_birth=dob1,blood_group="B-",user=u1,aadhar=a1)
		pd1.bank.add(b1)
		pd1.address.add(add1)
		pd1.qualification.add(q1)
		pd1.past_job_experience.add(e1)
		pd1.save()

	def test_login_signup(self):
		cl = Client()
		self.assertTrue(cl.post('/register',{'aadhar_no':'new_aadhar','password':'password','full_name':'new user','blood_group':'O+','dob':'2001-10-10'},content_type="application/json").json()['success'])
		self.assertEqual(len(personal_detail.objects.all()),2)
		self.assertEqual(len(user.objects.all()),2)
		self.assertEqual(len(aadhar.objects.all()),2)
		self.assertFalse(aadhar.objects.get(aadhar_no="new_aadhar").is_active)
		self.assertTrue(cl.post('/activate/new_aadhar').json()['success'])
		self.assertTrue(aadhar.objects.get(aadhar_no="new_aadhar").is_active)
		self.assertTrue(cl.post('/login',{'aadhar_no':'new_aadhar','password':'password'},content_type='application/json').json()['success'])


	def test_add_contact_info(self):
		cl = Client()
		self.assertFalse(cl.post('/aadhar_no/add',{"email":"a@example.com"},content_type='application/json').json()['success'])
		cl.cookies['auth'] = cl.post('/login',{'aadhar_no':'aadhar_no','password':'password'},content_type='application/json').json()['content']
		self.assertTrue(cl.post('/aadhar_no/add',{"email":"a@example.com"},content_type='application/json').json()['success'])
		self.assertTrue(cl.post('/aadhar_no/add',{"contact_no":"1234567890"},content_type='application/json').json()['success'])
		self.assertEqual(len(personal_detail.objects.all()[0].contact_no),1)
		self.assertEqual(len(personal_detail.objects.all()[0].email),1)

	def test_each(self):
		cl = Client()
		cl.cookies['auth'] = cl.post('/login',{'aadhar_no':'aadhar_no','password':'password'},content_type='application/json').json()['content']
		self.assertEqual(cl.get('/aadhar_no',content_type="application/json").json()['content'],personal_detail_ser(personal_detail.objects.all()[0]).data)
		cl.put('/aadhar_no',{"full_name":"nikhil"},content_type="application/json").json()['content']
		self.assertEqual(personal_detail_ser(personal_detail.objects.all()[0]).data["full_name"],"nikhil")
		
		self.assertTrue(cl.delete('/aadhar_no',content_type="application/json").json()['success'])
		self.assertEqual(len(personal_detail.objects.all()),0)


	def test_address(self):
		cl = Client()
		cl.cookies['auth'] = cl.post('/login',{'aadhar_no':'aadhar_no','password':'password'},content_type='application/json').json()['content']
		self.assertEqual(cl.get('/aadhar_no/address').json()['content'],personal_detail_ser(personal_detail.objects.all()[0]).data['address'])
		self.assertTrue(cl.put('/aadhar_no/address/1',{"street":"mine"},content_type='application/json').json()['success'])
		self.assertEqual(cl.get('/aadhar_no/address').json()['content'][0]['street'],"mine")
		self.assertTrue(cl.delete('/aadhar_no/address/1').json()['success'])
		self.assertEqual(len(address.objects.all()),0)

	def test_qualification(self):
		cl = Client()
		cl.cookies['auth'] = cl.post('/login',{'aadhar_no':'aadhar_no','password':'password'},content_type='application/json').json()['content']
		self.assertEqual(cl.get('/aadhar_no/qualification').json()['content'],personal_detail_ser(personal_detail.objects.all()[0]).data['qualification'])
		self.assertTrue(cl.put('/aadhar_no/qualification/1',{"name":"mine"},content_type='application/json').json()['success'])
		self.assertEqual(cl.get('/aadhar_no/qualification').json()['content'][0]['name'],"mine")
		self.assertTrue(cl.delete('/aadhar_no/qualification/1').json()['success'])
		self.assertEqual(len(qualification.objects.all()),0)

	def test_bank(self):
		cl = Client()
		cl.cookies['auth'] = cl.post('/login',{'aadhar_no':'aadhar_no','password':'password'},content_type='application/json').json()['content']
		self.assertEqual(cl.get('/aadhar_no/bank').json()['content'],personal_detail_ser(personal_detail.objects.all()[0]).data['bank'])
		self.assertTrue(cl.put('/aadhar_no/bank/1',{"bank_name":"mine"},content_type='application/json').json()['success'])
		self.assertEqual(cl.get('/aadhar_no/bank').json()['content'][0]['bank_name'],"mine")
		self.assertTrue(cl.delete('/aadhar_no/bank/1').json()['success'])
		self.assertEqual(len(bank.objects.all()),0)

	def test_experience(self):
		cl = Client()
		cl.cookies['auth'] = cl.post('/login',{'aadhar_no':'aadhar_no','password':'password'},content_type='application/json').json()['content']
		self.assertEqual(cl.get('/aadhar_no/experience').json()['content'],personal_detail_ser(personal_detail.objects.all()[0]).data['past_job_experience'])
		self.assertTrue(cl.put('/aadhar_no/experience/1',{"company_name":"mine"},content_type='application/json').json()['success'])
		self.assertEqual(cl.get('/aadhar_no/experience').json()['content'][0]['company_name'],"mine")
		self.assertTrue(cl.delete('/aadhar_no/experience/1').json()['success'])
		self.assertEqual(len(past_job_experience.objects.all()),0)
		
