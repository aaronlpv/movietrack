# Running this application
To run this application Python 3, Django and the Python Pillow library are required.  

The manage.py file uses a UNIX shebang with the 'python' command.  
If you do not use a UNIX-like system or if your system uses a different  
command for Python 3, you should put that command before manage.py in  
the following commands.

```bash
$ ./manage.py runserver
```

You will get a message about unapplied migrations.  
Interrupt the server with Ctrl+C.

```bash
$ ./manage.py migrate
$ ./manage.py runserver
```

You can now access the application by going to the link
the server gives you.

The next time you run the server just runserver will suffice
as the migrations are already applied.

## Database
Initially the movie database will be empty.  
You can populate it by logging in with any account  
and navigating to /api/omdb-debug?n=<amount\>.  
This will import <amount\> movies from the top 250 rated movies on IMDB.  
This can take a while however, we recommend importing no more than 50.


# Existing instance
An existing instance of the application can be found at
<https://aaronl.pythonanywhere.com>.  
Do note that importing movies via the OMDB API will not work here.  
This is due to a limitation in the free tier of PythonAnywhere,  
which only allows access to a list of pre-approved APIs.

## Accounts
A test user account is available.  
Its username is "TestUser" (case sensitive),
its password is "testpassword".

Feel free to create more accounts.
