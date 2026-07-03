from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

from .forms import StaffRegistrationForm, StaffLoginForm
from .decorators import staff_role_required

# Create your views here.

def staff_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 
    
     # Redirect to a dashboard or home page if already logged in

    if request.method == 'POST':
        form = StaffLoginForm(data=request.POST)
        if form.is_valid():

            # Log the user in

            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
          
        # Redirect to a dashboard or home page after login
    else:
        form = StaffLoginForm()
    return render(request, 'login.html', {'form': form})
