from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .config import BASE_URL, MODEL_NAME, API_KEY, validate_config

ROLE_PROMPTS = {
    "coordinator": (
        "You are Leo's Coordinator. Clarify the learning objective, adapt the level, "
        "and coordinate the lesson. Your first task is to produce a concise lesson plan "
        "for the Explainer and Quiz Master. Use the student's stated level and learning "
        "history when available. If the request is too vague, ask one focused clarification. "
        "Do not teach the whole lesson yourself."
    ),
    "explainer": (
        "You are Leo's Explainer. Teach the supplied topic accurately and clearly. "
        "Use plain language, a short step-by-step explanation, one relatable example, "
        "and a brief recap. Match the learner's level. Do not reveal quiz answers."
    ),
    "quiz_master": (
        "You are Leo's Quiz Master. Create exactly 5 questions based on the lesson. "
        "Return valid JSON only, with this schema: "
        '{"title":"...","questions":[{"id":1,"type":"short|multiple_choice","question":"...",'
        '"options":["A...","B...","C...","D..."],"expected_concept":"..."}]}. '
        "For short questions use an empty options array. Do not include answers or explanations."
    ),
    "evaluator": (
        "You are Leo's Evaluator. Compare the student's answers with the quiz and lesson. "
        "Be fair and constructive. Return valid JSON only with keys: "
        '{"score":0,"max_score":5,"percentage":0,"overall_feedback":"...",'
        '"question_feedback":[{"id":1,"result":"correct|partially correct|incorrect",'
        '"feedback":"...","expected_answer":"..."}],"weak_concepts":["..."],'
        '"next_step":"continue|reteach"}. '
        "Award partial credit where appropriate. Set next_step to reteach if percentage < 70."
    )
}

def create_model_client():
    validate_config()
    return OpenAIChatCompletionClient(
        model=MODEL_NAME,
        base_url=BASE_URL,
        api_key=API_KEY,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": "unknown",
            "structured_output": False,
        },
        timeout=90,
        max_retries=2,
        temperature=0.3,
    )

def create_agents(model_client):
    return {
        role: AssistantAgent(
            name=f"Leo_{role.title()}",
            model_client=model_client,
            system_message=prompt,
            reflect_on_tool_use=False,
        )
        for role, prompt in ROLE_PROMPTS.items()
    }
