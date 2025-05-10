from common.server.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from common.utils.push_notification_auth import PushNotificationSenderAuth
from finala2e.task_manager import AgentTaskManager
from finala2e.agent import A2ECombinedAgent
import click
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10003)
def main(host, port):
    """Starts the Combined A2A Agent server with Math, Currency, and generic A2A capabilities."""
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
        
        math_skill = AgentSkill(
            id="math_operations",
            name="Math Operations",
            description="Performs basic math operations like addition and multiplication",
            tags=["math", "calculations"],
            examples=["What is 123 + 456?", "Calculate 78 * 45"],
        )
        
        currency_skill = AgentSkill(
            id="currency_conversion",
            name="Currency Conversion",
            description="Helps with exchange values between various currencies",
            tags=["currency conversion", "currency exchange"],
            examples=["What is exchange rate between USD and GBP?", "Convert 100 EUR to JPY"],
        )
        
        a2a_skill = AgentSkill(
            id="a2a_agent_integration",
            name="A2A Agent Integration",
            description="Connects to external A2A-compatible agents for specialized tasks",
            tags=["a2a", "integration", "agent-to-agent"],
            examples=[
                "Create a Python function to parse JSON",
                "Generate documentation for my API",
                "Explain how to implement authentication in Express.js"
            ],
        )
        
        agent_card = AgentCard(
            name="Combined A2A Agent",
            description="An agent that combines math operations, currency conversions, and generic A2A capabilities",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=A2ECombinedAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=A2ECombinedAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[math_skill, currency_skill, a2a_skill],
        )

        notification_sender_auth = PushNotificationSenderAuth()
        notification_sender_auth.generate_jwk()
        
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=A2ECombinedAgent(), notification_sender_auth=notification_sender_auth),
            host=host,
            port=port,
        )

        server.app.add_route(
            "/.well-known/jwks.json", notification_sender_auth.handle_jwks_endpoint, methods=["GET"]
        )

        logger.info(f"Starting Combined A2A Agent server on {host}:{port}")
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()