FROM tiangolo/uwsgi-nginx-flask:python3.6

# Dependencies for Couchbase
RUN wget -O - http://packages.couchbase.com/ubuntu/couchbase.key | apt-key add -
RUN echo "deb http://packages.couchbase.com/ubuntu stretch stretch/main" > /etc/apt/sources.list.d/couchbase.list
RUN apt-get update && apt-get install -y libcouchbase-dev build-essential

# Also install fastapi to get the jsonable_encoder
RUN pip install flask==1.0.2 flask-cors==3.0.7 raven[flask] celery==4.2.1 passlib[bcrypt]==1.7.1 flask-apispec==0.7.0 apispec==0.39.0 marshmallow==2.18.0 flask-jwt-extended==3.17.0 tenacity==5.0.3 requests==2.21.0 couchbase emails==0.5.15 fastapi==0.2.0 pydantic==0.18.2

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter notebook --ip=0.0.0.0 --allow-root
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyter ; fi"
EXPOSE 8888

COPY ./app /app
WORKDIR /app/

ENV STATIC_PATH /app/app/static
ENV STATIC_INDEX 1

EXPOSE 80
