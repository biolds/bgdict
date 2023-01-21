# Dict creation

> git clone https://github.com/ilius/pyglossary.git
>
> python3 main.py freedict-eng-bul-2020.10.04.slob freedict-eng-bul-2020.10.04.json

# server install

> apt install python3-django python3-psycopg2 postgresql libjs-jquery uwsgi uwsgi-plugin-python3 python3-django-uwsgi
>
> su postgres -c "psql --command \"CREATE USER django WITH SUPERUSER PASSWORD 'django'\""
> su postgres -c "psql --command \"CREATE DATABASE django OWNER django\""
>
> python3 manage.py makemigrations
> python3 manage.py migrate
> python3 manage.py dict_import <dict.json>

# postgresql fulltext search

> git clone https://github.com/quasoft/postgres-tsearch-bulgarian.git
>
> cp bulgarian.* /usr/share/postgresql/13/tsearch_data/

Psql setup, needs to be run as the same PG user as the django app `psql -U django -d django -W`:

> CREATE TEXT SEARCH CONFIGURATION bulgarian (COPY = simple);
> CREATE TEXT SEARCH DICTIONARY bulgarian_ispell (
>     TEMPLATE = ispell,
>     DictFile = bulgarian,
>     AffFile = bulgarian,
>     StopWords = bulgarian
> );
> CREATE TEXT SEARCH DICTIONARY bulgarian_simple (
>     TEMPLATE = pg_catalog.simple,
>     STOPWORDS = bulgarian
> );
> ALTER TEXT SEARCH CONFIGURATION bulgarian ALTER MAPPING FOR asciiword, asciihword, hword, hword_part, word WITH bulgarian_ispell, bulgarian_simple;

# Systemd service

> # cat /etc/systemd/system/bgdict.service
> [Unit]
> Description=Django BGDict
> After=syslog.target
> 
> [Service]
> ExecStart=/bg-dict/run.sh
> RuntimeDirectory=bg-dict/
> Restart=always
> KillSignal=SIGQUIT
> Type=simple
> StandardError=syslog
> 
> [Install]
> WantedBy=multi-user.target
