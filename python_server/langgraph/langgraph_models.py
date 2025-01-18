from typing_extensions import TypedDict

class ConfigSchema(TypedDict):
    """
    The ConfigSchema defines what is passed into the execution flow at the start.
    """

    prompt_input: PromptInput


class AgentContext(BaseModel):
    """
    The AgentContext is initiated at the beginning of the execution flow and is available to all nodes.
    """

    class Config:
        arbitrary_types_allowed = True

    context_creation_timing: float
    prompt_input: PromptInput
    neo4j_manager: Neo4jManager
    mongodb_manager: AsyncMongoDBManager
    chat_analytics_manager: ChatAnalyticsManager
    initial_chat_state: InitialChatState
    runnable_factory: RunnableFactory
    neo4j_vectorstore_factory: Neo4jVectorStoreFactory
