FROM python:3.12-slim-bookworm

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y xz-utils git && pip install PyGithub

ADD release_tar.py /release_tar.py

ENTRYPOINT ["python", "/release_tar.py"]
