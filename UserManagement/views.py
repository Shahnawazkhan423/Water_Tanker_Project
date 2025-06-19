from django.shortcuts import render,redirect

def role_selection(request):
    if request.method == 'POST':
        role = request.POST.get('user_role') or request.POST.get('user_role_login')
        
        if role == 'customer':
            if 'user_role' in request.POST:
                return redirect('register')      
            elif 'user_role_login' in request.POST:
                return redirect('login')          

        elif role == 'supplier':
            if 'user_role' in request.POST:
                return redirect('Register_page')  
            elif 'user_role_login' in request.POST:
                return redirect('Login_page')         

    return render(request, 'base.html')