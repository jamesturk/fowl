rm fowl.db
./manage.py syncdb
./manage.py loaddata testdata
echo "%run setup_league.py" | ./manage.py shell
