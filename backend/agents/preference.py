def get_output(client, model: str, context: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": (
                f"You are a Preference Agent. {context} "
                "Suggest food choices based on this student's healthy habits and diet in 1–2 sentences."
            )
        }]
    )
    return response.choices[0].message.content
