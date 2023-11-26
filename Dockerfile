FROM python:3.11
COPY . /chester_project
WORKDIR /chester_project 
RUN pip install -r requirements.txt 
EXPOSE 8040
CMD ["python", "./index.py"]