def get_output(client, model: str, context: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": (
                f"You are a Schedule Agent. {context} "
                "Generate today's academic priorities for this student in 1–2 sentences."
            )
        }]
    )
    return response.choices[0].message.content
