from django.db import transaction
from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate

# user/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import CustomUser
from .forms import CustomUserForm, CustomUserEditForm, CustomUserPasswordResetForm
from django.contrib.auth.hashers import make_password
from django.conf import settings

import json
import subprocess


def handle_script_request(script_args):
    result = subprocess.run([settings.EDITOR_DIR, settings.SCRIPT_DIR, script_args], capture_output=True, text=True)
    if result.returncode == 0:
        try:
            script_output = json.loads(result.stdout)
            if script_output.get('code') == 200:
                return True, script_output
            else:
                raise Exception(
                    f"Script failed with code: {script_output.get('code')}, message: {script_output.get('msg')}")
        except json.JSONDecodeError:
            raise Exception("Failed to decode script output as JSON")
    else:
        raise Exception(result.stderr)


def add_user(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)

                    # Prepare the data for the external script
                    script_args = json.dumps({
                        "c": "user",
                        "a": "create_or_update_user",
                        "data": {
                            "user_name": user.username,
                            "password": user.password
                        }
                    })

                    # Call the external script
                    success, script_output = handle_script_request(script_args)

                    if success:
                        user.save()
                        return JsonResponse({'success': True, 'output': script_output})
                    else:
                        raise Exception("Script execution failed")
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def reset_password(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = CustomUserPasswordResetForm(request.POST, instance=user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)

                    # Prepare the data for the external script
                    script_args = json.dumps({
                        "c": "user",
                        "a": "create_or_update_user",
                        "data": {
                            "user_name": user.username,
                            "password": form.cleaned_data['new_password']
                        }
                    })

                    # Call the external script
                    success, script_output = handle_script_request(script_args)

                    if success:
                        user.password = form.cleaned_data['new_password']
                        user.save()
                        return JsonResponse({'success': True, 'output': script_output})
                    else:
                        raise Exception("Script execution failed")
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)

                    # Prepare the data for the external script
                    if user.is_disabled:
                        script_args = json.dumps({
                            "c": "user",
                            "a": "delete_user",
                            "data": {
                                "user_name": user.username
                            }
                        })
                    else:
                        script_args = json.dumps({
                            "c": "user",
                            "a": "create_or_update_user",
                            "data": {
                                "user_name": user.username,
                                "password": user.password
                            }
                        })

                    # Call the external script
                    success, script_output = handle_script_request(script_args)

                    if success:
                        user.save()
                        return JsonResponse({'success': True, 'output': script_output})
                    else:
                        raise Exception("Script execution failed")
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Prepare the data for the external script
                script_args = json.dumps({
                    "c": "user",
                    "a": "delete_user",
                    "data": {
                        "user_name": user.username
                    }
                })
                # Call the external script
                success, script_output = handle_script_request(script_args)


                if success:
                    user.delete()
                    return JsonResponse({'success': True, 'output': script_output})
                else:
                    raise Exception("Script execution failed")
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


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
