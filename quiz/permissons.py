from rest_framework import permissions
from .models import *
from django.contrib.auth.models import User
from datetime import datetime

class QuizLimit(permissions.BasePermission):
    
    def has_permission(self, request, view):
        user = request.user
        # 1. 해당 유저의 히스토리에서 create_dt를 가져온다.
        history_create_dt = QuizHistory.objects.all().order_by("-create_dt").first().create_dt
        # 2. 해당 유저의 last login을 가져온다.
        last_login_time = User.objects.get(username=user).last_login
        print(history_create_dt)
        print(last_login_time)
        # 3. 둘의 날짜가 다르다면 True반환
        if datetime.strptime(str(history_create_dt), "%Y-%m-%d") != datetime.strptime(str(last_login_time)[:10], "%Y-%m-%d"):
            return True
        # 4. 같다면 해당유저의 create_dt를 가져오는 필터가 갯수가 2개 미만이라면 True
        if len(QuizHistory.objects.filter(create_dt=history_create_dt, user_id=user)) < 2:
            return True
        print()
        # 2개 이상이라면 False
        return False
    
