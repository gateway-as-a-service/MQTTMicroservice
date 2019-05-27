# Our base image
FROM python:3-onbuild

ENV APP_ENV=docker

# Run application
CMD ["python", "./main.py"]
