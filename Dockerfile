# pull official base image
FROM python:3.10.6-alpine

# set work directory
WORKDIR /usr/src/app


# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
    

# copy project
COPY . .

# expose port 8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]