from typing import List, Dict

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
import os
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from global_code.helpful_functions import create_logger_error, log_it, CustomError
from db.tables.frontend_tables.users import User
from db.tables.frontend_tables.total_chats import TotalChats
from db.tables.frontend_tables.website_state import WebsiteState
from db.tables.frontend_tables.Message import Message
from db.tables.frontend_tables.chats import Chat
from db.tables.frontend_tables.models import Model
from db.tables.frontend_tables.agents_frontend import AgentFrontend
from db.tables.swarm.workflow import Workflow
from db.tables.swarm.project import Project
from db.tables.swarm.task_projects import TaskProject
from db.tables.swarm.prompts import Prompt
from db.tables.swarm.metrics import Metric
from db.tables.swarm.workflow_instance import WorkflowInstance
from db.tables.swarm.project_workflows import ProjectWorkflow
from db.tables.swarm.prompt_groups import PromptGroup
from db.tables.swarm.audit_logs import AuditLog
from db.tables.swarm.deployment_request import DeploymentRequest
from db.tables.swarm.logs import Log
from db.tables.swarm.recourse_allocation import ResourceAllocation
from db.tables.swarm.system_health import SystemHealth
from db.tables.swarm.task_tables.task import Task
from db.tables.swarm.project_agents import ProjectAgent
from db.tables.swarm.task_tables.task_results import TaskResult
from db.tables.swarm.task_tables.task_queue import TaskQueue
from db.tables.swarm.task_tables.task_outcome_feedback import TaskOutcomeFeedback
from db.tables.swarm.agent_tables.agent import Agent
from db.tables.swarm.agent_tables.agent_capability import AgentCapability
from db.tables.swarm.agent_tables.agent_config_version import AgentConfigVersion
from db.tables.swarm.agent_tables.agent_configuration import AgentConfiguration
from db.tables.swarm.agent_tables.agent_feedback import AgentFeedback
from db.tables.swarm.agent_tables.agent_health import AgentHealth
from db.tables.swarm.agent_tables.agent_interactions import AgentInteraction
from db.tables.swarm.agent_tables.agent_types import AgentType
from ai.other.text_to_speech import create_mp3_file, read_speech_file, delete_speech_file
from custom_code.user_sent_message import user_sent_message
logger = create_logger_error(file_path=os.path.abspath(__file__), name_of_log_file='name',
                                 log_to_console=True, log_to_file=False)


class CreateWorkflow(APIView):
    def post(self, request, *args, **kwargs):
        """
        Creates a workflow in the database
        :param request: Needs to have a workflow_name and description
        :param args:
        :param kwargs:
        :return: The result
        """
        workflow_name = request.data.get('workflow_name')
        description = request.data.get('description')
        # log_it(logger, error=None, custom_message=f'{request.data}')
        result = Workflow({'workflow_name': workflow_name, 'description': description}).save()
        return Response(result)


class CheckWorkflow(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the details of a workflow
        :param request: The workflow_id
        :param args:
        :param kwargs:
        :return: The details of the workflow
        """
        workflow_id = request.data.get('workflow_id')
        the_workflow = Workflow({}).select_by_workflow_id(workflow_id)
        return Response(the_workflow)


class CreateProject(APIView):
    def post(self, request, *args, **kwargs):
        """
        Creates a project in the database
        :param request: The project_name, description, start_date, end_date, and status
        :param args:
        :param kwargs:
        :return: The result
        """
        project_name = request.data.get('project_name')
        description = request.data.get('description')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        status = request.data.get('status')
        # log_it(logger, error=None, custom_message=f'{request.data}')
        result = Project({'project_name': project_name, 'description': description, 'start_date': start_date,
                 'end_date': end_date, 'status': status}).save()
        return Response(result)


class CheckProject(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the details of a project
        :param request: Needs to have a project_id
        :param args:
        :param kwargs:
        :return: The details of the project
        """
        project_id = request.data.get('project_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')
        result = Project({}).select_by_project_id(project_id)
        return Response(result)


class CreateUser(APIView):
    def post(self, request, *args, **kwargs):
        """
        Creates a user in the database
        :param request: Needs to have a password and name
        :param args:
        :param kwargs:
        :return: The result
        """
        password = request.data.get('password')
        name = request.data.get('name')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = User({'password': password, 'name': name, "total_chats_id": 1}).save()
        return Response(result)


class CheckUser(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the details of a user
        :param request: Needs to have a user_id
        :param args:
        :param kwargs:
        :return: The details of the user
        """
        user_id = request.data.get('user_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = User({}).select_one_for_primary(user_id)
        return Response(result)


class AllocateResources(APIView):
    def post(self, request, *args, **kwargs):
        """
        Allocates resources to an agent
        :param request: Needs to have an agent_id, cpu_limit, memory_limit, and storage_limit
        :param args:
        :param kwargs:
        :return: The result
        """
        agent_id = request.data.get('agent_id')
        cpu_limit = request.data.get('cpu_limit')
        memory_limit = request.data.get('memory_limit')
        storage_limit = request.data.get('storage_limit')
        # log_it(logger, error=None, custom_message=f'{request.data}')
        result = ResourceAllocation({'agent_id': agent_id, 'cpu_limit': cpu_limit, 'memory_limit': memory_limit,
                            'storage_limit': storage_limit}).save()
        return Response(result)


# Agent lifecycle management


class CreateAgent(APIView):
    def post(self, request, *args, **kwargs):
        """
        Creates an agent in the database
        :param request: Needs to have a name, state, status, type_id, pod_id, namespace, node_name, enlistment_status, last_active, and is_deleted
        :param args:
        :param kwargs:
        :return: The result
        """
        name = request.data.get('name')
        state = request.data.get('state')
        status = request.data.get('status')
        type_id = request.data.get('type_id')
        pod_id = request.data.get('pod_id')
        namespace = request.data.get('namespace')
        node_name = request.data.get('node_name')
        enlistment_status = request.data.get('enlistment_status')
        last_active = request.data.get('last_active')
        is_deleted = request.data.get('is_deleted')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = Agent({'name': name, 'state': state, 'status': status, 'type_id': type_id, 'pod_id': pod_id,
               'namespace': namespace, 'node_name': node_name, 'enlistment_status': enlistment_status,
               'last_active': last_active, 'is_deleted': is_deleted}).save()
        return Response(result)


class FetchAgentConfig(APIView):
    def get(self, request, *args, **kwargs):
        """
        Fetches the agent configuration
        :param request: Needs to have a config_id
        :param args:
        :param kwargs:
        :return: The agent configuration
        """
        config_id = request.data.get('config_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        config_data = AgentConfiguration({}).select_one_for_primary(config_id)
        return Response(config_data)


class UpdateAgentConfig(APIView):
    def post(self, request, *args, **kwargs):
        """
        Updates the agent configuration
        :param request: Needs to have a primary_key, key, value, and sensitive
        :param args:
        :param kwargs:
        :return: The result
        """
        primary_key = request.data.get('primary_key')
        key = request.data.get('key')
        value = request.data.get('value')
        sensitive = request.data.get('sensitive')

        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = AgentConfiguration({}).update_configuration(primary_key, key, value, sensitive)
        return Response(result)


class EnlistAgent(APIView):
    def post(self, request, *args, **kwargs):
        """
        Enlists the agent to the swarm
        :param request: Needs to have an agent_id and enlistment_status
        :param args:
        :param kwargs:
        :return: The status of the agent
        """
        enlistment_status = request.data.get('enlistment_status')
        agent_id = request.data.get('agent_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = Agent({}).update_field('enlistment_status', enlistment_status, agent_id)
        return Response(result)


class SendMessageToAgent(APIView):
    def post(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        agent_id = request.data.get('agent_id')
        agent_id = request.data.get('agent_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        return Response({"SUCCESS": "200"})


class CheckAgentStatus(APIView):
    def get(self, request, *args, **kwargs):
        """
        Check the status of an agent
        :param request: Needs to have an agent_id
        :param args:
        :param kwargs:
        :return: The status of the agent
        """
        agent_id = request.data.get('agent_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = Agent({}).select_one_for_primary(agent_id)
        return Response(result)


class CreateTask(APIView):
    def post(self, request, *args, **kwargs):
        """
        Creates a task in the database
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        description = request.data.get('description')
        priority = request.data.get('priority')
        status = request.data.get('status')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = Task({'description': description, 'priority': priority, 'status': status}).save()
        return Response(result)


class AgentDeployment(APIView):
    """
    Endpoint for deploying or registering a new agent.
    """
    def post(self, request, *args, **kwargs):
        agent_data = request.data
        # Assuming 'Agent' model has fields like 'name', 'status', etc.
        new_agent = Agent.objects.create(**agent_data)
        return Response({"message": "Agent deployed successfully", "agent_id": new_agent.id}, status=201)

class TaskAssignment(APIView):
    """
    Endpoint for assigning tasks to agents.
    """
    def post(self, request, *args, **kwargs):
        task_id = request.data.get('task_id')
        agent_id = request.data.get('agent_id')
        # Assuming 'Task' model has a field 'assigned_agent_id' to store the agent assigned to the task.


        x = AgentInteraction({'agent_id': agent_id, 'task_id': task_id}).save()
        return Response({"message": "Task assigned successfully"}, status=201)

class TaskProgressUpdate(APIView):
    """
    Endpoint for agents to update task progress.
    """
    def post(self, request, *args, **kwargs):
        task_id = request.data.get('task_id')


        # Assuming 'Task' model has a field 'progress' to store the progress of the task.
        result = TaskResult({}).select_one_for_task(task_id)
        return Response(result)



class SetAgentHealth(APIView):
    def post(self, request, *args, **kwargs):
        """
        Check the status of an agent
        :param request: Needs to have an agent_id
        :param args:
        :param kwargs:
        :return: The status of the agent
        """
        agent_id = request.data.get('agent_id')
        status = request.data.get('status')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = AgentHealth({}).update_status(status, agent_id)
        return Response(result)
# END Agent lifecycle management

# Project and Task management


class GetProjectDetails(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the details of a project
        :param request: Needs to have a project_id
        :param args:
        :param kwargs:
        :return: The details of the project
        """
        project_id = request.data.get('project_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = Project({}).select_by_project_id(project_id)
        return Response(result)


class UpdateProjectDetails(APIView):
    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        project_name = request.data.get('project_name', None)
        description = request.data.get('description', None)
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date', None)
        status = request.data.get('status', None)
        is_active = request.data.get('is_active', None)
        # log_it(logger, error=None, custom_message=f'{request.data}'

        result = Project({}).update_project(project_id, project_name, description, start_date, end_date, status, is_active)
        return Response(result)


class EnlistAgentInProject(APIView):
    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        agent_id = request.data.get('agent_id')
        role = request.data.get('role')
        # log_it(logger, error=None, custom_message=f'{request.data}'

        result = ProjectAgent({"project_id": project_id, "agent_id": agent_id, "role": role}).save()
        return Response(result)


class RemoveAgentFromProject(APIView):
    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        agent_id = request.data.get('agent_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = ProjectAgent({}).delete_project_agent(project_id, agent_id)
        return Response({"SUCCESS": "200"})


class CreateTaskForProject(APIView):
    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        task_id = request.data.get('task_id')

        result = TaskProject({"project_id": project_id, "task_id": task_id}).save()
        return Response(result)


class CheckStatusOfTask(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the details of a task
        :param request: The task_id
        :param args:
        :param kwargs:
        :return: The details of the task
        """
        task_id = request.data.get('task_id')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = Task({}).select_one_for_primary(task_id)
        return Response(result)


class UpdateTask(APIView):
    def post(self, request, *args, **kwargs):
        """
        Updates the task
        :param request: The task_id, status, description, and priority (last 3 are optional)
        :param args:
        :param kwargs:
        :return:
        """
        task_id = request.data.get('task_id')
        status = request.data.get('status', None)
        description = request.data.get('description', None)
        priority = request.data.get('priority', None)
        # log_it(logger, error=None, custom_message=f'{request.data}')

        result = Task({}).edit_task(task_id, status, description, priority)
        return Response(result)


class RemoveTaskFromProject(APIView):
    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        task_id = request.data.get('task_id')

        result = TaskProject({}).delete_association(project_id, task_id)
        return Response(result)


class SendMessageToProject(APIView):
    def post(self, request, *args, **kwargs):
        tts_on_off = request.data.get('tts_on_off')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        if not tts_on_off:
            tts_on_off = 0
        else:
            tts_on_off = 1
        WebsiteState({}).edit_any_row(new_name=tts_on_off, primary_key=1, row_name='tts')
        return Response({"SUCCESS": "200"})


# END Project and Task management

# Frontend stuff


class WhisperModelAPI(APIView):
    def get(self, request, format=None):
        # Placeholder for your GET request logic
        return Response({"message": "This is a GET request"})

    def post(self, request, format=None):
        # Placeholder for handling POST request, e.g., streaming audio data
        return Response({"message": "This is a POST request"})


class STTOnOffBtn(APIView):
    def post(self, request, *args, **kwargs):
        stt_on_off = request.data.get('stt_on_off')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        if not stt_on_off:
            stt_on_off = 0
        else:
            stt_on_off = 1
        WebsiteState({}).edit_any_row(new_name=stt_on_off, primary_key=1, row_name='stt')
        return Response({"SUCCESS": "200"})


class TtsOnOff(APIView):
    def post(self, request, *args, **kwargs):
        tts_on_off = request.data.get('tts_on_off')
        # log_it(logger, error=None, custom_message=f'{request.data}')

        if not tts_on_off:
            tts_on_off = 0
        else:
            tts_on_off = 1
        WebsiteState({}).edit_any_row(new_name=tts_on_off, primary_key=1, row_name='tts')
        return Response({"SUCCESS": "200"})




class ModelSelector(APIView):
    """Changes the selected model"""
    def post(self, request, *args, **kwargs):

        model_name = request.data.get('value')
        if not model_name:
            return Response({'error': 'Model ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        WebsiteState({}).edit_any_row(new_name=model_name, primary_key=1, row_name='model_selected')
        return Response({"SUCCESS": "200"})


class TemperatureSelector(APIView):
    """Changes the selected temperature"""
    def post(self, request, *args, **kwargs):

        temperature = request.data.get('value')
        if not temperature:
            return Response({'error': 'Model ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        WebsiteState({}).edit_any_row(new_name=temperature, primary_key=1, row_name='temperature')
        return Response({"SUCCESS": "200"})


class AgentSelected(APIView):
    """Changes the selected agent"""
    def post(self, request, *args, **kwargs):

        agent_selected = request.data.get('value')
        if not agent_selected:
            return Response({'error': 'Model ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        # model_id = Model({}).select_one_for_name(name=model_name)[0]['model_id']
        WebsiteState({}).edit_any_row(new_name=agent_selected, primary_key=1, row_name='agent_selected')

        return Response({"SUCCESS": "200"})


class ChatSelection(APIView):
    """Changes the selected chat"""
    def post(self, request, *args, **kwargs):
        log_it(logger, error=None, custom_message=f'Chat Change Request: {request.data}')
        chat_id = request.data.get('chat_id')
        if not chat_id:
            return Response({'error': 'Model ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        WebsiteState({}).edit_any_row(new_name=chat_id, primary_key=1, row_name='current_chat')
        return Response({'SUCCESS': '200'})


class CreateNewChat(APIView):
    """Changes the selected chat"""
    def post(self, request, *args, **kwargs):
        # create_new_chat = request.data.get('create_new_chat')
        # if not create_new_chat:
        #     return Response({'error': 'Model ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        new_chat_id = Chat({"title": "New Chat", "total_chats_id": 1}).save()
        WebsiteState({}).edit_any_row(new_name=new_chat_id, primary_key=1, row_name='current_chat')
        return Response({'SUCCESS': '200'})


class ServeMp3(APIView):
    """Serves the speech.mp3 file."""

    def get(self, request, *args, **kwargs):
        return self.serve_file()

    def post(self, request, *args, **kwargs):
        return self.serve_file()

    def serve_file(self):
        file_path = r"/src/media/speech.mp3"
        file_name = "speech.mp3"
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                mp3_data = f.read()
            response = HttpResponse(mp3_data, content_type='audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        else:
            return HttpResponse(status=404)



class UserSendsMessage(APIView):
    """Changes the selected chat"""
    def post(self, request, *args, **kwargs):
        create_new_chat = request.data.get('create_new_message')
        if not create_new_chat:
            return Response({'error': 'Model ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        web_state: dict = WebsiteState({}).select_one_for_primary(1)[0]
        # log_it(logger, error=None, custom_message=f'Website State: {web_state}')
        Message({'model': "User", 'agent': "User",
                 'temp': 0.0,
                 'chat_id': web_state['current_chat'], 'message': create_new_chat}).save()
        total_chat = Chat({}).select_one_for_primary(web_state['current_chat'])[0]
        # log_it(logger, error=None, custom_message=f'total_chat: {total_chat}')
        # log_it(logger, error=None, custom_message=f'all_msg: {Message({}).select_all()}')
        # total_chat: dict = TotalChats({}).select_one_for_primary(web_state['current_chat'])[0]
        ai_response: str = user_sent_message(total_chat, web_state)
        Message({'model': web_state["model_selected"], 'agent': web_state["agent_selected"],
                 'temp': web_state["temperature"],
                 'chat_id': web_state['current_chat'], 'message': ai_response}).save()
        current_chat_frontend_version: List[Dict[str, str]] = []
        current_chat_db_version = Message({}).select_one_where_chat_id(web_state['current_chat'])

        for chat in current_chat_db_version:
            if chat['model'] == 'User':
                current_chat_frontend_version.append({"who_said_it": "User", "text": chat['message']})
            else:
                current_chat_frontend_version.append({"who_said_it": "Jarvis", "text": chat['message']})

        if web_state['tts'] == 0:
            log_it(logger, error=None, custom_message=f'STT AI: {ai_response}')
            create_mp3_file(ai_response)
            speech_file = read_speech_file()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'audio_group',  # Use the same group name as in your consumer
                {
                    'type': 'audiomessage',  # Matches the method in the consumer
                    'message': speech_file
                }
            )

        return Response(current_chat_frontend_version)


class GetWebsiteState(APIView):
    """Changes the selected chat"""
    def get(self, request, *args, **kwargs):

        web_state: dict = WebsiteState({}).select_one_for_primary(1)[0]
        log_it(logger, error=None, custom_message=f'Website State: {web_state}')
        current_chat_frontend_version: List[Dict[str, str]] = [] # Only things in the dict will be who_said_it and text
        current_chat_db_version = Message({}).select_one_where_chat_id(web_state['current_chat'])

        for chat in current_chat_db_version:
            if chat['model'] == 'User':
                current_chat_frontend_version.append({"who_said_it": "User", "text": chat['message']})
            else:
                current_chat_frontend_version.append({"who_said_it": "Jarvis", "text": chat['message']})
        past_convos_db_version = Chat({}).select_all()
        past_convos_frontend_version = []
        # Make the same loop but loop through in opposite order
        for chat in reversed(past_convos_db_version):
            past_convos_frontend_version.append(chat)

        web_state["past_convos"] = past_convos_frontend_version
        web_state["current_convo"] = current_chat_frontend_version
        web_state["agents"] = AgentFrontend({}).select_all()
        web_state["models"] = Model({}).select_all()

        return Response(web_state)


class PWButtonClicked(APIView):
    """Changes the selected chat"""
    def get(self, request, *args, **kwargs):
        ai = Agent({}).select_one_for_primary(1)
        log_it(logger, error=None, custom_message=f'AI PW: {ai}')
        url = "http://agent1:7866/api/internal/message"
        try:
            response = requests.get(url, timeout=10)  # 10-second timeout
            response.raise_for_status()  # Raises an HTTPError for bad responses
            data = response.json()
            log_it(logger=logger, error=None, custom_message=f'PW Button Clicked: {data}')
        except requests.RequestException as e:
            log_it(logger=logger, error=e, custom_message=f"Failed to fetch data from {url}")
            raise CustomError(f"Error fetching data from {url}: {e}")
        return Response({"SUCCESS": "200"})
