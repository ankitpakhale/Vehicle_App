from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Driver(models.Model):
    firstName=models.CharField(max_length=100)
    lastName=models.CharField(max_length=100)
    nationalId=models.CharField(max_length=13)
    address=models.CharField(max_length=1000)
    email=models.CharField(max_length=300)
    phoneNumber=models.CharField(max_length=10)
    licenseCategory=models.CharField(max_length=100)
    status_CHOICES=(
        ('B','booked'),
        ('NB','not booked')
    )
    status=models.CharField(
        max_length=2,
        choices=status_CHOICES,
        default='NB',
    )
    def __str__(self):
        return 'Driver name : '+self.firstName

class Vehicle(models.Model):
    VEHICLE_STATUS_CHOICES = (
        ('B', 'Booked'),
        ('NB', 'Not Booked'),
    )
    INSURANCE_STATUS_CHOICES = (
        ('U','Updated'),
        ('NU','Not Updated'),
    )
    VEHICLE_TYPE_CHOICES = (
        ('P','Passenger'),
        ('T','Truck'),
        ('C','Construction'),
    )
    FUEL_TYPE_CHOICES = (
        ('P','Petrol'),
        ('D','Diesel'),
    )
    owner = models.ForeignKey(User,default=None,on_delete=models.CASCADE)
    cost_per_km = models.DecimalField(max_digits=20,default=0,decimal_places=2)
    price = models.DecimalField(max_digits=20,default="0",decimal_places=3)
    registration_plate = models.CharField(max_length=200,default='')
    vehicle_status = models.CharField(max_length=2,default='NB',choices=VEHICLE_STATUS_CHOICES)
    insurance_status = models.CharField(max_length=2,default='NU',choices=INSURANCE_STATUS_CHOICES)
    no_of_km_travelled = models.DecimalField(max_digits=20,default=0,decimal_places=0)
    fuel_type = models.CharField(max_length=1,default='P',choices=FUEL_TYPE_CHOICES)
    mileage = models.DecimalField(max_digits=20,default=0,decimal_places=0)
    vehicle_type = models.CharField(max_length=1,default='P',choices=VEHICLE_TYPE_CHOICES)
    image=models.ImageField(upload_to="vehicle_image",default="default.png",blank=True)

    def __str__(self):
        return self.registration_plate

class Book(models.Model):
    source=models.CharField(max_length=100)
    destination=models.CharField(max_length=100)
    distance=models.DecimalField(max_digits=20,default=0,decimal_places=2)
    bookingDate=models.DateTimeField(default=timezone.now)
    startDate=models.DateTimeField("Start date ")
    endDate=models.DateTimeField("end date ")
    securityDeposit=models.IntegerField()
    status_CHOICES=(
        ('B','booked'),
        ('NB','not booked'),
        ('E','expired')
    )
    status=models.CharField(
        max_length=2,
        choices=status_CHOICES,
        default='NB',
    )
    discountId=models.CharField(max_length=100)
    allottedUser=models.ForeignKey(User,default=None,on_delete=models.CASCADE)
    allottedDriver=models.ForeignKey(Driver,null=True,blank=True,on_delete=models.CASCADE)
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    cost=models.FloatField()
    duration=models.CharField(max_length=100,default="Error")
    def __str__(self):
        return 'source : '+self.source

class Repair(models.Model):
    registeredDate=models.DateTimeField(default=timezone.now)
    status_CHOICES=(
        ('S','solved'),
        ('NS','not solved')
    )
    status=models.CharField(
        max_length=2,
        choices=status_CHOICES,
        default='NS',
    )
    registeredUser=models.ForeignKey(User,default=None,on_delete=models.CASCADE)
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    issue=models.CharField(max_length=1000)
    def __str__(self):
        return 'issue : '+self.issue