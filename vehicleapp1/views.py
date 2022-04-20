from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,UserChangeForm
from django.contrib.auth import login,logout
from django.contrib.auth.models import User
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.http import Http404
from django.utils import timezone
from django.template import loader

from .models import *
from .forms import *

import requests

from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string

from django.core.mail import send_mail
from django.core.mail import EmailMessage


def signup(request):
    if request.method=="POST":
        form=RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=RegistrationForm()
    return render(request,'account/signup.html',{'form' : form})


def loginView(request):
    if request.method == 'POST':
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('profile')
    else:
        form=AuthenticationForm()
    return render(request,'account/login.html',{'form': form})

def logoutView(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

def profileView(request):
    if request.user.is_authenticated:
        user=request.user
        print(user)
        print("Get")
        form=editForm(instance=user)
        args = { 'user' : request.user,'form' : form}
        print(form)
        return render(request,'account/profile.html',args)
    else:
        return redirect('pageNotFound')

def editView(request):
    if request.method == "POST":
        print("POST")
        form=editForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account:profile')

def bindex(request):
    if request.user.is_authenticated:
        form=BookForm()
        return render(request,'booking/index.html',{'form':form})
    else:
        return redirect('pageNotFound')

def pay(request):
    if request.user.is_authenticated:
        return render(request,'booking/payment.html')
    else:
        return redirect('pageNotFound')

def book(request):
    if request.POST:
        form=BookForm(request.POST)
        if form.is_valid():
            print('success')
            instance=form.save(commit=False)
            instance.allottedUser=request.user
            source=instance.source
            source=source.replace(" ","+")
            instance.source=source
            print(instance.source)
            destination=instance.destination
            destination=destination.replace(" ","+")
            instance.destination=destination
            print(instance.destination)
            url='https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins='+source +'&destinations='+destination+'&key=AIzaSyBKmBYERZyz9Cj7-F9bT7WMWVuSHiaX9kU';
            print(url)
            r = requests.get(url)
            results = r.json()
            instance.distance=int(results["rows"][0]["elements"][0]["distance"]["value"]/1000)
            instance.duration=results["rows"][0]["elements"][0]["duration"]["text"]
            print(instance.distance)
            print(instance.vehicle.cost_per_km)
            instance.cost=int(float(instance.vehicle.cost_per_km)*float(instance.distance))
            instance.save()
            print('success')
            success_message='Booking done. You will be informed once the booking is confirmed'
            return render(request,'booking/success.html',{'details': instance ,'success' : success_message})
    else:
        if request.user.is_authenticated:
            form=BookForm()
            error_message='Something went wrong error'
            return render(request,'booking/index.html',{ 'form' : form ,'error':error_message})
        else:
            return redirect('pageNotFound')

def booking(request):
    if request.POST:
        form=BookForm(request.POST)
        return render(request,'booking/index.html',{'form':form})
    else:
        if request.user.is_authenticated:
            bookings = Book.objects.all()
            for booking in bookings:
                if booking.status=="B" and timezone.now()>booking.endDate:
                    vehicle = booking.vehicle
                    vehicle.status="NB"
                    vehicle.save()
                    booking.status="E"
                    driver=booking.allottedDriver
                    booking.allottedDriver=None
                    driver.status="NB"
                    booking.save()
                    driver.save()
                elif booking.status=="NB" and timezone.now()>booking.endDate:
                    booking.status="E"
                    booking.save()
            if request.user.is_superuser:
                return render(request,'booking/bookinglist.html',{ 'bookings' : bookings ,'user':request.user})
            else:
                bookings = Book.objects.filter(allottedUser=request.user)
                return render(request,'booking/bookinglist.html',{ 'bookings' : bookings ,'user':request.user})
        else:
            return redirect('pageNotFound')

def bdelete(request,id):
    if request.POST:
        return render(request,'vehicle/index.html',{'form':form})
    else:
        if request.user.is_authenticated:
            booking = Book.objects.get(id=id)
            booking.delete()
            return redirect('http://localhost:8000/booking/bookings')
        else:
            return redirect('pageNotFound')

def mail(request,id):
    if request.POST:
        return render(request,'booking/index.html',{'form':form})
    else:
        if request.user.is_authenticated:
            booking = Book.objects.get(id=id)
            if booking.status == "B":
                vehicle = booking.vehicle
                vehicle.vehicle_status="NB"
                driver=booking.allottedDriver
                driver.status="NB"
                vehicle.save()
                driver.save()
                booking.status = "NB"
                booking.allottedDriver = None
                booking.save()
            else:
                drivers = Driver.objects.filter(status="NB")
                if drivers:
                    for driver in drivers:
                        vehicle = booking.vehicle
                        if vehicle.vehicle_status == "B":
                            failure_message="Vehicle already booked"
                            return redirect('http://localhost:8000/booking/bookings')
                        else:
                            booking.status = "B"
                            vehicle.vehicle_status="B"
                            vehicle.save()
                            booking.allottedDriver = driver
                            driver.status="B"
                            driver.save()
                            msg = EmailMessage(
                               'Your Booking Has Been Confirmed',
                               '<!DOCTYPE html><html><head><title></title><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="X-UA-Compatible" content="IE=edge"/><body style="margin: 0 !important; padding: 0 !important; background-color: #eeeeee;" bgcolor="#eeeeee"><div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: Open Sans, Helvetica, Arial, sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">Confirmation of your booking - RoadLink!</div><table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td align="center" style="background-color: #eeeeee;" bgcolor="#eeeeee"><!--[if (gte mso 9)|(IE)]> <table align="center" border="0" cellspacing="0" cellpadding="0" width="600"> <tr> <td align="center" valign="top" width="600"><![endif]--> <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;"> <tr> <td align="center" valign="top" style="font-size:0; padding: 35px;" bgcolor="#044767"><!--[if (gte mso 9)|(IE)]> <table align="center" border="0" cellspacing="0" cellpadding="0" width="600"> <tr> <td align="left" valign="top" width="300"><![endif]--> <div style="display:inline-block; max-width:50%; min-width:100px; vertical-align:top; width:100%;"> <table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:300px;"> <tr> <td align="left" valign="top" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 36px; font-weight: 800; line-height: 48px;" class="mobile-center"> <h1 style="font-size: 36px; font-weight: 800; margin: 0; color: #ffffff;">RoadLink</h1> </td></tr></table> </div><!--[if (gte mso 9)|(IE)]> </td><td align="right" width="300"><![endif]--> <div style="display:inline-block; max-width:50%; min-width:100px; vertical-align:top; width:100%;" class="mobile-hide"> <table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:300px;"> <tr> <td align="right" valign="top" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 48px; font-weight: 400; line-height: 48px;"> <table cellspacing="0" cellpadding="0" border="0" align="right"> <tr> <td style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 400;"> <p style="font-size: 18px; font-weight: 400; margin: 0; color: #ffffff;"></p></td><td style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 400; line-height: 24px;">  </td></tr></table> </td></tr></table> </div><!--[if (gte mso 9)|(IE)]> </td></tr></table><![endif]--> </td></tr><tr> <td align="center" style="padding: 35px 35px 20px 35px; background-color: #ffffff;" bgcolor="#ffffff"><!--[if (gte mso 9)|(IE)]> <table align="center" border="0" cellspacing="0" cellpadding="0" width="600"> <tr> <td align="center" valign="top" width="600"><![endif]--> <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;"> <tr> <td align="center" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding-top: 25px;"> <img src="https://goo.gl/fZqQ2F" width="125" height="120" style="display: block; border: 0px;"/><br><h2 style="font-size: 30px; font-weight: 800; line-height: 36px; color: #333333; margin: 0;"> Your Booking is Confirmed!<br><h2><h3><a href="http://localhost:8000/booking/bookings">See your Booking</a> </h3> </td></tr><tr> <td align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding-top: 10px;"> <p style="font-size: 16px; font-weight: 400; line-height: 24px; color: #777777;"> </p></td></tr><tr> <td align="left" style="padding-top: 20px;"> </td></tr><tr> <td align="left" style="padding-top: 20px;"> <table cellspacing="0" cellpadding="0" border="0" width="100%"> <tr> <td width="75%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px; border-top: 3px solid #eeeeee; border-bottom: 3px solid #eeeeee;"> TOTAL </td><td width="25%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px; border-top: 3px solid #eeeeee; border-bottom: 3px solid #eeeeee;"> Rs{}</td></tr></table> </td></tr></table><!--[if (gte mso 9)|(IE)]> </td></tr></table><![endif]--> </td></tr><tr> <td align="center" height="100%" valign="top" width="100%" style="padding: 0 35px 35px 35px; background-color: #ffffff;" bgcolor="#ffffff"><!--[if (gte mso 9)|(IE)]> <table align="center" border="0" cellspacing="0" cellpadding="0" width="600"> <tr> <td align="center" valign="top" width="600"><![endif]--> <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:660px;"> <tr> <td align="center" valign="top" style="font-size:0;"><!--[if (gte mso 9)|(IE)]> <table align="center" border="0" cellspacing="0" cellpadding="0" width="600"> <tr> <td align="left" valign="top" width="300"><![endif]--> <div style="display:inline-block; max-width:50%; min-width:240px; vertical-align:top; width:100%;"> </div><!--[if (gte mso 9)|(IE)]> </td><td align="left" valign="top" width="300"><![endif]--> <div style="display:inline-block; max-width:50%; min-width:240px; vertical-align:top; width:100%;"> <table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:300px;"> <tr> <td align="left" valign="top" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px;"> <p style="font-weight: 800;">Driver Details</p><p>Name :{}{}</p><p>Contact :{}</p></td></tr></table> </div><!--[if (gte mso 9)|(IE)]> </td></tr></table><![endif]--> </td></tr></table> </td></tr></table> </body></html>'.format(booking.cost,driver.firstName,driver.lastName,driver.phoneNumber),
                               'iit2016106@iiita.ac.in',
                               [booking.allottedUser.email],
                            )
                            msg.content_subtype = "html"
                            msg.send()
                        booking.save()
                        break
                else:
                    failure_message="No Drivers Available"
                    return redirect('http://localhost:8000/booking/bookings')
            return redirect('http://localhost:8000/booking/bookings')
        else:
            return redirect('pageNotFound')

def dindex(request):
    if request.user.is_authenticated:
        form=DriverForm()
        return render(request,'driver/index.html',{'form':form})
    else:
        return redirect('pageNotFound')

def driver(request):
    if request.POST:
        form=DriverForm(request.POST)
        if form.is_valid():
            form.save()
            success_message='Driver registered'
            form=DriverForm()
            return render(request,'driver/index.html',{'form':form,'success' : success_message})
    else:
        if request.user.is_authenticated:
            form=DriverForm()
            error_message='Something went wrong error'
            return render(request,'driver/index.html',{ 'form' : form ,'error':error_message})
        else:
            return redirect('pageNotFound')

def drivers(request):
    if request.POST:
        form=DriverForm(request.POST)
        return render(request,'driver/index.html',{'form':form})
    else:
        if request.user.is_authenticated:
            drivers = Driver.objects.all()
            return render(request,'driver/driverlist.html',{ 'drivers' : drivers ,'user':request.user})
        else:
            return redirect('pageNotFound')

def vdelete(request,id):
    if request.POST:
        return render(request,'driver/index.html',{'form':form})
    else:
        if request.user.is_authenticated:
            drivers = Driver.objects.get(id=id)
            drivers.delete()
            return redirect('http://localhost:8000/driver/drivers')
        else:
            return redirect('pageNotFound')

def edit(request,id):
    if request.method == "POST":
        driver=Driver.objects.get(id=id)
        form=DriverForm(request.POST,instance=driver)
        if form.is_valid():
            form.save()
            return redirect('http://localhost:8000/driver/drivers')
    elif request.user.is_authenticated:
        driver=Driver.objects.get(id=id)
        form=DriverForm(instance=driver)
        return render(request,'driver/driverEdit.html',{ 'form' : form ,'id':id})


def vindex(request):
    # if request.user.is_authenticated:
    form=VehicleForm()
    return render(request,'vehicle/index.html',{'form':form})
    # else:
    #     return redirect('pageNotFound')

def addVehicle(request):
    if request.POST:
        form=VehicleForm(request.POST,request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner=request.user
            instance.save()
            success_message='Adding done'
            form=VehicleForm()
            return render(request,'vehicle/index.html',{'form':form,'success' : success_message})
    else:
        if request.user.is_authenticated:
            form=VehicleForm()
            error_message='Something went wrong error'
            return render(request,'vehicle/index.html',{ 'form' : form ,'error':error_message})

def showVehicles(request):
    if request.method=='POST' and 'searchb' in request.POST:
        search_query = request.POST.get('search_box')
        vehiclesList = Vehicle.objects.filter(registration_plate=search_query)
        return render(request,'vehicle/vehiclelist.html',{ 'vehiclesList' : vehiclesList})
    elif request.method=='POST' and 'viewallb' in request.POST: 
        vehiclesList = Vehicle.objects.all()
        return render(request,'vehicle/vehiclelist.html',{ 'vehiclesList' : vehiclesList})
    else:
        if request.user.is_authenticated:
            if request.user.is_superuser:
                vehiclesList = Vehicle.objects.all()
            else:
                vehiclesList = Vehicle.objects.filter(owner=request.user)        
            return render(request,'vehicle/vehiclelist.html',{ 'vehiclesList' : vehiclesList})
        else:
            return redirect('pageNotFound')

def delete(request,id):
    if request.POST:

        return render(request,'vehicle/index.html',{'form':form,'user':request.user})
    else:
        if request.user.is_authenticated:
            vehicle = Vehicle.objects.get(id=id)
            vehicle.delete()
            return redirect('http://localhost:8000/vehicle/vehicles')
        else:
            return redirect('pageNotFound')

def vedit(request,id):
    if request.method == "POST":
        vehicle=Vehicle.objects.get(id=id)
        form=VehicleForm(request.POST,request.FILES,instance=vehicle)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('http://localhost:8000/vehicle/vehicles')
    elif request.user.is_authenticated:
        vehicle=Vehicle.objects.get(id=id)
        form=VehicleForm(instance=vehicle)
        return render(request,'vehicle/vehicleEdit.html',{ 'form' : form ,'id':id})


# Create your views here.
def bookindex(request):
    if request.user.is_authenticated:
        bookinglist = Book.objects.filter(allottedUser = request.user,status="B")
        totdistance = 0
        totcost = 0
        for i in bookinglist:
            totdistance = totdistance + i.distance
            totcost = totcost + i.cost
        # html_string = render_to_string('report/index.html', {'bookinglist':bookinglist,'totdistance':totdistance,'totcost':totcost})

        # html = HTML(string=html_string)
        # html.write_pdf(target='/tmp/mypdf.pdf');

        # fs = FileSystemStorage('/tmp')
        # with fs.open('mypdf.pdf') as pdf:
        #     response = HttpResponse(pdf, content_type='application/pdf')
        #     response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
        #     render(request,'report/index.html',{'bookinglist':bookinglist,'totdistance':totdistance,'totcost':totcost})
        #     return response
        return render(request,'report/index.html',{'bookinglist':bookinglist,'totdistance':totdistance,'totcost':totcost})
    else:
        return redirect('pageNotFound')

def change(request):
    if request.POST:
        return render(request,'booking/index.html',{'form':form})
    else:
        if request.user.is_authenticated:
            bookinglist = Book.objects.filter(allottedUser = request.user,status="B")
            totdistance = 0
            totcost = 0
            for i in bookinglist:
                totdistance = totdistance + i.distance
                totcost = totcost + i.cost
            msg = EmailMessage(
               'Your Travel Report',
               '<!DOCTYPE html><html><head> <title></title> <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/> <meta name="viewport" content="width=device-width, initial-scale=1"> <meta http-equiv="X-UA-Compatible" content="IE=edge"/> <body style="margin: 0 !important; padding: 0 !important; background-color: #eeeeee;" bgcolor="#eeeeee"> <div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: Open Sans, Helvetica, Arial, sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">Travel Report - RoadLink!</div><table border="0" cellpadding="0" cellspacing="0" width="100%"> <tr> <td align="center" style="background-color: #eeeeee;" bgcolor="#eeeeee"> <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;"> <tr> <td align="center" valign="top" style="font-size:0; padding: 35px;" bgcolor="#044767"> <div style="display:inline-block; max-width:50%; min-width:100px; vertical-align:top; width:100%;"> <table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:300px;"> <tr> <td align="left" valign="top" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 36px; font-weight: 800; line-height: 48px;" class="mobile-center"> <h1 style="font-size: 36px; font-weight: 800; margin: 0; color: #ffffff;">RoadLink</h1> </td></tr></table> </div><div style="display:inline-block; max-width:50%; min-width:100px; vertical-align:top; width:100%;" class="mobile-hide"> <table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:300px;"> <tr> <td align="right" valign="top" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 48px; font-weight: 400; line-height: 48px;"> <table cellspacing="0" cellpadding="0" border="0" align="right"> <tr> <td style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 400;"> <p style="font-size: 18px; font-weight: 400; margin: 0; color: #ffffff;"></p></td><td style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 400; line-height: 24px;"> </td></tr></table> </td></tr></table> </div></td></tr><tr> <td align="center" style="padding: 35px 35px 20px 35px; background-color: #ffffff;" bgcolor="#ffffff"> <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;"> <tr> <td align="center" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding-top: 25px;"> <img src="https://kingit.com.au/wp-content/uploads/2016/04/Report.gif" width="125" height="120" style="display: block; border: 0px;"/> <br><h2 style="font-size: 30px; font-weight: 800; line-height: 36px; color: #333333; margin: 0;"> Travel Report !<br><h2><h3><a href="http://localhost:8000/report">See your Report</a> </h3> </td></tr><tr> <td align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 400; line-height: 24px; padding-top: 10px;"> <p style="font-size: 16px; font-weight: 400; line-height: 24px; color: #777777;"> </p></td></tr><tr> <td align="left" style="padding-top: 20px;"> </td></tr><tr> <td align="left" style="padding-top: 20px;"> <table cellspacing="0" cellpadding="0" border="0" width="100%"> <tr> <td width="75%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px; border-top: 3px solid #eeeeee; border-bottom: 3px solid #eeeeee;"> Total Distance </td><td width="25%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px; border-top: 3px solid #eeeeee; border-bottom: 3px solid #eeeeee;"> {} Km</td></tr><tr> <td width="75%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px; border-top: 3px solid #eeeeee; border-bottom: 3px solid #eeeeee;"> Total Expenditure </td><td width="25%" align="left" style="font-family: Open Sans, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 800; line-height: 24px; padding: 10px; border-top: 3px solid #eeeeee; border-bottom: 3px solid #eeeeee;"> Rs {}</td></tr></table> </td></tr></table> </td></tr><tr> <td align="center" height="100%" valign="top" width="100%" style="padding: 0 35px 35px 35px; background-color: #ffffff;" bgcolor="#ffffff"> <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:660px;"> <tr> <td align="center" valign="top" style="font-size:0;"> <div style="display:inline-block; max-width:50%; min-width:240px; vertical-align:top; width:100%;"> </div><div style="display:inline-block; max-width:50%; min-width:240px; vertical-align:top; width:100%;"> </body></html>'.format(totdistance,totcost),
               'iit2016106@iiita.ac.in',
               [request.user.email],
            )
            msg.content_subtype = "html"
            msg.send()
            return redirect('http://localhost:8000/report')
        else:
            return redirect('pageNotFound')



# Create your views here.

def rindex(request):
    if request.user.is_authenticated:
        form=RepairForm()
        return render(request,'repair/index.html',{'form':form})
    else:
        return redirect('pageNotFound')

def repair(request):
    if request.POST:
        form=RepairForm(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.registeredUser=request.user
            instance.save()
            success_message='Issue Registered'
            form=RepairForm()
            return render(request,'repair/index.html',{'form':form,'success' : success_message})
    else:
        if request.user.is_authenticated:
            form=RepairForm()
            error_message='Something went wrong error'
            return render(request,'repair/index.html',{ 'form' : form ,'error':error_message})
        else:
            return redirect('pageNotFound')

def issues(request):
    if request.POST:
        form=RepairForm(request.POST)
        # if form.is_valid():
        #     instance=form.save(commit=False)
        #     instance.registeredUser=request.user
        #     instance.save()
        #     success_message='Issue Registered'
        #     form=RepairForm()
        return render(request,'repair/index.html',{'form':form})
    else:
        if request.user.is_authenticated:
            repairsList = Repair.objects.all()
            return render(request,'repair/issues.html',{ 'repairsList' : repairsList})
        else:
            return redirect('pageNotFound')

def update(request,id):
    if request.POST:
        # form=RepairForm(request.POST)
        # if form.is_valid():
        #     instance=form.save(commit=False)
        #     instance.registeredUser=request.user
        #     instance.save()
        #     success_message='Issue Registered'
        #     form=RepairForm()
        return render(request,'repair/index.html',{'form':form})
    else:
        if request.user.is_authenticated:
            repair = Repair.objects.get(id=id)
            if repair.status == "S":
                repair.status = "NS"
            else:
                repair.status = "S"
            repair.save()
            repairsList = Repair.objects.all()
            return redirect('http://localhost:8000/repair/issues')
        else:
            return redirect('pageNotFound')

def edit(request,id):
    if request.method == "POST":
        repair=Repair.objects.get(id=id)
        form=RepairForm(request.POST,instance=repair)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('http://localhost:8000/repair/issues')
    elif request.user.is_authenticated:
        repair=Repair.objects.get(id=id)
        form=RepairForm(instance=repair)
        return render(request,'repair/repairEdit.html',{ 'form' : form ,'id':id})
    


def pageNotFound(request):
    return render(request,'404.html')
    


