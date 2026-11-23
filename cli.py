from leo.tutor import run_start_lesson, run_evaluate

def main():
    print("\n=== Leo: Multi-Agent AI Tutor (CLI) ===")
    student = input("Student name: ").strip()
    topic = input("Topic to learn: ").strip()
    level = input("Level [Beginner/Intermediate/Advanced] (default Beginner): ").strip() or "Beginner"
    try:
        session = run_start_lesson(student, topic, level)
        print("\n--- Explainer ---\n", session["lesson"])
        print("\n--- Quiz Master ---")
        for q in session["quiz"]["questions"]:
            print(f"\n{q['id']}. {q['question']}")
            for opt in q.get("options", []):
                print("  ", opt)
        answers = input("\nEnter your numbered answers (1–5):\n")
        result, reteach, followup, log = run_evaluate(session, answers)
        print("\n--- Evaluator feedback ---\n", result)
        if reteach:
            print("\n--- Re-teaching ---\n", reteach)
        if followup:
            print("\n--- Follow-up quiz ---\n", followup)
        print("\n--- Agent handoffs ---")
        print("\n".join(log))
    except Exception as exc:
        print(f"\nLeo Coordinator: I couldn't complete that step. Details: {exc}")

if __name__ == "__main__":
    main()
