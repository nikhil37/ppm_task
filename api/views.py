from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.conf import settings
import jwt,json,datetime
from api.serializers import *

def login_check(view_func):
	def check(request, *args, **kwargs):
		try:
			j = jwt.decode(request.COOKIES['auth'],key=settings.JWT_KEY,algorithms='HS256')
		except jwt.exceptions.DecodeError:
			return JsonResponse({'success':False,'content':"Invalid cookie."},status=403)
		except KeyError:
			return JsonResponse({'success':False,'content':'Not logged in.'},status=403)
		if request.method != "GET" and j['is_manager'] is False:
			return JsonResponse({'success':False,'content':'Not allowed'},status=403)
		return view_func(request, *args, **kwargs)
	return check


@login_check
@csrf_exempt
def add_contact(request,aadhar_no):
	if request.method == "POST":
		try:
			bd = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		if "email" in bd.keys():
			aadhar_no = jwt.decode(request.COOKIES['auth'],key=settings.JWT_KEY,algorithms='HS256')['aadhar_no']
			a1 = aadhar.objects.get(aadhar_no=aadhar_no)
			u1 = personal_detail.objects.get(aadhar=a1)
			u1.email.append(bd['email'])
			u1.save()
			return JsonResponse({'success':True,'content':'Added.'})
		elif "contact_no" in bd.keys():
			aadhar_no = jwt.decode(request.COOKIES['auth'],key=settings.JWT_KEY,algorithms='HS256')['aadhar_no']
			a1 = aadhar.objects.get(aadhar_no=aadhar_no)
			u1 = personal_detail.objects.get(aadhar=a1)
			u1.contact_no.append(bd['contact_no'])
			u1.save()
			return JsonResponse({'success':True,'content':'Added.'})
		else:
			return JsonResponse({'success':False,'content':'Invalid parameter'})
	return JsonResponse({'success':False,'content':'Only post allowed'})


@csrf_exempt
def signup(request):
	if request.method == "POST":
		try:
			try:
				bd = json.loads(request.body)
			except:
				return JsonResponse({'success':False,'content':'Bad request'},status=400)
			if 'is_manager' in bd.keys():
				u1 = user.objects.create_user(username=bd['aadhar_no'],password=bd['password'],is_staff=True)
			else:
				u1 = user.objects.create_user(username=bd['aadhar_no'],password=bd['password'],is_staff=False)
			a1 = aadhar.objects.create(aadhar_no=bd['aadhar_no'])
			d = datetime.datetime(int(bd['dob'].split('-')[0]),int(bd['dob'].split('-')[1]),int(bd['dob'].split('-')[2]))
			pd1 = personal_detail.objects.create(full_name=bd['full_name'],date_of_birth = d, blood_group = bd['blood_group'],user=u1,aadhar=a1)
			return JsonResponse({'success':True,'content':'Registered.'})
		except KeyError as e:
			return JsonResponse({'success':False,'content':'Required field: '+str(e).split(' ')[-1]})
	return JsonResponse({'success':False,'content':'Only post allowed'})

@csrf_exempt
def signin(request):
	if request.method == "POST":
		try:
			bd = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		ut = authenticate(username = bd['aadhar_no'],password=bd['password'])
		if ut is not None:
			request.COOKIES['auth'] = jwt.encode({"logged_in":True,"is_manager":ut.is_staff,'aadhar_no':bd['aadhar_no']},key=settings.JWT_KEY,algorithm='HS256')
			return JsonResponse({'success':True,'content':jwt.encode({"logged_in":True,"is_manager":ut.is_staff,'aadhar_no':bd['aadhar_no']},key=settings.JWT_KEY,algorithm='HS256')})
		return JsonResponse({'success':False,'content':'Invalid credentials'})
	return JsonResponse({'success':False,'content':'Only POST allowed'})

@csrf_exempt
@login_check
def index(request):
	if "filter" in request.GET.keys() and "id" in request.GET.keys():
		if request.GET['filter'] == "qualification":
			objs = personal_detail.objects.filter(qualification__in=[request.GET['filter']])
		elif request.GET['filter'] == "address":
			objs = personal_detail.objects.filter(address__in=[request.GET['filter']])
		elif request.GET['filter'] == "bank":
			objs = personal_detail.objects.filter(bank_in=[request.GET['filter']])
		elif request.GET['filter'] == "experience":
			objs = personal_detail.objects.filter(past_job_experience__in=[request.GET['filter']])
		else:
			return JsonResponse({'success':False,'content':'Invalid filter'})
	else:
		objs = personal_detail.objects.all()
	if 'sort' in request.GET.keys():
		objs.order_by(request.GET['sort'])
	if 'aadhar-status' in request.GET.keys():
		if request.GET['aadhar-status'] == 'true':
			objs.filter(aadhar__is_active=True)
		elif request.GET['aadhar-status'] == 'false':
			objs.filter(aadhar__is_active=False)
		else:
			return JsonResponse({'success':True,'content':' Invalid parameter'})
	return JsonResponse({'success':True,'content':personal_detail_ser(objs,many=True).data})
	

def activate(request,aadhar_no):
	c = aadhar.objects.get(aadhar_no=aadhar_no)
	c.is_active = True
	c.save()
	return JsonResponse({'success':True,'content':'Activated'})

@csrf_exempt
@login_check
def each(request,aadhar_no):
	try:
		aadhar_obj = aadhar.objects.get(aadhar_no=aadhar_no)
	except aadhar.DoesNotExist:
		return JsonResponse({'success':False,'content':'Invalid aadhar number.'})
	person_det=personal_detail.objects.get(aadhar=aadhar_obj)
	
	if request.method == "GET":		# View
		a = personal_detail_ser(person_det,many=False).data
		return JsonResponse({'success':True,'content':a})
	
	elif request.method == "PUT":	# Update
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		for i in b:
			try:
				getattr(person_det,i)
				setattr(person_det,i,b[i])
			except AttributeError:
				return JsonResponse({'success':False,'content':"Invalid parameter."})
		person_det.save()
		return JsonResponse({'success':True,'content':'Updated'})
	elif request.method == "DELETE":
		person_det.delete()
		return JsonResponse({'success':True,'content':'Deleted'})

@csrf_exempt
@login_check
def address_view(request,aadhar_no,obj_id=None):
	try:
		aadhar_obj = aadhar.objects.get(aadhar_no=aadhar_no)
	except aadhar.DoesNotExist:
		return JsonResponse({'success':False,'content':'Invalid aadhar number.'})
	person_det=personal_detail.objects.get(aadhar=aadhar_obj)
	
	if request.method == "GET":			# View
		obj = person_det.address.all()
		return JsonResponse({'success':True,'content':address_ser(obj,many=True).data})

	
	elif request.method == "POST":		# Create
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		try:
			obj = address.objects.create(**b)
		except TypeError as e:
			return JsonResponse({'success':False,'content':f'Invalid parameter {str(e).split(" ")[-1]}'})
		person_det.address.add(obj)
		person_det.save()
		return JsonResponse({'success':True,'content':'Added'})
	
	elif request.method == "PUT":		# Update
		try:
			obj = person_det.address.get(a_id=obj_id)
		except address.DoesNotExist:
			return JsonResponse({'success':False,'content':"'id' needed"})
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		for i in b:
			try:
				getattr(obj,i)
				setattr(obj,i,b[i])
			except AttributeError:
				return JsonResponse({'success':False,'content':"Invalid parameter."})
		obj.save()
		return JsonResponse({'success':True,'content':'Updated'})
	
	elif request.method == "DELETE":	# Delete
		try:
			obj = person_det.address.get(a_id=obj_id)
			obj.delete()
		except address.DoesNotExist:
			return JsonResponse({'success':False,'content':"'id' required"})
		return JsonResponse({'success':True,'content':'Deleted'})
	return JsonResponse({"try":True})

@csrf_exempt
@login_check
def qualification_view(request,aadhar_no,obj_id=None):
	try:
		aadhar_obj = aadhar.objects.get(aadhar_no=aadhar_no)
	except aadhar.DoesNotExist:
		return JsonResponse({'success':False,'content':'Invalid aadhar number.'})
	person_det=personal_detail.objects.get(aadhar=aadhar_obj)
	
	if request.method == "GET":			# View
		obj = person_det.qualification.all()
		return JsonResponse({'success':True,'content':qualification_ser(obj,many=True).data})

	
	elif request.method == "POST":		# Create
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		try:
			obj = qualification.objects.create(**b)
		except TypeError as e:
			return JsonResponse({'success':False,'content':f'Invalid parameter {str(e).split(" ")[-1]}'})
		person_det.qualification.add(obj)
		person_det.save()
		return JsonResponse({'success':True,'content':'Added'})
	
	elif request.method == "PUT":		# Update
		obj = person_det.qualification.get(q_id=obj_id)
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		for i in b:
			try:
				getattr(obj,i)
				setattr(obj,i,b[i])
			except AttributeError:
				return JsonResponse({'success':False,'content':"Invalid parameter."})
		obj.save()
		return JsonResponse({'success':True,'content':'Updated'})
	
	elif request.method == "DELETE":	# Delete
		try:
			obj = person_det.qualification.get(q_id=obj_id)
			obj.delete()
		except qualification.DoesNotExist:
			return JsonResponse({'success':False,'content':"'id' required"})
		return JsonResponse({'success':True,'content':'Deleted'})
	

@csrf_exempt
@login_check
def bank_view(request,aadhar_no,obj_id=None):
	try:
		aadhar_obj = aadhar.objects.get(aadhar_no=aadhar_no)
	except aadhar.DoesNotExist:
		return JsonResponse({'success':False,'content':'Invalid aadhar number.'})
	person_det=personal_detail.objects.get(aadhar=aadhar_obj)
	
	if request.method == "GET":			# View
		obj = person_det.bank.all()
		return JsonResponse({'success':True,'content':bank_ser(obj,many=True).data})

	
	elif request.method == "POST":		# Create
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		try:
			obj = bank.objects.create(**b)
		except TypeError as e:
			return JsonResponse({'success':False,'content':f'Invalid parameter {str(e).split(" ")[-1]}'})
		person_det.bank.add(obj)
		person_det.save()
		return JsonResponse({'success':True,'content':'Added'})
	
	elif request.method == "PUT":		# Update
		obj = person_det.bank.get(b_id=obj_id)
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		for i in b:
			try:
				getattr(obj,i)
				setattr(obj,i,b[i])
			except AttributeError:
				return JsonResponse({'success':False,'content':"Invalid parameter."})
		obj.save()
		return JsonResponse({'success':True,'content':'Updated'})
	
	elif request.method == "DELETE":	# Delete
		try:
			obj = person_det.bank.get(b_id=obj_id)
			obj.delete()
		except bank.DoesNotExist:
			return JsonResponse({'success':False,'content':"'id' required"})
		return JsonResponse({'success':True,'content':'Deleted'})
	

@csrf_exempt
@login_check
def experience_view(request,aadhar_no,obj_id=None):
	try:
		aadhar_obj = aadhar.objects.get(aadhar_no=aadhar_no)
	except aadhar.DoesNotExist:
		return JsonResponse({'success':False,'content':'Invalid aadhar number.'})
	person_det=personal_detail.objects.get(aadhar=aadhar_obj)
	
	if request.method == "GET":			# View
		obj = person_det.past_job_experience.all()
		return JsonResponse({'success':True,'content':past_job_experience_ser(obj,many=True).data})

	
	elif request.method == "POST":		# Create
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		try:
			obj = past_job_experience.objects.create(**b)
		except TypeError as e:
			return JsonResponse({'success':False,'content':f'Invalid parameter {str(e).split(" ")[-1]}'})
		person_det.past_job_experience.add(obj)
		person_det.save()
		return JsonResponse({'success':True,'content':'Added'})
	
	elif request.method == "PUT":		# Update
		obj = person_det.past_job_experience.get(p_id=obj_id)
		try:
			b = json.loads(request.body)
		except:
			return JsonResponse({'success':False,'content':'Bad request'},status=400)
		for i in b:
			try:
				getattr(obj,i)
				setattr(obj,i,b[i])
			except AttributeError:
				return JsonResponse({'success':False,'content':"Invalid parameter."})
		obj.save()
		return JsonResponse({'success':True,'content':'Updated'})
	
	elif request.method == "DELETE":	# Delete
		try:
			obj = person_det.past_job_experience.get(p_id=obj_id)
			obj.delete()
		except past_job_experience.DoesNotExist:
			return JsonResponse({'success':False,'content':"'id' required"})
		return JsonResponse({'success':True,'content':'Deleted'})
	
