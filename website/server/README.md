Server Setup
-------------------


I encourage you to use virtualenv to keep the environment clean. Under server, do

~~~
virtualenv .
source bin/activate
pip install django
python manage test flux
~~~

All tests, except libsbml, should pass.


