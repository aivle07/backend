from django.urls import path
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register("board",BoardViewSet)

app_name = "quiz"
urlpatterns = [
    path("",views.QuizListAPIView.as_view(), name="quiz-list"),
    path("<int:pk>/",views.QuizRetrieveAPIView.as_view(), name="quiz-detail"),
    path("history/",views.QuizHistoryListAPIView.as_view(), name="quiz-history"),
    path("history/<int:pk>/",views.QuizHistoryRetrieveAPIView.as_view(),name="quiz-history-detail"),
    
    
    
]