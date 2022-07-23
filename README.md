## Yatube

Yatube is a social network where users can keep their personal diaries.

### Overview

In general, the site allows users to create their own page, subscribe to the pages of other users and form a news feed from subscriptions.

Furthermore, users can view the pages of all other authors and leave comments on the entries. At the same time, posts can be attributed to different groups, which allows users to find authors by interests.

Authorized users can also fully edit all their posts and comments.

### Technologies

- Python 3.9.5
- Django

### Installation and launch

Clone the repository and go to it using the command line:

```bash
git clone 
```

```bash
cd yatube
```

Create and activate a virtual environment:

Windows:

```bash
py -3 -m venv env
```

```bash
. venv/Scripts/activate 
```

```bash
py -m pip install --upgrade pip
```

macOS/Linux:

```bash
python3 -m venv .venv
```

```bash
source env/bin/activate
```

```bash
python3 -m pip install --upgrade pip
```

Install dependencies from a file requirements.txt:

```bash
pip install -r requirements.txt
```

Make migrations:

Windows: 

```bash
py manage.py migrate
```

macOS/Linux:

```bash
python3 manage.py migrate
```

Launch:

Windows:

```bash
py manage.py runserver
```

macOS/Linux:

```bash
python3 manage.py runserver
```

### Project status 

At the moment, it is planned to redesign the site to bring it to a more modern and presentable look.

### License

MIT
