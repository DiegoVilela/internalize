# Internalize

This project is an exercise to apply the concepts of the Django web
framework and Python.

The purpose of the app is to ease the transit of configuration
item data between an IT managed services provider (MSP) and
its clients.

## Workflow

1. Once on the homepage, the client needs to register into the system.
2. The MSP approves the user attaching a client to it.
3. Once logged in, the approved user can manage its company's
   configuration items data and choose the ones that must be monitored.
4. From this point, the MSP has an updated list of configuration items
   with all information needed to manage them.


## Live Demo

You can access it with the following credentials.

| username | password | login page |
| -------- | -------- | -----------|
| admin | UnQt5uGgjErbwkN | [for admins][2]
| client_a_user@example.com | UnQt5uGgjErbwkN | [for users][1]
| client_b_user@example.com | UnQt5uGgjErbwkN | [for users][1]

[1]: https://secure-forest-64714.herokuapp.com/cis/cis/0/
[2]: https://secure-forest-64714.herokuapp.com/admin/

## Heroku Setup
1. Create a `Procfile` at the root of the project with the following:
    ```
    web: gunicorn myproject.wsgi
    ```
2. `pip install gunicorn`
3. `pip install django-heroku`
4. `pip install whitenoise`
5. Add the following to `settings.py`:
    - At the top:
      ```python
      import django_heroku
      ```
    - At the bottom:
      ```python
      # Activate Django-Heroku.
      django_heroku.settings(locals())
      ```
    - For static assets:
      ```python
      STATIC_ROOT = BASE_DIR / 'staticfiles'
      STATIC_URL = '/static/'

      # Extra places for collectstatic to find static files.
      STATICFILES_DIRS = (BASE_DIR / 'static',)
      ```
    - WhiteNoise to serve static files in production:
      ```python
      MIDDLEWARE = [
         # Simplified static file serving.
         # https://warehouse.python.org/project/whitenoise/
         'whitenoise.middleware.WhiteNoiseMiddleware',
         ...
      ```
    - If you’d like gzip functionality enabled:
      ```python
      STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
      ```

Source: <https://devcenter.heroku.com/categories/working-with-django>