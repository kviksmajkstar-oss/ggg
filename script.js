const state = {
  currentUser: null,
  users: [],
  feed: [],
  chats: [],
  activeAuthTab: 'login',
  activeChatPeerId: null,
  messages: [],
  theme: localStorage.getItem('nomercy-theme') || 'dark',
};

const authView = document.getElementById('authView');
const appView = document.getElementById('appView');
const authTabs = document.querySelectorAll('.auth-tab');
const authForms = document.querySelectorAll('.auth-form');
const authMessage = document.getElementById('authMessage');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const logoutButton = document.getElementById('logoutButton');
const themeToggle = document.getElementById('themeToggle');

const profileAvatar = document.getElementById('profileAvatar');
const profileName = document.getElementById('profileName');
const profileHandle = document.getElementById('profileHandle');
const profileBio = document.getElementById('profileBio');
const profileForm = document.getElementById('profileForm');
const profileNameInput = document.getElementById('profileNameInput');
const profileBioInput = document.getElementById('profileBioInput');
const profileStatusInput = document.getElementById('profileStatusInput');
const profileThemeInput = document.getElementById('profileThemeInput');

const postForm = document.getElementById('postForm');
const postInput = document.getElementById('postInput');
const feedList = document.getElementById('feedList');
const postTemplate = document.getElementById('postTemplate');

const userList = document.getElementById('userList');
const chatList = document.getElementById('chatList');
const chatWindow = document.getElementById('chatWindow');
const chatHeader = document.getElementById('chatHeader');
const messageList = document.getElementById('messageList');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const chatPeerStatus = document.getElementById('chatPeerStatus');

function api(path, options = {}) {
  return fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  }).then(async (response) => {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Ошибка запроса');
    }
    return data;
  });
}

function initials(name) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || '')
    .join('') || 'NM';
}

function applyTheme(theme) {
  state.theme = theme;
  document.body.classList.toggle('light', theme === 'light');
  localStorage.setItem('nomercy-theme', theme);
  themeToggle.textContent = theme === 'light' ? 'Тёмная тема' : 'Светлая тема';
}

function setAuthTab(tab) {
  state.activeAuthTab = tab;
  authTabs.forEach((button) => button.classList.toggle('active', button.dataset.authTab === tab));
  authForms.forEach((form) => form.classList.toggle('active', form.id === `${tab}Form`));
  authMessage.textContent = '';
}

function renderUser() {
  if (!state.currentUser) {
    return;
  }
  profileAvatar.textContent = initials(state.currentUser.name);
  profileName.textContent = state.currentUser.name;
  profileHandle.textContent = `@${state.currentUser.handle}`;
  profileBio.textContent = state.currentUser.bio;
  profileNameInput.value = state.currentUser.name;
  profileBioInput.value = state.currentUser.bio;
  profileStatusInput.value = state.currentUser.status;
  profileThemeInput.value = state.currentUser.theme;
}

function renderFeed() {
  feedList.innerHTML = '';
  state.feed.forEach((post) => {
    const node = postTemplate.content.firstElementChild.cloneNode(true);
    node.dataset.postId = String(post.id);
    node.querySelector('[data-author]').textContent = `${post.author.name} · @${post.author.handle}`;
    node.querySelector('[data-meta]').textContent = `${post.author.status} · ${post.created_at}`;
    node.querySelector('[data-content]').textContent = post.content;
    node.querySelector('[data-likes]').textContent = `${post.likes} likes`;
    const likeButton = node.querySelector('[data-like-button]');
    likeButton.classList.toggle('is-liked', post.liked);
    feedList.appendChild(node);
  });
}

function renderUsers() {
  userList.innerHTML = '';
  chatList.innerHTML = '';
  state.users
    .filter((user) => !state.currentUser || user.id !== state.currentUser.id)
    .forEach((user) => {
      const userButton = document.createElement('button');
      userButton.className = 'user-chip';
      userButton.dataset.userId = String(user.id);
      userButton.innerHTML = `<strong>${user.name}</strong><small>@${user.handle} · ${user.status}</small>`;
      userList.appendChild(userButton);
    });

  state.chats.forEach((chat) => {
    const chatButton = document.createElement('button');
    chatButton.className = 'user-chip';
    chatButton.dataset.userId = String(chat.id);
    chatButton.innerHTML = `<strong>${chat.name}</strong><small>${chat.last_message}</small>`;
    if (state.activeChatPeerId === chat.id) {
      chatButton.classList.add('active');
    }
    chatList.appendChild(chatButton);
  });
}

function renderMessages() {
  const peer = state.users.find((user) => user.id === state.activeChatPeerId);
  if (!peer) {
    chatWindow.classList.add('hidden');
    chatPeerStatus.textContent = 'Выбери собеседника';
    return;
  }
  chatWindow.classList.remove('hidden');
  chatPeerStatus.textContent = `Чат с @${peer.handle}`;
  chatHeader.innerHTML = `<strong>${peer.name}</strong><span class="hint-text">${peer.status}</span>`;
  messageList.innerHTML = '';
  state.messages.forEach((message) => {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble${message.sender_id === state.currentUser.id ? ' mine' : ''}`;
    bubble.textContent = message.content;
    messageList.appendChild(bubble);
  });
  messageList.scrollTop = messageList.scrollHeight;
}

async function loadMessages(peerId) {
  state.activeChatPeerId = peerId;
  const data = await api(`/api/messages?peer_id=${peerId}`);
  state.messages = data.messages;
  renderUsers();
  renderMessages();
}

function setAuthenticatedUI(isAuthenticated) {
  authView.classList.toggle('hidden', isAuthenticated);
  appView.classList.toggle('hidden', !isAuthenticated);
  logoutButton.classList.toggle('hidden', !isAuthenticated);
}

async function bootstrap() {
  applyTheme(state.theme);
  const data = await api('/api/bootstrap');
  state.currentUser = data.current_user;
  state.users = data.users;
  state.feed = data.feed;
  state.chats = data.chats || [];
  setAuthenticatedUI(Boolean(state.currentUser));
  if (state.currentUser) {
    renderUser();
    renderFeed();
    renderUsers();
    if (state.chats[0]) {
      await loadMessages(state.chats[0].id);
    }
  }
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  try {
    await api('/api/login', {
      method: 'POST',
      body: JSON.stringify(Object.fromEntries(formData.entries())),
    });
    await bootstrap();
  } catch (error) {
    authMessage.textContent = error.message;
  }
});

registerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(registerForm);
  try {
    await api('/api/register', {
      method: 'POST',
      body: JSON.stringify(Object.fromEntries(formData.entries())),
    });
    authMessage.textContent = 'Аккаунт создан. Теперь войди в систему.';
    setAuthTab('login');
  } catch (error) {
    authMessage.textContent = error.message;
  }
});

authTabs.forEach((button) => {
  button.addEventListener('click', () => setAuthTab(button.dataset.authTab));
});

logoutButton.addEventListener('click', async () => {
  await api('/api/logout', { method: 'POST', body: '{}' });
  state.currentUser = null;
  state.messages = [];
  setAuthenticatedUI(false);
  setAuthTab('login');
});

themeToggle.addEventListener('click', () => {
  applyTheme(state.theme === 'dark' ? 'light' : 'dark');
});

profileForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = {
    name: profileNameInput.value,
    bio: profileBioInput.value,
    status: profileStatusInput.value,
    theme: profileThemeInput.value,
  };
  const data = await api('/api/profile', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  state.currentUser = data.user;
  renderUser();
  state.users = state.users.map((user) => (user.id === data.user.id ? data.user : user));
  renderUsers();
});

postForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const content = postInput.value.trim();
  if (!content) {
    return;
  }
  const data = await api('/api/posts', {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
  state.feed = data.feed;
  postInput.value = '';
  renderFeed();
});

feedList.addEventListener('click', async (event) => {
  const likeButton = event.target.closest('[data-like-button]');
  const postCard = event.target.closest('[data-post-id]');
  if (!likeButton || !postCard) {
    return;
  }
  const data = await api(`/api/posts/${postCard.dataset.postId}/like`, {
    method: 'POST',
    body: '{}',
  });
  state.feed = data.feed;
  renderFeed();
});

userList.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-user-id]');
  if (!button) {
    return;
  }
  await loadMessages(Number(button.dataset.userId));
});

chatList.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-user-id]');
  if (!button) {
    return;
  }
  await loadMessages(Number(button.dataset.userId));
});

messageForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!state.activeChatPeerId) {
    return;
  }
  const content = messageInput.value.trim();
  if (!content) {
    return;
  }
  const data = await api('/api/messages', {
    method: 'POST',
    body: JSON.stringify({ peer_id: state.activeChatPeerId, content }),
  });
  state.messages = data.messages;
  state.chats = data.chats;
  messageInput.value = '';
  renderUsers();
  renderMessages();
});

bootstrap();
