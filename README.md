# Dict creation

```
git clone https://github.com/ilius/pyglossary.git

python3 main.py freedict-eng-bul-2020.10.04.slob freedict-eng-bul-2020.10.04.json
```

# server install

```
apt install python3-django python3-psycopg2 postgresql

su postgres -c "psql --command \"CREATE USER django WITH SUPERUSER PASSWORD 'django'\""
su postgres -c "psql --command \"CREATE DATABASE django OWNER django\""
 
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py import_dict <dict.json>
```

# postgresql fulltext search

```
git clone https://github.com/quasoft/postgres-tsearch-bulgarian.git

cp bulgarian.* /usr/share/postgresql/11/tsearch_data/
```

psql:

```
CREATE TEXT SEARCH CONFIGURATION bulgarian (COPY = simple);
CREATE TEXT SEARCH DICTIONARY bulgarian_ispell (
    TEMPLATE = ispell,
    DictFile = bulgarian, 
    AffFile = bulgarian, 
    StopWords = bulgarian
);
CREATE TEXT SEARCH DICTIONARY bulgarian_simple (
    TEMPLATE = pg_catalog.simple,
    STOPWORDS = bulgarian
);
ALTER TEXT SEARCH CONFIGURATION bulgarian ALTER MAPPING FOR asciiword, asciihword, hword, hword_part, word WITH bulgarian_ispell, bulgarian_simple;
```

