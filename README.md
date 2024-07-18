# Starnavi test task

## How to run the backend
1. Checkout the repo.
2. Install the requirements:
```bash
> pip install -r requirements.txt
```
3. Create an .env file in the /src dir.
4. Set the env varibles in the .env file, it should look something like this:
```
SECRET="..."  # A passphrase for the auth_backend
API_KEY="sk-proj-..."   # OpenAI API key
```
5. Run the `src/main.py` file.
6. Open `http://localhost:8000/docs` in your browser of choice.


## How to run the tests
Just use pytest.
```bash
(.venv) ~\PycharmProjects\starnavi test task git:[main]
pytest
======================================================================================== test session starts =========================================================================================
platform win32 -- Python 3.12.2, pytest-8.2.2, pluggy-1.5.0
rootdir: C:\Users\punch\PycharmProjects\starnavi test task
plugins: anyio-4.4.0
collected 23 items                                                                                                                                                                                    

test\test_auth.py ....                                                                                                                                                                          [ 17%]
test\test_comments.py ...........                                                                                                                                                               [ 65%]
test\test_posts.py ........     
```
