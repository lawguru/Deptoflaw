npm install
ln -s $(which python3.12) /usr/local/bin/python
ln -s $(which pip) /usr/local/bin/pip
npm run venv
npm run activate
npm run pip-install
npm run collectstatic
npm run scss