const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { URL } = require('url');

const HOST = '127.0.0.1';
const PORT = 8000;
const SESSION_COOKIE = 'nomercy_session';
const DATA_PATH = path.join(__dirname, 'nomercy-data.json');
const STATIC_FILES = {
  '/': 'index.html',
  '/index.html': 'index.html',
  '/styles.css': 'styles.css',
  '/script.js': 'script.js',
};
const CONTENT_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
};

function now() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19);
}

function createPasswordHash(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 200000, 32, 'sha256').toString('hex');
  return `${salt}$${hash}`;
}

function verifyPassword(password, stored) {
  const [salt, original] = stored.split('$');
  const hash = crypto.pbkdf2Sync(password, salt, 200000, 32, 'sha256').toString('hex');
  return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), Buffer.from(original, 'hex'));
}

function seedData() {
  return {
    nextUserId: 5,
    nextPostId: 4,
    nextMessageId: 5,
    users: [
      { id: 1, name: 'Руслан Kviksmajk', handle: 'kviksmajk', password_hash: createPasswordHash('nomercy123'), bio: 'Музыкант, автор kviksmajkmusic и разработчик NOMERCY.', status: 'В онлайне', theme: 'dark', created_at: now() },
      { id: 2, name: 'Lisa Stone', handle: 'lisastone', password_hash: createPasswordHash('design123'), bio: 'UI / motion designer в creator-продуктах.', status: 'В эфире', theme: 'light', created_at: now() },
      { id: 3, name: 'Dan North', handle: 'dannorth', password_hash: createPasswordHash('product123'), bio: 'Product strategist и человек про social UX.', status: 'На связи', theme: 'dark', created_at: now() },
      { id: 4, name: 'Mira Ray', handle: 'miraray', password_hash: createPasswordHash('arcade123'), bio: 'Ведёт игровые комнаты и community events.', status: 'В студии', theme: 'dark', created_at: now() },
    ],
    sessions: [],
    posts: [
      { id: 1, user_id: 1, content: 'Привет! Я Руслан Kviksmajk — музыкант, автор kviksmajkmusic и разработчик NOMERCY. Теперь проект можно запускать без Python — через Node.js.', created_at: now() },
      { id: 2, user_id: 2, content: 'NOMERCY уже реально работает как локальная соцсеть: аккаунты, посты, лайки, переписка.', created_at: now() },
      { id: 3, user_id: 3, content: 'Удобно, что теперь запуск на Windows не упирается в отсутствие Python.', created_at: now() },
    ],
    likes: [],
    messages: [
      { id: 1, sender_id: 2, recipient_id: 1, content: 'Руслан, Node-версия решает проблему запуска на Windows.', created_at: now() },
      { id: 2, sender_id: 1, recipient_id: 2, content: 'Да, теперь можно запускать NOMERCY без Python.', created_at: now() },
      { id: 3, sender_id: 3, recipient_id: 1, content: 'Это намного удобнее для локальных демо.', created_at: now() },
      { id: 4, sender_id: 1, recipient_id: 3, content: 'Согласен — меньше барьеров для запуска.', created_at: now() },
    ],
  };
}

function ensureDataFile() {
  if (!fs.existsSync(DATA_PATH)) {
    fs.writeFileSync(DATA_PATH, JSON.stringify(seedData(), null, 2));
  }
}

function readData() {
  ensureDataFile();
  return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'));
}

function writeData(data) {
  fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
}

function parseCookies(cookieHeader = '') {
  return cookieHeader
    .split(';')
    .map((part) => part.trim())
    .filter(Boolean)
    .reduce((acc, pair) => {
      const [key, ...rest] = pair.split('=');
      acc[key] = rest.join('=');
      return acc;
    }, {});
}

function serializeUser(user) {
  return {
    id: user.id,
    name: user.name,
    handle: user.handle,
    bio: user.bio,
    status: user.status,
    theme: user.theme,
  };
}

function getCurrentUser(req, data) {
  const cookies = parseCookies(req.headers.cookie);
  const token = cookies[SESSION_COOKIE];
  if (!token) {
    return null;
  }
  const session = data.sessions.find((item) => item.token === token);
  if (!session) {
    return null;
  }
  return data.users.find((user) => user.id === session.user_id) || null;
}

function buildFeed(data, viewerId = null) {
  return [...data.posts]
    .sort((a, b) => b.id - a.id)
    .map((post) => {
      const author = data.users.find((user) => user.id === post.user_id);
      const likes = data.likes.filter((like) => like.post_id === post.id);
      return {
        id: post.id,
        content: post.content,
        created_at: post.created_at,
        author: {
          id: author.id,
          name: author.name,
          handle: author.handle,
          status: author.status,
        },
        likes: likes.length,
        liked: Boolean(viewerId && likes.find((like) => like.user_id === viewerId)),
      };
    });
}

function buildChats(data, currentUserId) {
  return data.users
    .filter((user) => user.id !== currentUserId)
    .map((user) => {
      const relevant = data.messages
        .filter(
          (message) =>
            (message.sender_id === currentUserId && message.recipient_id === user.id) ||
            (message.sender_id === user.id && message.recipient_id === currentUserId),
        )
        .sort((a, b) => a.id - b.id);
      const lastMessage = relevant[relevant.length - 1];
      return {
        ...serializeUser(user),
        last_message: lastMessage ? lastMessage.content : 'Напишите первым',
        last_message_at: lastMessage ? lastMessage.created_at : null,
      };
    });
}

function buildMessages(data, currentUserId, peerId) {
  return data.messages
    .filter(
      (message) =>
        (message.sender_id === currentUserId && message.recipient_id === peerId) ||
        (message.sender_id === peerId && message.recipient_id === currentUserId),
    )
    .sort((a, b) => a.id - b.id);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
    });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (error) {
        reject(error);
      }
    });
  });
}

function sendJson(res, status, payload, headers = {}) {
  const body = Buffer.from(JSON.stringify(payload));
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': body.length,
    ...headers,
  });
  res.end(body);
}

function sendFile(res, filePath) {
  const ext = path.extname(filePath);
  const content = fs.readFileSync(filePath);
  res.writeHead(200, {
    'Content-Type': CONTENT_TYPES[ext] || 'application/octet-stream',
    'Content-Length': content.length,
  });
  res.end(content);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = url.pathname;
  if (STATIC_FILES[pathname] && req.method === 'GET') {
    return sendFile(res, path.join(__dirname, STATIC_FILES[pathname]));
  }

  const data = readData();
  const currentUser = getCurrentUser(req, data);

  try {
    if (req.method === 'GET' && pathname === '/api/bootstrap') {
      return sendJson(res, 200, {
        current_user: currentUser ? serializeUser(currentUser) : null,
        users: data.users.map(serializeUser),
        feed: buildFeed(data, currentUser?.id),
        chats: currentUser ? buildChats(data, currentUser.id) : undefined,
      });
    }

    if (req.method === 'GET' && pathname === '/api/messages') {
      if (!currentUser) {
        return sendJson(res, 401, { error: 'Требуется вход в аккаунт' });
      }
      const peerId = Number(url.searchParams.get('peer_id') || 0);
      return sendJson(res, 200, { messages: buildMessages(data, currentUser.id, peerId) });
    }

    if (req.method === 'POST' && pathname === '/api/register') {
      const body = await readBody(req);
      const name = String(body.name || '').trim();
      const handle = String(body.handle || '').trim().toLowerCase();
      const password = String(body.password || '').trim();
      if (!name || !handle || !password) {
        return sendJson(res, 400, { error: 'Заполни имя, логин и пароль' });
      }
      if (data.users.find((user) => user.handle === handle)) {
        return sendJson(res, 400, { error: 'Такой логин уже занят' });
      }
      data.users.push({
        id: data.nextUserId++,
        name,
        handle,
        password_hash: createPasswordHash(password),
        bio: 'Новый пользователь NOMERCY.',
        status: 'В онлайне',
        theme: 'dark',
        created_at: now(),
      });
      writeData(data);
      return sendJson(res, 201, { ok: true });
    }

    if (req.method === 'POST' && pathname === '/api/login') {
      const body = await readBody(req);
      const handle = String(body.handle || '').trim().toLowerCase();
      const password = String(body.password || '').trim();
      const user = data.users.find((item) => item.handle === handle);
      if (!user || !verifyPassword(password, user.password_hash)) {
        return sendJson(res, 401, { error: 'Неверный логин или пароль' });
      }
      const token = crypto.randomBytes(24).toString('hex');
      data.sessions.push({ token, user_id: user.id, created_at: now() });
      writeData(data);
      return sendJson(res, 200, { ok: true }, {
        'Set-Cookie': `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax`,
      });
    }

    if (req.method === 'POST' && pathname === '/api/logout') {
      const cookies = parseCookies(req.headers.cookie);
      const token = cookies[SESSION_COOKIE];
      data.sessions = data.sessions.filter((session) => session.token !== token);
      writeData(data);
      return sendJson(res, 200, { ok: true }, {
        'Set-Cookie': `${SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax`,
      });
    }

    if (!currentUser) {
      return sendJson(res, 401, { error: 'Требуется вход в аккаунт' });
    }

    if (req.method === 'POST' && pathname === '/api/profile') {
      const body = await readBody(req);
      const user = data.users.find((item) => item.id === currentUser.id);
      user.name = String(body.name || user.name).trim();
      user.bio = String(body.bio || user.bio).trim();
      user.status = String(body.status || user.status).trim() || 'В онлайне';
      user.theme = String(body.theme || user.theme).trim() || 'dark';
      writeData(data);
      return sendJson(res, 200, { user: serializeUser(user) });
    }

    if (req.method === 'POST' && pathname === '/api/posts') {
      const body = await readBody(req);
      const content = String(body.content || '').trim();
      if (!content) {
        return sendJson(res, 400, { error: 'Пост не может быть пустым' });
      }
      data.posts.push({ id: data.nextPostId++, user_id: currentUser.id, content, created_at: now() });
      writeData(data);
      return sendJson(res, 201, { feed: buildFeed(data, currentUser.id) });
    }

    const likeMatch = pathname.match(/^\/api\/posts\/(\d+)\/like$/);
    if (req.method === 'POST' && likeMatch) {
      const postId = Number(likeMatch[1]);
      const existing = data.likes.find((like) => like.user_id === currentUser.id && like.post_id === postId);
      if (existing) {
        data.likes = data.likes.filter((like) => !(like.user_id === currentUser.id && like.post_id === postId));
      } else {
        data.likes.push({ user_id: currentUser.id, post_id: postId });
      }
      writeData(data);
      return sendJson(res, 200, { feed: buildFeed(data, currentUser.id) });
    }

    if (req.method === 'POST' && pathname === '/api/messages') {
      const body = await readBody(req);
      const peerId = Number(body.peer_id || 0);
      const content = String(body.content || '').trim();
      if (!peerId || !content) {
        return sendJson(res, 400, { error: 'Нужно выбрать собеседника и ввести сообщение' });
      }
      data.messages.push({
        id: data.nextMessageId++,
        sender_id: currentUser.id,
        recipient_id: peerId,
        content,
        created_at: now(),
      });
      writeData(data);
      return sendJson(res, 201, {
        messages: buildMessages(data, currentUser.id, peerId),
        chats: buildChats(data, currentUser.id),
      });
    }

    return sendJson(res, 404, { error: 'Не найдено' });
  } catch (error) {
    return sendJson(res, 500, { error: error.message || 'Внутренняя ошибка сервера' });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`NOMERCY running on http://${HOST}:${PORT}`);
});
