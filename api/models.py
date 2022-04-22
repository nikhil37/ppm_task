from django.db import models
from django.contrib.auth.models import AbstractUser
from json import dumps

# Create your models here.

class user(AbstractUser):
	pass

class aadhar(models.Model):
	a_id = models.AutoField(primary_key=True)
	aadhar_no = models.CharField(max_length=12,unique=True)
	is_active = models.BooleanField(default=False)

class address(models.Model): # multiple for each user
	a_id = models.AutoField(primary_key=True)
	street = models.CharField(max_length=150)
	city = models.CharField(max_length=30)
	state = models.CharField(max_length=30)
	postal_code = models.IntegerField()

class qualification(models.Model): # multiple for each user
	q_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=500)
	year_of_passing = models.IntegerField()
	percentage = models.FloatField()

class bank(models.Model): # multiple for each user
	b_id = models.AutoField(primary_key=True)
	account_no = models.CharField(max_length=50,unique=True)
	bank_name = models.CharField(max_length=200)
	ifsc_code = models.CharField(max_length=50)

class personal_detail(models.Model):
	pd_id = models.AutoField(primary_key=True)
	full_name = models.CharField(max_length=100)
	date_of_birth = models.DateField()
	blood_group =  models.CharField(max_length=5)
	contact_no = models.JSONField(default=list)
	email = models.JSONField(default=list)
	## Relations
	user = models.ForeignKey('user',on_delete=models.CASCADE)
	aadhar = models.ForeignKey('aadhar',on_delete=models.CASCADE)
	qualification = models.ManyToManyField('qualification',related_name='pd_qualification')
	address = models.ManyToManyField('address',related_name='pd_address')
	bank = models.ManyToManyField('bank',related_name='pd_bank')
	past_job_experience = models.ManyToManyField('past_job_experience',related_name='pd_past_job_experience')
	


class past_job_experience(models.Model): # multiple for each user
	p_id = models.AutoField(primary_key=True)
	company_name = models.CharField(max_length=200)
	job_role = models.CharField(max_length=100)
	duration = models.FloatField()
