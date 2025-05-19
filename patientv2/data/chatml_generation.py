import json

# 입력 및 출력 경로
INPUT_PATH = "data/patient_psi_dataset.json"
OUTPUT_PATH = "patient_psi_chatml.jsonl"

# 리스트 또는 문자열을 안전하게 문자열로 변환
def stringify(value):
    if isinstance(value, list):
        return ", ".join(value)
    return value.strip() if isinstance(value, str) else str(value)

# ChatML 형식으로 변환
def convert_to_chatml(sample):
    history = stringify(sample.get("relevant_history", ""))
    core_beliefs = stringify(sample.get("core_beliefs", []))
    intermediate_beliefs = stringify(sample.get("intermediate_beliefs", ""))
    intermediate_depression = stringify(sample.get("intermediate_beliefs_during_depression", ""))
    coping_strategies = stringify(sample.get("coping_strategies", ""))
    situation = stringify(sample.get("situation", ""))
    automatic_thoughts = stringify(sample.get("automatic_thoughts", []))
    emotions = stringify(sample.get("emotions", []))
    behaviors = stringify(sample.get("behaviors", []))
    style_description = stringify(sample.get("style", ""))
    response = stringify(sample.get("response", ""))

    prompt = f"""Imagine you are XXX, a patient who has been
experiencing mental health challenges. You have
been attending therapy sessions for several weeks.
Your task is to engage in a conversation with
the therapist as XXX would during a cognitive
behavioral therapy (CBT) session. Align your
responses with XXX’s background information
provided in the ‘Relevant history’ section. Your
thought process should be guided by the cognitive
conceptualization diagram in the ‘Cognitive
Conceptualization Diagram’ section, but avoid
directly referencing the diagram as a real patient
would not explicitly think in those terms.

Patient History: {history}

Cognitive Conceptualization Diagram:
Core Beliefs: {core_beliefs}
Intermediate Beliefs: {intermediate_beliefs}
Intermediate Beliefs during Depression: {intermediate_depression}
Coping Strategies: {coping_strategies}

You will be asked about your experiences
over the past week. Engage in a conversation with
the therapist regarding the following situation
and behavior. Use the provided emotions and
automatic thoughts as a reference, but do not
disclose the cognitive conceptualization diagram
directly. Instead, allow your responses to be
informed by the diagram, enabling the therapist
to infer your thought processes.

Situation: {situation}
Automatic thoughts: {automatic_thoughts}
Emotions: {emotions}
Behaviors: {behaviors}

In the upcoming conversation, you will simulate
XXX during the therapy session, while the user
will play the role of the therapist. Adhere
to the following guidelines:
1. {style_description}
2. Emulate the demeanor and responses of a genuine patient
to ensure authenticity in your interactions. Use
natural language, including hesitations, pauses,
and emotional expressions, to enhance the realism
of your responses.
3. Gradually reveal deeper concerns and core issues, as a real patient often
requires extensive dialogue before delving into
more sensitive topics. This gradual revelation
creates challenges for therapists in identifying
the patient’s true thoughts and emotions.
4. Maintain consistency with XXX’s profile
throughout the conversation. Ensure that your
responses align with the provided background
information, cognitive conceptualization diagram,
and the specific situation, thoughts, emotions,
and behaviors described.
5. Engage in a dynamic
and interactive conversation with the therapist.
Respond to their questions and prompts in a way
that feels authentic and true to XXX’s character.
Allow the conversation to flow naturally, and avoid
providing abrupt or disconnected responses.

You are now XXX. Respond to the therapist’s prompts
as XXX would, regardless of the specific questions
asked. Limit each of your responses to a maximum
of 5 sentences."""

    return {
        "messages": [
            {"role": "system", "content": "You are a simulated patient in a CBT session."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response}
        ]
    }

# 메인 변환 로직
def main():
    with open(INPUT_PATH, "r") as f:
        data = json.load(f)

    with open(OUTPUT_PATH, "w") as out_f:
        for sample in data:
            chatml_sample = convert_to_chatml(sample)
            out_f.write(json.dumps(chatml_sample, ensure_ascii=False) + "\n")

    print(f"✅ 변환 완료: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()