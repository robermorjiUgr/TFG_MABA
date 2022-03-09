FROM ubuntu:20.04

ENV PATH_DEPLOY=/home/django/webapps/sotsia/
ENV NAME_APP=supervisor_sotsia.conf 

RUN apt-get update

RUN apt-get install -y bash && \	
    apt-get install -y nano && \
    apt-get install -y software-properties-common && \
    apt-get install -y python3-setuptools && \
    apt-get install -y build-essential && \
    apt-get install -y python3-pip && \
    apt-get install -y python3-dev && \
    apt-get install -y git-core && \
    apt-get install -y build-essential autoconf libtool pkg-config python-opengl python-pil && \
    apt-get install -y python-pyrex   && \
    apt-get install -y   libgle3 python-dev libssl-dev && \
    apt-get install -y libexpat1 && \
    apt-get install -y ssl-cert && \
    apt-get install -y openssh-server && \
    apt-get install -y  libpq-dev && \
    apt-get install -y libffi-dev && \
    apt-get install -y nodejs && \
    apt-get install -y nginx && \
    apt-get install -y gunicorn && \
    apt-get install -y supervisor && \
    apt-get install -y virtualenv 


RUN useradd -m django

RUN mkdir -p ${PATH_DEPLOY}

WORKDIR ${PATH_DEPLOY}

COPY . ${PATH_DEPLOY}

RUN python3 -m virtualenv .

# RUN ${PATH_DEPLOY}/bin/activate

COPY requirements.txt .


RUN pip install -r requirements.txt && pip install gunicorn


COPY config/gunicorn_start ${PATH_DEPLOY}/bin/

RUN chmod u+x ${PATH_DEPLOY}/bin/gunicorn_start

COPY config/supervisor_sotsia.conf /etc/supervisor/conf.d/  

RUN mkdir -p ${PATH_DEPLOY}/logs

RUN touch ${PATH_DEPLOY}/logs/gunicorn_supervisor.log

COPY config/nginx_sotsia.conf /etc/nginx/sites-available/

RUN ln -s /etc/nginx/sites-available/nginx_sotsia.conf /etc/nginx/sites-enabled/nginx_sotsia.conf

RUN python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py collectstatic


CMD ['/usr/bin/supervisord']


