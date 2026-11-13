# Back-end-Development-Capstone

Project: Band website — IBM Back-end Application Development Capstone.

Django frontend connects to the Pictures and Songs Flask microservices. Includes signup/login/logout, song lyrics modals, photos, concert listings and authenticated attendance updates.

## Local setup

```sh
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver 0.0.0.0:8000
```

Configure `SONGS_SERVICE_URL` and `PICTURES_SERVICE_URL` without trailing slashes. Defaults are local ports 5082 and 5081. Configure `DJANGO_SECRET_KEY` to a private random value that persists across restarts, `DJANGO_ALLOWED_HOSTS` to a comma-separated host list, and `DJANGO_DEBUG=0` outside local development. The included runserver command follows the teaching lab and is not a production hosting configuration. No default administrator is created; use `python manage.py createsuperuser` interactively.

Verified locally: migrations, 5 authentication/attendance tests and live integration with both microservices. Cloud deployment is pending.

Based on IBM Skills Network's sfvih template. OpenAI Codex assisted implementation and debugging; learner review and understanding are required before submission.
