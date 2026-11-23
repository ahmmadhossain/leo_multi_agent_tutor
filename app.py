import json
import gradio as gr
from leo.tutor import run_start_lesson, run_evaluate

def begin(student, topic, level):
    try:
        session = run_start_lesson(student, topic, level)
        quiz_md = render_quiz(session["quiz"])
        log_md = "\n".join(f"- {item}" for item in session["log"])
        return session, session["lesson"], quiz_md, log_md, "Quiz ready. Answer all five questions below."
    except Exception as exc:
        return None, "", "", f"**Coordinator handled a problem:** {exc}", "Could not start session."

def submit(session, answers):
    try:
        evaluation, reteach, followup, log = run_evaluate(session, answers)
        feedback = render_evaluation(evaluation)
        if reteach:
            feedback += "\n\n## Targeted re-teaching\n" + reteach
        if followup:
            feedback += "\n\n## Follow-up practice\n" + render_quiz(followup)
        log_md = "\n".join(f"- {item}" for item in log)
        return feedback, log_md, "Evaluation complete. Your progress has been saved locally."
    except Exception as exc:
        return f"**Coordinator handled a problem:** {exc}", "", "Please correct the issue and try again."

def render_quiz(quiz):
    lines = [f"### {quiz.get('title', 'Practice Quiz')}"]
    for q in quiz.get("questions", []):
        lines.append(f"**{q.get('id', '')}. {q.get('question', '')}**")
        for option in q.get("options", []):
            lines.append(f"- {option}")
        lines.append("")
    return "\n".join(lines)

def render_evaluation(data):
    lines = [
        f"## Result: {data.get('score', '?')}/{data.get('max_score', 5)} "
        f"({data.get('percentage', '?')}%)",
        data.get("overall_feedback", "")
    ]
    for item in data.get("question_feedback", []):
        lines.append(
            f"\n**Q{item.get('id')}: {item.get('result', 'review')}** — "
            f"{item.get('feedback', '')}\n"
            f"Expected concept/answer: {item.get('expected_answer', '')}"
        )
    if data.get("weak_concepts"):
        lines.append("\n**Areas to improve:** " + ", ".join(data["weak_concepts"]))
    return "\n".join(lines)

with gr.Blocks(title="Leo — Multi-Agent AI Tutor", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# 🎓 Leo — Multi-Agent AI Tutor\n"
        "A team of AI agents that plans, teaches, quizzes, evaluates, and re-teaches."
    )
    session_state = gr.State(None)
    with gr.Row():
        student = gr.Textbox(label="Student name", placeholder="e.g. Alex")
        level = gr.Dropdown(["Beginner", "Intermediate", "Advanced"], value="Beginner", label="Learning level")
    topic = gr.Textbox(label="What would you like to learn?", placeholder="e.g. Python loops, photosynthesis, fractions")
    start_btn = gr.Button("Start lesson and generate quiz", variant="primary")
    status = gr.Markdown()
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Explainer's lesson")
            lesson_out = gr.Markdown()
        with gr.Column():
            gr.Markdown("## Quiz Master's questions")
            quiz_out = gr.Markdown()
    gr.Markdown("## Your answers")
    answers = gr.Textbox(
        label="Write answers numbered 1–5",
        lines=8,
        placeholder="1. ...\n2. ...\n3. ..."
    )
    submit_btn = gr.Button("Submit answers to Evaluator", variant="primary")
    evaluation_out = gr.Markdown()
    gr.Markdown("## Agent activity / handoff trace")
    activity_out = gr.Markdown()
    start_btn.click(
        begin, inputs=[student, topic, level],
        outputs=[session_state, lesson_out, quiz_out, activity_out, status]
    )
    submit_btn.click(
        submit, inputs=[session_state, answers],
        outputs=[evaluation_out, activity_out, status]
    )
    gr.Markdown(
        "---\n**Privacy:** Student learning history is stored locally in "
        "`data/student_memory.json`. Do not put sensitive personal information here."
    )

if __name__ == "__main__":
    demo.queue().launch()
