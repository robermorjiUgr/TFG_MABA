
#!/bin/sh

app_supervisor=api_cloud_app

service supervisor start

chmod u+x run.sh

supervisorctl restart $app_supervisor

service nginx start
