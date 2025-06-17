from django.shortcuts import render,redirect

def role_selection(request):
    if request.method == 'POST':
        user_role = request.POST.get('user_role')
        
        if user_role == 'customer':
            return redirect('register')
        elif user_role == 'supplier':
            return redirect('Register_page')
    
    return render(request, 'base.html')