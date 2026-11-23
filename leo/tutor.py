import asyncio
import json
import re
from .agents import create_model_client, create_agents
from .memory import load_memory, save_memory

def _content(task_result):
    if not task_result.messages:
        return ""
    value = task_result.messages[-1].content
    return value if isinstance(value, str) else str(value)

def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start:end + 1])
    raise ValueError("Agent did not return a valid JSON object.")

async def _ask(agent, prompt):
    result = await agent.run(task=prompt)
    return _content(result)

async def start_lesson(student_name: str, topic: str, level: str):
    if not student_name.strip() or not topic.strip():
        raise ValueError("Please enter both your name and a topic.")
    client = create_model_client()
    agents = create_agents(client)
    memory = load_memory(student_name)
    history = memory.get("topics", [])
    log = []
    try:
        log.append("1) Coordinator is planning the learning session...")
        plan = await _ask(
            agents["coordinator"],
            f"Student: {student_name}\nLevel: {level}\nRequested topic: {topic}\n"
            f"Previously studied topics: {history}\nCreate a short plan and specify what "
            "the Explainer should teach and what the Quiz Master should assess."
        )

        log.append("2) Coordinator → Explainer: lesson plan handed off.")
        lesson = await _ask(
            agents["explainer"],
            f"Coordinator's plan (follow this):\n{plan}\n\n"
            f"Teach the student about: {topic}. Level: {level}."
        )

        log.append("3) Explainer → Quiz Master: lesson content handed off.")
        quiz_text = await _ask(
            agents["quiz_master"],
            f"Create a quiz using only the material in this lesson.\n"
            f"Topic: {topic}\nLevel: {level}\nLesson:\n{lesson}"
        )
        quiz = _extract_json(quiz_text)
        questions = quiz.get("questions", [])
        if len(questions) != 5:
            raise ValueError("Quiz Master did not produce exactly five questions. Please try again.")
        log.append("4) Quiz Master → Student: five practice questions are ready.")
        return {
            "lesson": lesson,
            "quiz": quiz,
            "plan": plan,
            "log": log,
            "student": student_name,
            "topic": topic,
            "level": level,
        }
    finally:
        await client.close()

async def evaluate_answers(session: dict, answers: str):
    if not session or not session.get("quiz"):
        raise ValueError("Start a lesson and generate the quiz first.")
    if not answers.strip():
        raise ValueError("Please enter your answers before submitting.")
    client = create_model_client()
    agents = create_agents(client)
    log = list(session.get("log", []))
    try:
        log.append("5) Student → Evaluator: answers submitted for assessment.")
        evaluation_text = await _ask(
            agents["evaluator"],
            f"Topic: {session['topic']}\nLesson:\n{session['lesson']}\n"
            f"Quiz JSON:\n{json.dumps(session['quiz'], ensure_ascii=False)}\n"
            f"Student answers:\n{answers}\nEvaluate using the required JSON schema."
        )
        evaluation = _extract_json(evaluation_text)
        log.append("6) Evaluator: answers checked and feedback prepared.")
        reteach = ""
        followup_quiz = None
        if float(evaluation.get("percentage", 0)) < 70 or evaluation.get("next_step") == "reteach":
            log.append("7) Evaluator → Explainer: weak concepts sent back for re-teaching.")
            weak = evaluation.get("weak_concepts", [])
            reteach = await _ask(
                agents["explainer"],
                f"The student needs targeted re-teaching. Topic: {session['topic']}. "
                f"Weak concepts: {weak}. Original lesson: {session['lesson']}. "
                "Explain only the weak areas differently, with a new example and a quick recap."
            )
            log.append("8) Explainer → Quiz Master: remedial explanation handed off.")
            followup_text = await _ask(
                agents["quiz_master"],
                f"Create exactly 3 follow-up questions in the same JSON schema, "
                f"but with 3 questions, based on this remedial teaching.\n{reteach}"
            )
            try:
                followup_quiz = _extract_json(followup_text)
            except (ValueError, json.JSONDecodeError):
                followup_quiz = {"title": "Follow-up practice", "raw": followup_text}
            log.append("9) Quiz Master: follow-up practice generated.")
        save_memory(
            session["student"], session["topic"],
            score=evaluation.get("percentage"),
            summary=evaluation.get("overall_feedback", "")
        )
        return evaluation, reteach, followup_quiz, log
    finally:
        await client.close()

def run_start_lesson(student_name, topic, level):
    return asyncio.run(start_lesson(student_name, topic, level))

def run_evaluate(session, answers):
    return asyncio.run(evaluate_answers(session, answers))
