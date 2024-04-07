FROM python:3.10-alpine3.15
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN echo "0 8 * * * /app/daily_mail.py" >> /var/spool/cron/crontabs/root
COPY . .
