FROM python:3.10

COPY ./ /DiscordBot
WORKDIR /DiscordBot

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]git 