from rest_framework import serializers
from api.models import *
from json import loads,dumps


class user_ser(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = '__all__'

class aadhar_ser(serializers.ModelSerializer):
    class Meta:
        model = aadhar
        fields = ["aadhar_no","is_active"]

class address_ser(serializers.ModelSerializer):
    class Meta:
        model = address
        fields = '__all__'#['street','city','state','postal_code']

class qualification_ser(serializers.ModelSerializer):
    class Meta:
        model = qualification
        fields = '__all__'#['name','year_of_passing','percentage']

class bank_ser(serializers.ModelSerializer):
    class Meta:
        model = bank
        fields = '__all__'#['account_no','bank_name','ifsc_code']

class past_job_experience_ser(serializers.ModelSerializer):
    class Meta:
        model = past_job_experience
        fields = '__all__'#['company_name','job_role','duration']

class personal_detail_ser(serializers.ModelSerializer):
    class Meta:
        model = personal_detail
        fields = ["full_name","date_of_birth","blood_group","contact_no","email","aadhar","qualification","address","bank","past_job_experience"]
        depth = 1
