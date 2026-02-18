def get_output(client, model: str, context: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": (
                f"You are a Logistics Agent. {context} "
                "Suggest a healthy breakfast and a commute route for this student in 1–2 sentences."
            )
        }]
    )
    return response.choices[0].message.content
