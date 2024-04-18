# myapp/middleware.py
import os
import importlib.util
import sys


from global_code.helpful_functions import create_logger_error, log_it

logger = create_logger_error(file_path=os.path.abspath(__file__), name_of_log_file='middleware',
                                 log_to_console=True, log_to_file=False)


class RunOnceMiddleware:
    has_run = False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self.__class__.has_run:
            self.run_once()
            self.__class__.has_run = True
        return self.get_response(request)

    @staticmethod
    def run_once():
        # Your initialization code here
        log_it(logger, error=None, custom_message="Running initialization code")
        check_user()
        initialize_template_agent()









        # tools_dir = r"ai/tools"
        # find_and_register_tools(tools_dir)
        # target_directory = 'ai/agents'  # Set the path to your target directory
        # load_and_register_agents(target_directory)

        # for folder_name in os.listdir(target_directory):
        #     folder_path = os.path.join(target_directory, folder_name)
        #     if os.path.isdir(folder_path):
        #         Folder.objects.get_or_create(name=folder_name)



        # all_functs = Function({}).select_all()
        # log_it(logger, error=None, custom_message=f"ALL FUNCTS: {all_functs}")
        # all_agents = Agent({}).select_all()
        # log_it(logger, error=None, custom_message=f"ALL AGENTS: {all_agents}")
        # all_agent_functions = AgentFunctions().select_all()
        # log_it(logger, error=None, custom_message=f"ALL AGENT FUNCTIONS: {all_agent_functions}")


def load_module_from_file(file_path):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_and_register_tools(tools_dir):
    """
    Will search the tools directory for any tools and register them in the database
    :param tools_dir:
    :return:
    """
    for root, dirs, files in os.walk(tools_dir):
        for file in files:
            if file == '__init__.py' or file == "ToolExample.py":
                continue
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                module = load_module_from_file(file_path)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type):  # Check if the attribute is a class
                        if hasattr(attr, 'json_of_tool'):
                            tool_info = attr.json_of_tool()
                            if not Function({}).select_one_for_name(tool_info['name']):
                                Function({
                                    "function_name": tool_info['name'],
                                    "function_description": tool_info['description'],
                                    "function_inputs": tool_info['parameters']['properties'],
                                    "function_output": "",
                                    "function_json": tool_info
                                }).save()
                                log_it(logger, error=None, custom_message=f"Registered tool: {tool_info['name']}")


def load_and_register_agents(target_directory):
    """
    Will search the target directory for any agents and register them in the database
    :param target_directory:
    :return:
    """
    for agent_name in os.listdir(target_directory):
        if agent_name == '__pycache__' or agent_name == "AgentExample":
            continue
        agent_dir_path = os.path.join(target_directory, agent_name)
        if os.path.isdir(agent_dir_path):
            agent_file_path = os.path.join(agent_dir_path, f"{agent_name}.py")
            if os.path.isfile(agent_file_path):
                module = load_module_from_file(agent_file_path)
                if hasattr(module, agent_name):
                    agent_class = getattr(module, agent_name)
                    if hasattr(agent_class, 'change_these_attributes'):
                        attributes = agent_class.change_these_attributes()
                        # Check if the agent is already in the DB
                        agent_id_check = AgentFrontend({}).select_one_for_name(agent_name)

                        if not agent_id_check:
                            # If it is, update the attributes
                            agent_id = AgentFrontend({
                                "agent_name": agent_name,
                                "agent_description": attributes['agent_description'],
                                "base_temp": attributes['base_temp'],
                                "base_model": attributes['base_model'],
                                "long_term_memory": attributes['long_term_memory'],
                                "contextual_environmental_memory": attributes['contextual_environmental_memory'],
                                "task_delegation": attributes['task_delegation'],
                                "emotional_intelligence": attributes['emotional_intelligence']
                            }).save()
                            tools_li = attributes['tools']
                            for tool in tools_li:
                                function_id = Function({}).select_one_for_name(tool)[0]['function_id']
                                # log_it(logger, error=None, custom_message=f"Function ID: {function_id}")
                                # log_it(logger, error=None, custom_message=f"Agent ID: {agent_id}")
                                AgentFunctions().link_agent_to_function(agent_id=agent_id, function_id=function_id)
                            log_it(logger, error=None,
                                   custom_message=f"Registered agent: {agent_name}")


def check_user():
    """
    Checks if DB is already populated if not will populate it
    :return:
    """
    if not User({}).select_one_for_primary(1):
        TotalChats({
            'total_chats_id': 0,
            'total_chats': 0
        }).save()
        User({
            'password': 'password',
            'name': 'admin',
            'total_chats_id': 1
        }).save()
        Chat({"title": "Theory of the universe", "total_chats_id": 1}).save()
        Chat({"title": "Testing something", "total_chats_id": 1}).save()
        WebsiteState({
            'website_state_id': 0,
            'user_id': 1,
            'tts': 0,
            'stt': 0,
            'current_chat': 1,
            'model_selected': 'Gpt 3.5',
            'temperature': 0.7,
            'agent_selected': 'none'
        }).save()
        Model({"model_name": "Auto", "model_info": "Let the gods decide your fate", "company": "NA"}).save()
        Model({"model_name": "Gpt 3.5", "model_info": "16k context window", "company": "OpenAI"}).save()
        Model({"model_name": "Gpt 4", "model_info": "128k context window", "company": "OpenAI"}).save()
        Model({"model_name": "Gpt 4V", "model_info": "128k context window, multimodal", "company": "OpenAI"}).save()
        Model({"model_name": "Gemini Pro", "model_info": "128k context window, multimodal", "company": "Google"}).save()
        Model({"model_name": "Gemini 1.5", "model_info": "1M context window, multimodal", "company": "Google"}).save()
        Model({"model_name": "Mixtral 8x7b", "model_info": "32k context window", "company": "Mistral"}).save()
        Model({"model_name": "Mistral 7b", "model_info": "32k context window", "company": "Mistral"}).save()
        Model({"model_name": "Claude 3 Haiku", "model_info": "200k context window, multimodal, cheapest", "company": "Anthropic"}).save()
        Model({"model_name": "Claude 3 Sonnet", "model_info": "200k context window, multimodal, middle-ground", "company": "Anthropic"}).save()
        Model({"model_name": "Claude 3 Opus", "model_info": "200k context window, multimodal, best & pricey", "company": "Anthropic"}).save()

        AgentFrontend({"agent_name": "None", "agent_description": "No agent selected", "base_temp": 0.1, "base_model": "Gpt 3.5",
               "long_term_memory": False,
               "contextual_environmental_memory": False,
               "task_delegation": False,
               "emotional_intelligence": False
               }).save()
        AgentFrontend({"agent_name": "Everything", "agent_description": "All agents combined", "base_temp": 0.1, "base_model": "Gpt 3.5",
               "long_term_memory": True,
               "contextual_environmental_memory": True,
               "task_delegation": False,
               "emotional_intelligence": False
               }).save()

        log_it(logger, error=None, custom_message='User and TotalChats, Website_state, models, chats tables have been initialized.')


def initialize_template_agent():
    """
    Initializes a template agent and related records such as agent type, configuration, and capabilities.
    """
    # Ensure the agent type exists or create it
    log_it(logger, error=None, custom_message=f"Initializing template agent {AgentType({}).select_one_for_name('Standard')}")
    if not isinstance((AgentType({}).select_one_for_name("Standard")), tuple):
        log_it(logger, error=None, custom_message="Template agent already exists")
        return None
    # This method would ideally check if the agent type exists and return its ID, or create it if it doesn't exist
    agent_type = AgentType({"type_name": "Standard", "image": "image.name"})
    type_id = agent_type.save()

    # Create the agent itself
    template_agent_data = {
        'name': 'TemplateAgent',
        'state': 'idle',
        'status': 'online',
        'type_id': type_id,
        'pod_id': 'default-pod',
        'namespace': 'default-namespace',
        'node_name': 'default-node',
        'enlistment_status': 'sleep',
        'is_deleted': False
    }
    template_agent = Agent(template_agent_data)
    agent_id: int = template_agent.save()  # Assume this method returns the newly created agent's ID

    agent_config_id = AgentConfiguration({
        "type_id": type_id,
        "key_name": "default_config",
        "value_name": "true",
        "sensitive_name": False,
        "is_deleted": False
    }).save()

    AgentConfigVersion({
        "config_id": agent_config_id,
        "type_id": type_id,
        "key_name": "default_config",
        "value_name": "true",
        "sensitive_name": False
    }).save()

    AgentCapability({
        "agent_id": agent_id,
        "capability_name": "default_capability",
        "capability_value": "standard"
    }).save()


def init_agent_type(agent_name: str, image_name: str, agent_config_key: str, agent_config_value: str,
                    agent_capability_name: str, agent_capability_value: str):
    """
    Initializes an agent type and related records such as agent configuration and capabilities.
    :param agent_name: The name of the agent type
    :param image_name: The name of the image
    :param agent_config_key: The key of the agent configuration
    :param agent_config_value: Required value of the agent configuration
    :param agent_capability_name: Required name of the agent capability
    :param agent_capability_value: The value of the agent capability
    :return: NONE
    """
    if not isinstance((AgentType({}).select_one_for_name(agent_name)), tuple):
        log_it(logger, error=None, custom_message="Template agent already exists")
        return None
    # This method would ideally check if the agent type exists and return its ID, or create it if it doesn't exist
    agent_type = AgentType({"type_name": agent_name, "image": image_name})
    type_id = agent_type.save()

    # Create the agent itself
    template_agent_data = {
        'name': agent_name,
        'state': 'idle',
        'status': 'offline',
        'type_id': type_id,
        'pod_id': 'default-pod',
        'namespace': 'default-namespace',
        'node_name': 'default-node',
        'enlistment_status': 'sleep',
        'is_deleted': False
    }
    template_agent = Agent(template_agent_data)
    agent_id: int = template_agent.save()  # Assume this method returns the newly created agent's ID

    agent_config_id = AgentConfiguration({
        "type_id": type_id,
        "key_name": agent_config_key,
        "value_name": agent_config_value,
        "sensitive": False,
        "is_deleted": False
    }).save()

    AgentConfigVersion({
        "config_id": agent_config_id,
        "type_id": type_id,
        "key_name": "default_config",
        "value_name": "true",
        "sensitive": False
    }).save()

    AgentCapability({
        "agent_id": agent_id,
        "capability_name": agent_capability_name,
        "capability_value": agent_capability_value
    }).save()
