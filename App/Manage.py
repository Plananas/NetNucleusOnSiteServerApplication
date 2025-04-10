import click
import requests

@click.command()
@click.argument("message")
def send(message):
    response = requests.post(
        "http://localhost:5000/admin/command",
        json={"message": message}
    )
    print(response.json())

if __name__ == "__main__":
    send()
