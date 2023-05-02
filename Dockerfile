# syntax=docker/dockerfile:1

FROM python:3.10-slim
RUN useradd --create-home vmuser
USER vmuser
WORKDIR /home/vmuser/app
COPY /vm_uncovered requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt
ENV FORWARDED_ALLOW_IPS="*"
CMD [ "python3", "-m", "uvicorn", "--host", "0.0.0.0", "--proxy-headers", "--access-log", "app:app" ]
