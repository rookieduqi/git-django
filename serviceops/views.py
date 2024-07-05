from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def service_operations(request):
    # 示例服务状态和端口号，实际应该从服务获取状态
    service_status = "未知"
    port = 8000
    return render(request, 'service.html', {'service_status': service_status, 'port': port})


@csrf_exempt
def start_service(request):
    # 在这里添加启动服务的实际逻辑
    return JsonResponse({'message': '服务已启动'})


@csrf_exempt
def stop_service(request):
    # 在这里添加停止服务的实际逻辑
    return JsonResponse({'message': '服务已停止'})


@csrf_exempt
def refresh_service_status(request):
    # 在这里添加刷新服务状态的实际逻辑
    service_status = "运行中"  # 示例状态
    return JsonResponse({'service_status': service_status})
