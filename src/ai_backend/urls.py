"""ai_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import (UserSendsMessage, GetWebsiteState, TtsOnOff, WhisperModelAPI, STTOnOffBtn,
                    ModelSelector, TemperatureSelector, AgentSelected, ChatSelection, CreateNewChat,
                    ServeMp3, CreateWorkflow, CheckWorkflow, CreateProject, CheckProject, CreateUser, CheckUser,
                    SendMessageToAgent, CheckAgentStatus, AllocateResources, CreateAgent,
                    FetchAgentConfig, UpdateAgentConfig, EnlistAgent, GetProjectDetails, UpdateProjectDetails,
                    EnlistAgentInProject, RemoveAgentFromProject, CreateTaskForProject, CheckStatusOfTask,
                    UpdateTask, RemoveTaskFromProject, SendMessageToProject, PWButtonClicked)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Frontend
    path('api/whisper', WhisperModelAPI.as_view(), name='whisper_api'),
    path('api/stt_toggle', STTOnOffBtn.as_view(), name='stt_toggle'),
    path('api/tts_toggle', TtsOnOff.as_view(), name='tts_toggle'),
    path('api/model_change', ModelSelector.as_view(), name='model_change'),
    path('api/temp_change', TemperatureSelector.as_view(), name='temp_change'),
    path('api/agent_select', AgentSelected.as_view(), name='agent_select'),
    path('api/chat_select', ChatSelection.as_view(), name='chat_select'),
    path('api/create_new_chat', CreateNewChat.as_view(), name='create_new_chat'),
    path('api/send_message', UserSendsMessage.as_view(), name='send_message'),
    path('api/get_web_state', GetWebsiteState.as_view(), name='get_web_state'),
    path('api/serve_mp3', ServeMp3.as_view(), name='serve_mp3'),
    # End Frontend

    # Swarm
    path('api/create_workflow', CreateWorkflow.as_view(), name='create_workflow'),
    path('api/check_workflow', CheckWorkflow.as_view(), name='check_workflow'),
    path('api/create_project', CreateProject.as_view(), name='create_project'),
    path('api/check_project', CheckProject.as_view(), name='check_project'),
    path('api/create_user', CreateUser.as_view(), name='create_user'),
    path('api/check_user', CheckUser.as_view(), name='check_user'),
    path('api/send_message_to_agent', SendMessageToAgent.as_view(), name='send_message_to_agent'),
    path('api/check_agent_status', CheckAgentStatus.as_view(), name='check_agent_status'),
    path('api/allocate_resources', AllocateResources.as_view(), name='allocate_resources'),
    path('api/create_agent', CreateAgent.as_view(), name='create_agent'),
    path('api/fetch_agent_config', FetchAgentConfig.as_view(), name='fetch_agent_config'),
    path('api/update_agent_config', UpdateAgentConfig.as_view(), name='update_agent_config'),
    path('api/enlist_agent', EnlistAgent.as_view(), name='enlist_agent'),
    path('api/get_project_details', GetProjectDetails.as_view(), name='get_project_details'),
    path('api/update_project_details', UpdateProjectDetails.as_view(), name='update_project_details'),
    path('api/enlist_agent_in_project', EnlistAgentInProject.as_view(), name='enlist_agent_in_project'),
    path('api/remove_agent_from_project', RemoveAgentFromProject.as_view(), name='remove_agent_from_project'),
    path('api/create_task_for_project', CreateTaskForProject.as_view(), name='create_task_for_project'),
    path('api/check_status_of_task', CheckStatusOfTask.as_view(), name='check_status_of_task'),
    path('api/update_task', UpdateTask.as_view(), name='update_task'),
    path('api/remove_task_from_project', RemoveTaskFromProject.as_view(), name='remove_task_from_project'),
    path('api/send_message_to_project', SendMessageToProject.as_view(), name='send_message_to_project'),
    path('api/pw_button_clicked', PWButtonClicked.as_view(), name='pw_button_clicked'),
    # End swarm
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
