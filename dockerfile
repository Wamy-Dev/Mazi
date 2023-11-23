FROM python:3.8-alpine
WORKDIR /Mazi
COPY . .

RUN apk update && apk add --no-cache git gcc libffi-dev python3-dev libc-dev linux-headers
RUN pip install --no-cache-dir -r requirements.txt
ENV CLIENTTOKEN=
CMD ["python", "bot.py"]
