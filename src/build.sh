ln -s $(which python3.12) /usr/local/bin/python
python -m venv venv
source venv/bin/activate
pip install -r ./project/requirements.txt
npm install
npm run collectstatic
npm run scss