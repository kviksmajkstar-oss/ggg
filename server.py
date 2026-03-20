import hashlib
import json
import secrets
import sqlite3
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'nomercy.db'
HOST = '127.0.0.1'
PORT = 8000
SESSION_COOKIE = 'nomercy_session'
STATIC_FILES = {
    '/': 'index.html',
    '/index.html': 'index.html',
    '/styles.css': 'styles.css',
    '/script.js': 'script.js',
}
CONTENT_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
}


def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 200_000)
    return f'{salt}${digest.hex()}'


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split('$', 1)
    candidate = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 200_000)
    return secrets.compare_digest(candidate.hex(), digest)


def init_db():
    conn = db_connect()
    conn.executescript(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            handle TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            bio TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'В онлайне',
            theme TEXT NOT NULL DEFAULT 'dark',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS likes (
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            PRIMARY KEY(user_id, post_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(post_id) REFERENCES posts(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(recipient_id) REFERENCES users(id)
        );
        '''
    )
    user_count = conn.execute('SELECT COUNT(*) AS count FROM users').fetchone()['count']
    if user_count == 0:
        users = [
            ('Руслан Kviksmajk', 'kviksmajk', 'nomercy123', 'Музыкант, автор kviksmajkmusic и разработчик NOMERCY.', 'В онлайне', 'dark'),
            ('Lisa Stone', 'lisastone', 'design123', 'UI / motion designer в creator-продуктах.', 'В эфире', 'light'),
            ('Dan North', 'dannorth', 'product123', 'Product strategist и человек про social UX.', 'На связи', 'dark'),
            ('Mira Ray', 'miraray', 'arcade123', 'Ведёт игровые комнаты и community events.', 'В студии', 'dark'),
        ]
        for name, handle, password, bio, status, theme in users:
            conn.execute(
                'INSERT INTO users (name, handle, password_hash, bio, status, theme) VALUES (?, ?, ?, ?, ?, ?)',
                (name, handle, hash_password(password), bio, status, theme),
            )

        posts = [
            (1, 'Привет! Я Руслан Kviksmajk — музыкант, автор kviksmajkmusic и разработчик NOMERCY. Это уже не макет, а реально работающий локальный сайт соцсети с аккаунтами, постами и чатами.'),
            (2, 'Очень круто, что теперь в NOMERCY можно реально зарегистрироваться, войти и публиковать посты.'),
            (3, 'Рабочий backend делает соцсеть совсем по-другому ощущаемой: теперь это уже настоящий продуктовый прототип.'),
        ]
        for user_id, content in posts:
            conn.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))

        messages = [
            (2, 1, 'Руслан, NOMERCY стал намного ближе к реальному продукту.'),
            (1, 2, 'Да, теперь тут есть настоящие аккаунты, посты и живая переписка.'),
            (3, 1, 'Следующий шаг — notifications и подписки.'),
            (1, 3, 'Согласен, но база уже рабочая.'),
        ]
        for sender_id, recipient_id, content in messages:
            conn.execute(
                'INSERT INTO messages (sender_id, recipient_id, content) VALUES (?, ?, ?)',
                (sender_id, recipient_id, content),
            )
    conn.commit()
    conn.close()


def serialize_user(row):
    return {
        'id': row['id'],
        'name': row['name'],
        'handle': row['handle'],
        'bio': row['bio'],
        'status': row['status'],
        'theme': row['theme'],
    }


def fetch_current_user(conn, token):
    if not token:
        return None
    row = conn.execute(
        '''
        SELECT users.* FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
        ''',
        (token,),
    ).fetchone()
    return row


def fetch_feed(conn, viewer_id=None):
    rows = conn.execute(
        '''
        SELECT posts.id, posts.content, posts.created_at, users.id AS user_id, users.name, users.handle,
               users.status,
               COUNT(DISTINCT likes.user_id) AS like_count,
               MAX(CASE WHEN likes.user_id = ? THEN 1 ELSE 0 END) AS liked
        FROM posts
        JOIN users ON users.id = posts.user_id
        LEFT JOIN likes ON likes.post_id = posts.id
        GROUP BY posts.id
        ORDER BY posts.id DESC
        ''',
        (viewer_id or -1,),
    ).fetchall()
    return [
        {
            'id': row['id'],
            'content': row['content'],
            'created_at': row['created_at'],
            'author': {
                'id': row['user_id'],
                'name': row['name'],
                'handle': row['handle'],
                'status': row['status'],
            },
            'likes': row['like_count'],
            'liked': bool(row['liked']),
        }
        for row in rows
    ]


def fetch_users(conn):
    rows = conn.execute('SELECT * FROM users ORDER BY id').fetchall()
    return [serialize_user(row) for row in rows]


def fetch_chat_overview(conn, current_user_id):
    others = conn.execute('SELECT * FROM users WHERE id != ? ORDER BY name', (current_user_id,)).fetchall()
    result = []
    for other in others:
        last_message = conn.execute(
            '''
            SELECT content, created_at FROM messages
            WHERE (sender_id = ? AND recipient_id = ?) OR (sender_id = ? AND recipient_id = ?)
            ORDER BY id DESC LIMIT 1
            ''',
            (current_user_id, other['id'], other['id'], current_user_id),
        ).fetchone()
        result.append(
            {
                **serialize_user(other),
                'last_message': last_message['content'] if last_message else 'Напишите первым',
                'last_message_at': last_message['created_at'] if last_message else None,
            }
        )
    return result


def fetch_messages(conn, current_user_id, peer_id):
    rows = conn.execute(
        '''
        SELECT * FROM messages
        WHERE (sender_id = ? AND recipient_id = ?) OR (sender_id = ? AND recipient_id = ?)
        ORDER BY id
        ''',
        (current_user_id, peer_id, peer_id, current_user_id),
    ).fetchall()
    return [
        {
            'id': row['id'],
            'sender_id': row['sender_id'],
            'recipient_id': row['recipient_id'],
            'content': row['content'],
            'created_at': row['created_at'],
        }
        for row in rows
    ]


class NOMERCYHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, file_path: Path):
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', CONTENT_TYPES[file_path.suffix])
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def parse_json(self):
        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length) if length else b'{}'
        return json.loads(raw.decode('utf-8'))

    def get_session_token(self):
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None
        jar = cookies.SimpleCookie()
        jar.load(cookie_header)
        morsel = jar.get(SESSION_COOKIE)
        return morsel.value if morsel else None

    def get_current_user(self, conn):
        return fetch_current_user(conn, self.get_session_token())

    def require_auth(self, conn):
        user = self.get_current_user(conn)
        if not user:
            self.send_json(401, {'error': 'Требуется вход в аккаунт'})
            return None
        return user

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in STATIC_FILES:
            return self.send_file(BASE_DIR / STATIC_FILES[parsed.path])

        conn = db_connect()
        try:
            if parsed.path == '/api/bootstrap':
                user = self.get_current_user(conn)
                payload = {
                    'current_user': serialize_user(user) if user else None,
                    'users': fetch_users(conn),
                    'feed': fetch_feed(conn, user['id'] if user else None),
                }
                if user:
                    payload['chats'] = fetch_chat_overview(conn, user['id'])
                return self.send_json(200, payload)

            if parsed.path == '/api/messages':
                user = self.require_auth(conn)
                if not user:
                    return
                peer_id = int(parse_qs(parsed.query).get('peer_id', ['0'])[0])
                return self.send_json(200, {'messages': fetch_messages(conn, user['id'], peer_id)})

            self.send_json(404, {'error': 'Не найдено'})
        finally:
            conn.close()

    def do_POST(self):
        parsed = urlparse(self.path)
        conn = db_connect()
        try:
            if parsed.path == '/api/register':
                data = self.parse_json()
                name = data.get('name', '').strip()
                handle = data.get('handle', '').strip().lower()
                password = data.get('password', '').strip()
                if not name or not handle or not password:
                    return self.send_json(400, {'error': 'Заполни имя, логин и пароль'})
                exists = conn.execute('SELECT id FROM users WHERE handle = ?', (handle,)).fetchone()
                if exists:
                    return self.send_json(400, {'error': 'Такой логин уже занят'})
                conn.execute(
                    'INSERT INTO users (name, handle, password_hash, bio, status, theme) VALUES (?, ?, ?, ?, ?, ?)',
                    (name, handle, hash_password(password), 'Новый пользователь NOMERCY.', 'В онлайне', 'dark'),
                )
                conn.commit()
                return self.send_json(201, {'ok': True})

            if parsed.path == '/api/login':
                data = self.parse_json()
                handle = data.get('handle', '').strip().lower()
                password = data.get('password', '').strip()
                user = conn.execute('SELECT * FROM users WHERE handle = ?', (handle,)).fetchone()
                if not user or not verify_password(password, user['password_hash']):
                    return self.send_json(401, {'error': 'Неверный логин или пароль'})
                token = secrets.token_hex(24)
                conn.execute('INSERT INTO sessions (token, user_id) VALUES (?, ?)', (token, user['id']))
                conn.commit()
                headers = {'Set-Cookie': f'{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax'}
                return self.send_json(200, {'ok': True}, headers)

            if parsed.path == '/api/logout':
                token = self.get_session_token()
                if token:
                    conn.execute('DELETE FROM sessions WHERE token = ?', (token,))
                    conn.commit()
                headers = {'Set-Cookie': f'{SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax'}
                return self.send_json(200, {'ok': True}, headers)

            user = self.require_auth(conn)
            if not user:
                return

            if parsed.path == '/api/profile':
                data = self.parse_json()
                name = data.get('name', user['name']).strip()
                bio = data.get('bio', user['bio']).strip()
                status = data.get('status', user['status']).strip() or 'В онлайне'
                theme = data.get('theme', user['theme']).strip() or 'dark'
                conn.execute(
                    'UPDATE users SET name = ?, bio = ?, status = ?, theme = ? WHERE id = ?',
                    (name, bio, status, theme, user['id']),
                )
                conn.commit()
                updated = conn.execute('SELECT * FROM users WHERE id = ?', (user['id'],)).fetchone()
                return self.send_json(200, {'user': serialize_user(updated)})

            if parsed.path == '/api/posts':
                data = self.parse_json()
                content = data.get('content', '').strip()
                if not content:
                    return self.send_json(400, {'error': 'Пост не может быть пустым'})
                conn.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user['id'], content))
                conn.commit()
                return self.send_json(201, {'feed': fetch_feed(conn, user['id'])})

            if parsed.path.startswith('/api/posts/') and parsed.path.endswith('/like'):
                post_id = int(parsed.path.split('/')[3])
                liked = conn.execute(
                    'SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?',
                    (user['id'], post_id),
                ).fetchone()
                if liked:
                    conn.execute('DELETE FROM likes WHERE user_id = ? AND post_id = ?', (user['id'], post_id))
                else:
                    conn.execute('INSERT INTO likes (user_id, post_id) VALUES (?, ?)', (user['id'], post_id))
                conn.commit()
                return self.send_json(200, {'feed': fetch_feed(conn, user['id'])})

            if parsed.path == '/api/messages':
                data = self.parse_json()
                peer_id = int(data.get('peer_id', 0))
                content = data.get('content', '').strip()
                if not peer_id or not content:
                    return self.send_json(400, {'error': 'Нужно выбрать собеседника и ввести сообщение'})
                conn.execute(
                    'INSERT INTO messages (sender_id, recipient_id, content) VALUES (?, ?, ?)',
                    (user['id'], peer_id, content),
                )
                conn.commit()
                return self.send_json(
                    201,
                    {
                        'messages': fetch_messages(conn, user['id'], peer_id),
                        'chats': fetch_chat_overview(conn, user['id']),
                    },
                )

            self.send_json(404, {'error': 'Не найдено'})
        finally:
            conn.close()


if __name__ == '__main__':
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), NOMERCYHandler)
    print(f'NOMERCY running on http://{HOST}:{PORT}')
    server.serve_forever()
