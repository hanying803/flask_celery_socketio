FROM python:3
EXPOSE 8000
WORKDIR /opt/project
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /opt/project
CMD ["sh","-c","supervisord -c supervisor.conf"]