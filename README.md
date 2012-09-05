EggPotaLog
==========

Simple Django on Appengine blogging tool.

To run locally:

0.  get GAE SDK enviroment(https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)

1.  git clone git://github.com/aklapcin/EggPotaLog.git

2.  download django 1.4 and put django dir in lib

3.  run: <path to sdk>/dev_appenserver.py <project directory>

4.  in settings.py put in ADMINS_EMAILS your email(you can register only with it)

5.  go to http://localhost:8080/admin/register

To deploy:

0.  create ne application id (http://appengine.google.com)

1.  put your application id on the top of app.yaml file(application: <your application id>)

2.  in settings.py put in ADMINS_EMAILS your email(you can register only with it)

3.  <path to sdk>/appcfg.py update <project dir>

4.  go to http://<your application id>.appspot.com/

Features:
---------
* Creating, edititng, deleting posts
* Admin dashboard with list of all created posts
* Publishing and unpublishing created posts
