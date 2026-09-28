def build_history(session):

    history = ""

    for msg in session["conversation"]:

        history += (

            f'{msg["role"]}: '

            f'{msg["message"]}\n'

        )

    return history