# uottahack8

Instructions for running server

# Windows

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
cd frontend
npm install
npm run build
```

# Linux

```
python3 -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
python3 app.py
cd frontend
npm install
npm run build
```
## Docker Stuff

```
docker build -t ai .
docker run -p 5000:5000 ai
```

Go to `localhost:5000` in your browser ;]



## the cool way of running it:
sam run
python app_sam.py
cd frontend
npm run dev