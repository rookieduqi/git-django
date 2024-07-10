from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess

SERVICE_NAME = 'mydjango.service'
PORT = 8000


def service_operations(request):
    service_status = get_service_status()
    return render(request, 'service.html', {'service_status': service_status, 'port': PORT})


def get_service_status():
    try:
        result = subprocess.run(['systemctl', 'is-active', SERVICE_NAME], capture_output=True, text=True)
        if result.returncode == 0:
            status_map = {
                'active': '运行中',
                'inactive': '已停止',
                'failed': '失败'
            }
            return status_map.get(result.stdout.strip(), '未知')
        else:
            return "未知"
    except Exception as e:
        return f"错误: {str(e)}"


def manage_service(action):
    try:
        result = subprocess.run(['sudo', 'systemctl', action, SERVICE_NAME], capture_output=True, text=True)
        if result.returncode == 0:
            return f'服务已{action}'
        else:
            return f'{action.capitalize()}服务失败: {result.stderr}'
    except Exception as e:
        return f'{action.capitalize()}服务时发生错误: {str(e)}'


def start_service(request):
    message = manage_service('start')
    return JsonResponse({'message': message})


def stop_service(request):
    message = manage_service('stop')
    return JsonResponse({'message': message})


def refresh_service_status(request):
    service_status = get_service_status()
    return JsonResponse({'service_status': service_status})
