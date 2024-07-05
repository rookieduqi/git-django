from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate

# user/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import CustomUser
from .forms import CustomUserForm, CustomUserEditForm, CustomUserPasswordResetForm
from django.contrib.auth.hashers import make_password


def user_list(request):
    if request.method == 'GET':
        users = CustomUser.objects.all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'remark': user.remark,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_disabled': user.is_disabled
            })
        return JsonResponse({'success': True, 'users': users_data})


def add_user(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        user.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def reset_password(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = CustomUserPasswordResetForm(request.POST, instance=user)
        if form.is_valid():
            # hashed_password = make_password(form.cleaned_data['new_password'])
            # user.password = hashed_password
            user.password = form.cleaned_data['new_password']
            user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def login(request):
    if request.method == 'POST':
        return redirect('home')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(username, password)
        if user is not None:
            return render(request, 'base.html')
            # return redirect('home')  # 使用redirect进行页面跳转
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'login.html')


def home(request):
    return render(request, 'base.html')
