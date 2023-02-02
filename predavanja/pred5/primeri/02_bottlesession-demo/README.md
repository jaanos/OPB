bottlesession
=============

This project adds simple session management to Bottle Python.

To use this, just add the following import statement to any bottle project:
```python
from bottlesession import session
```

To initialize a session just create a new session object.
```python
sess = session()
```

You can also specify a secret key for Bottle to use when signing the cookie.
```python
sess = session('reallySecurePasskey')
```

If the user has already used a session on your server, he/she will automatically have their session variables placed back into the object, from file.

To add/update/read session variables, use the following methods.
```python
sess.set('user','name')
sess.read('user')
```

When you're done, make sure you close the session so that the variables get written to disk.
```python
sess.close()
```

When the user returns to your site, their session will be reloaded as soon as you initialize the 'session' object.