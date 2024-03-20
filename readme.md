# Flask Invoice Generator

Create Python virtual env:

Linux
```
python -m virtualenv env
```
Windows
```
python -m venv env
```

Activate vritual env:

Linux

```
source env/bin/activate
```
Windows

```
env/scripts/activate
```

Install requirements.txt
```
pip install -r requirements.txt
```

Run on Linux:
```
python app.py
```
Run on Windows with PS:
```
python app.py
```

Docker:
Build docker image:
```
docker build -t [image_name] .
```
Run docker container on port 5001 (docker container expose port 5001):
```
docker run -d -p 5001:5001 [image_name]
```

App runs on localhost:5001
