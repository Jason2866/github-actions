FROM python:3.12-slim-bookworm

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Mark the `/github/workspace` directory as "safe" for Git operations.
RUN git config --system --add safe.directory /github/workspace
RUN git config --global pull.ff only

RUN apt-get update && apt-get install -y p7zip-full git && pip install PyGithub

ADD release_zips.py /release_zips.py

ENTRYPOINT ["python", "/release_zips.py"]
