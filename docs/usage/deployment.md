# Deployment

## Install app
To perform the deployment, it is necessary to add the application, in the INSTALLED_APPS section of the settings.py of our project.
This app depend and use an other django app, **django-background-tasks**.
You need to install it before **djimporter**

For start this app manualy you need to exec:
```
python manager process_tasks
```

## Supervisor
For run this process in background you need to add a package to your system called **supervisor**.
In Debian it would be like this:
```
apt-get install supervisor
```
Then the file is copied:

```
cp docs/config/supervisord.conf
/etc/supervisor/supervisord.conf
```

In this file you have to change the command path
command= in the appropriate path where the initialization file is.

Finally you have to go to the file:
***
monitoring/cmd/start.sh
***

and modify the **HOME_PROJECT** variable accordingly. Notice that it depends on the **$HOME** variable and the user that is defined in supervisord.conf is www-data, so that variable will send us to a different place from where the project resides. That is why we have to correctly choose the place where we host the project or modify HOME_PROJECT correctly.
