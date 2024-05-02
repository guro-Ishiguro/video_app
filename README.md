<div id="top"></div>

## プロジェクトについて

動画投稿アプリ

### 構成

<pre>
.
├── .env
├── .gitignore
├── README.md
├── main
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations
│   ├── models.py
│   ├── storage.py
│   ├── templates
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
└── video_app
    ├── __init__.py
    ├── asgi.py
    ├── settings
    ├── urls.py
    └── wsgi.py
</pre>

### 環境

| 言語・フレームワーク  | バージョン |
| --------------------- | ---------- |
| Python                | 3.11.4     |
| Django                | 5.0.1      |

### ローカルでのプロジェクトの作成と起動

```bash
git clone https://github.com/guro-Ishiguro/video_app.git
cd video_app
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```