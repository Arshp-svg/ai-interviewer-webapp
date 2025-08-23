import json
import re




def analyze_answer_with_ai(answer, question, groq_client, model="llama-3.3-70b-versatile"):
    prompt = (
        f"Question: {question}\n"
        f"Candidate's Answer: {answer}\n"
        "As an HR interviewer, evaluate the answer in four categories: Communication, Technical, Problem Solving, and Confidence. "
        "For each category, rate from 1 to 10 and provide a brief justification. "
        "Respond in JSON format as follows:\n"
        "{"
        "\"Communication\": {\"score\": <score>, \"justification\": \"...\"}, "
        "\"Technical\": {\"score\": <score>, \"justification\": \"...\"}, "
        "\"Problem_Solving\": {\"score\": <score>, \"justification\": \"...\"}, "
        "\"Confidence\": {\"score\": <score>, \"justification\": \"...\"}"
        "}"
    )
        
    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3,
        n=1,
    )
    content = response.choices[0].message.content
    print(content)  # For debugging

    # Extract JSON block using regex
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            result = json.loads(json_str)
            return result
        except Exception as e:
            print("JSON parsing error:", e)
            return None
    else:
        print("No JSON found in response.")
        return None


