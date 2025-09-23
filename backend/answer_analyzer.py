import json




def analyze_answer_with_ai(answer, question, groq_client, model="llama-3.3-70b-versatile"):
    prompt = (
        f"Question: {question}\n"
        f"Candidate's Answer: {answer}\n"
        "As an HR interviewer, analyze this answer and provide:\n"
        "1. A score from 1 to 10\n"
        "2. A brief justification\n"
        "3. The category this question falls under (technical, communication, analytical, leadership, problem_solving)\n"
        "Respond in JSON: {\"score\": <score>, \"justification\": \"...\", \"category\": \"...\"}"
    )
    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.3,
        n=1,
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result["score"], result["justification"], result.get("category", "general")
    except Exception:
        return None, "Unable to analyze response at this time.", "general"


