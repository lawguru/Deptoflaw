python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements.txt 
python3.12 manage.py collectstatic
python3.12 manage.py makemigrations
python3.12 manage.py migrate
python3.12 manage.py loaddata database.json