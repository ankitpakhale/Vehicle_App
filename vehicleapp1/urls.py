from vehicleapp1 import views
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('vindex/', views.vindex,name='vindex'),
    path('addVehicle/',views.addVehicle,name='addVehicle'),
    path('vehicles/',views.showVehicles,name='showVehicles'),
    path('delete/<int:id>/',views.vdelete,name='delete'),
    path('edit/<int:id>/',views.vedit,name='edit'),
    path('mail/',views.mail,name='mail'),

    path('rindex/', views.rindex,name='rindex'),
    path('issues/',views.issues,name='issues'),
    path('update/<int:id>/',views.update,name='update'),
    path('edit/<int:id>/',views.edit,name='edit'),
    path('repair/',views.repair,name='repair'),

    path('bindex/', views.bindex,name='bindex'),
    path('book/',views.book,name='book'),
    path('bookings/',views.booking,name='bookings'),
    path('pay/',views.pay,name='pay'),
    path('delete/<int:id>/',views.bdelete,name='bdelete'),
    path('changestatus/<int:id>/',views.change,name='delete'),

    path('signup/',views.signup,name='signup'),
    path('login/',views.loginView,name='login'),
    path('logout/',views.logoutView,name='logout'),
    path('profile/',views.profileView,name='profile'),
    path('edit/',views.editView,name='edit'),
    
    path('pageNotFound/',views.pageNotFound,name='pageNotFound'),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

