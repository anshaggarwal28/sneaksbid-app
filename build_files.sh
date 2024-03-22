echo "BUILD START"
python3.9 -m pip install -r requirements.txt
python3.9 -m pip install -r Django
python3.9 -m pip install -r dj-stripe
python3.9 manage.py collectstatic --noinput --clear
echo "BUILD END"