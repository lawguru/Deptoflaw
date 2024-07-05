cd ..
npm install
npm run scss

cd project
python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python3.12 manage.py collectstatic