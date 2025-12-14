# content_generation_agent.py
import logging
from langchain_core.messages import SystemMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph
from agents.agent_state import AgentState
from repositories.campaign_repository import CampaignRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentGenerationAgent:
    def __init__(self, model, campaign_repository: CampaignRepository, system="", add_context=True):
        self.system = system
        self.model = model
        self.campaign_repository = campaign_repository
        self.add_context = add_context
        self.graph = self._initialize_graph()
        logger.info("ContentGenerationAgent initialized.")

    def _initialize_graph(self):
        try:
            graph = StateGraph(AgentState)
            graph.add_node("generate_content", self.generate_campaign_content)
            graph.set_entry_point("generate_content")
            logger.info("StateGraph initialized and compiled.")
            return graph.compile()
        except Exception as e:
            logger.error(f"Error initializing StateGraph: {e}")
            raise

    def generate_campaign_content(self, state: AgentState):
        try:
            messages = state['messages']
            user_query = messages[-1].content
            logger.info("Generating campaign content.")

            # Add system message if there is only a single message
            if len(messages) == 1 and self.system:
                messages.insert(0, SystemMessage(content=self.system))
                logger.debug("System message added to messages.")

            # Add audience information as a system message
            selected_audience_name = state.get('selected_audience_name', '')
            selected_audience_description = state.get('selected_audience_description', '')
            if selected_audience_name:
                audience_info = f"\n\n Take into account that the target audience is {selected_audience_name} - {selected_audience_description}"
                audience_message = SystemMessage(content=audience_info)
                messages.append(audience_message)
                logger.debug("Audience information added to messages.")

            # Add context if applicable
            if self.add_context:
                similar_contents = self.campaign_repository.search_similar_campaigns(user_query)
                if similar_contents:
                    context = "\n".join(similar_contents)
                    context_message = SystemMessage(content=f"Similar Content:\n{context}")
                    messages.append(context_message)
                    logger.debug("Context added to messages.")

            message = self.model.invoke(messages)
            logger.info("Content generated successfully.")

            return {'messages': [message], 'initial_english_content': message.content.replace("```json", "").replace("```", "")}
        except Exception as e:
            logger.error(f"Error generating campaign content: {e}")
            raise