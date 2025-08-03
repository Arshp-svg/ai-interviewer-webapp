import json




def analyze_answer_with_ai(answer, question, groq_client, model="llama-3.3-70b-versatile"):
    prompt = (
        f"Question: {question}\n"
        f"Candidate's Answer: {answer}\n"
        "As an HR interviewer, rate the answer from 1 to 10 and provide a brief justification. "
        "Respond in JSON: {\"score\": <score>, \"justification\": \"...\"}"
    )
    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.3,
        n=1,
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result["score"], result["justification"]
    except Exception:
        return None, "Could not parse AI response."


