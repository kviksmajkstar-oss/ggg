const STORAGE_KEY = 'nomercy-app-state-v3';

const body = document.body;
const navTabs = document.querySelectorAll('.nav-tab');
const tabPanels = document.querySelectorAll('.tab-panel');
const shortcutButtons = document.querySelectorAll('[data-tab-target]');
const themeToggle = document.getElementById('themeToggle');

const postInput = document.getElementById('postInput');
const postCategory = document.getElementById('postCategory');
const publishButton = document.getElementById('publishButton');
const feedList = document.getElementById('feedList');
const filterChips = document.querySelectorAll('.filter-chip');
const postTemplate = document.getElementById('postTemplate');

const nameInput = document.getElementById('nameInput');
const bioInput = document.getElementById('bioInput');
const themeSelect = document.getElementById('themeSelect');
const statusSelect = document.getElementById('statusSelect');
const applyProfileButton = document.getElementById('applyProfile');

const topbarAvatar = document.getElementById('topbarAvatar');
const topbarName = document.getElementById('topbarName');
const topbarRole = document.getElementById('topbarRole');
const profileAvatar = document.getElementById('profileAvatar');
const profileName = document.getElementById('profileName');
const profileBio = document.getElementById('profileBio');
const composerAvatar = document.getElementById('composerAvatar');
const heroStatus = document.getElementById('heroStatus');
const heroStatusDot = document.getElementById('heroStatusDot');

const refreshLiveButton = document.getElementById('refreshLive');
const liveHeadline = document.getElementById('liveHeadline');
const liveDescription = document.getElementById('liveDescription');
const liveCreators = document.getElementById('liveCreators');
const liveGames = document.getElementById('liveGames');
const liveViewers = document.getElementById('liveViewers');

const startTapRushButton = document.getElementById('startTapRush');
const tapRushButton = document.getElementById('tapRushButton');
const tapScore = document.getElementById('tapScore');
const tapRushTimer = document.getElementById('tapRushTimer');
const startMemoryGameButton = document.getElementById('startMemoryGame');
const memoryStatus = document.getElementById('memoryStatus');
const memoryTiles = document.querySelectorAll('.memory-tile');

const chatList = document.getElementById('chatList');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendChatButton = document.getElementById('sendChatButton');
const activeChatAvatar = document.getElementById('activeChatAvatar');
const activeChatName = document.getElementById('activeChatName');
const activeChatStatus = document.getElementById('activeChatStatus');
const quickContactList = document.getElementById('quickContactList');
const chatListItemTemplate = document.getElementById('chatListItemTemplate');
const quickReplies = document.querySelectorAll('.quick-reply');
const typingIndicator = document.getElementById('typingIndicator');

const profileGrid = document.getElementById('profileGrid');
const profileCardTemplate = document.getElementById('profileCardTemplate');
const spotlightAvatar = document.getElementById('spotlightAvatar');
const spotlightName = document.getElementById('spotlightName');
const spotlightRole = document.getElementById('spotlightRole');
const spotlightBio = document.getElementById('spotlightBio');
const openSpotlightChatButton = document.getElementById('openSpotlightChat');
const useSpotlightProfileButton = document.getElementById('useSpotlightProfile');

const categoryTitles = {
  all: 'General',
  music: 'Music',
  tech: 'Tech',
  community: 'Community',
  gaming: 'Gaming',
};

const visuals = {
  all: ['Fresh social OS', 'Live profile'],
  music: ['kviksmajkmusic', 'Studio drop'],
  tech: ['NOMERCY dev', 'Build faster'],
  community: ['Creator room', 'Community wave'],
  gaming: ['Arcade mode', 'High score'],
};

const avatarThemes = {
  gradient: 'avatar--gradient',
  sunset: 'avatar--sunset',
  neo: 'avatar--neo',
  night: 'avatar--night',
};

const defaultProfiles = [
  {
    id: 'ruslan',
    name: 'Руслан Kviksmajk',
    role: 'kviksmajkmusic • разработчик NOMERCY',
    bio: 'Музыкант, автор проекта kviksmajkmusic и разработчик социальной сети NOMERCY. Собираю музыку, комьюнити, live и игровые механики в одном продукте.',
    status: 'В онлайне',
    avatar: 'RK',
    theme: 'gradient',
    online: true,
  },
  {
    id: 'lisa',
    name: 'Lisa Stone',
    role: 'UI / motion designer',
    bio: 'Создаёт смелые интерфейсы, motion-эстетику и визуальные системы для creator-платформ.',
    status: 'В эфире',
    avatar: 'LS',
    theme: 'sunset',
    online: true,
  },
  {
    id: 'dan',
    name: 'Dan North',
    role: 'product strategist',
    bio: 'Запускает community-driven продукты и помогает делать сильные social UX сценарии.',
    status: 'На связи',
    avatar: 'DN',
    theme: 'night',
    online: true,
  },
  {
    id: 'mira',
    name: 'Mira Ray',
    role: 'gaming host',
    bio: 'Ведёт игровые комнаты, турниры и social arcade-события прямо внутри NOMERCY.',
    status: 'В студии',
    avatar: 'MR',
    theme: 'neo',
    online: true,
  },
];

const defaultChats = {
  lisa: {
    profileId: 'lisa',
    messages: [
      { mine: false, text: 'Руслан, новый визуал NOMERCY выглядит намного сильнее.' },
      { mine: true, text: 'Супер. Хочу, чтобы платформа чувствовалась как новый social OS.' },
    ],
  },
  dan: {
    profileId: 'dan',
    messages: [
      { mine: false, text: 'Рабочие вкладки и профили уже ощущаются как настоящий продукт.' },
      { mine: true, text: 'Да, теперь добавил ещё и живые чаты, чтобы было меньше ощущения макета.' },
    ],
  },
  mira: {
    profileId: 'mira',
    messages: [
      { mine: false, text: 'Игровой хаб стал крутым. Надо потом добавить лидерборды.' },
      { mine: true, text: 'Согласен, это хороший следующий шаг для NOMERCY Arcade.' },
    ],
  },
};

const defaultPosts = [
  {
    id: 1,
    author: 'Руслан Kviksmajk',
    avatar: 'RK',
    avatarClass: 'avatar--gradient',
    meta: 'Сегодня · автор NOMERCY',
    category: 'music',
    status: 'В онлайне',
    text: 'NOMERCY — моя социальная сеть, где соединяются музыка, живые чаты, профили, переключаемые темы и свои игры. Хотелось сделать не просто аналог Facebook, а более современную и живую платформу.',
    likes: 18420,
    comments: 2040,
    shares: 512,
    visual: visuals.music,
    liked: false,
  },
  {
    id: 2,
    author: 'Lisa Stone',
    avatar: 'LS',
    avatarClass: 'avatar--sunset',
    meta: '45 мин назад · design room',
    category: 'community',
    status: 'В эфире',
    text: 'Рабочие вкладки и настоящие чаты сильно меняют ощущение продукта. NOMERCY уже не выглядит как просто концепт — он ощущается как живая социальная платформа.',
    likes: 2380,
    comments: 196,
    shares: 44,
    visual: visuals.community,
    liked: false,
  },
  {
    id: 3,
    author: 'Dan North',
    avatar: 'DN',
    avatarClass: 'avatar--night',
    meta: '1 час назад · product talk',
    category: 'tech',
    status: 'На связи',
    text: 'Очень нравится, что здесь можно открыть профиль человека, сразу перейти в чат и тут же написать сообщение. Это делает путь пользователя намного понятнее.',
    likes: 4210,
    comments: 302,
    shares: 105,
    visual: visuals.tech,
    liked: false,
  },
  {
    id: 4,
    author: 'Mira Ray',
    avatar: 'MR',
    avatarClass: 'avatar--neo',
    meta: '2 часа назад · arcade room',
    category: 'gaming',
    status: 'В студии',
    text: 'Color Match и Tap Rush — хорошее начало. Люблю, когда соцсеть даёт не только контент, но и игровые мини-сценарии прямо внутри интерфейса.',
    likes: 5390,
    comments: 448,
    shares: 129,
    visual: visuals.gaming,
    liked: false,
  },
];

const livePresets = [
  {
    headline: '14 creator rooms активны',
    description: 'Сейчас обсуждают музыку, запуск альбомов, визуал клипов и игровые стримы.',
    creators: '312',
    games: '9',
    viewers: '27.4K',
  },
  {
    headline: '18 live-комнат в эфире',
    description: 'Музыканты тестируют новые релизы, а игровые хосты ведут вечерние комнаты.',
    creators: '356',
    games: '12',
    viewers: '31.2K',
  },
  {
    headline: '11 стримов онлайн прямо сейчас',
    description: 'Сегодня особенно активны kviksmajkmusic, creator-rooms и gaming challenges.',
    creators: '245',
    games: '7',
    viewers: '22.9K',
  },
];

const autoReplies = {
  lisa: [
    'Мне нравится, как в NOMERCY показан online-flow через живой чат и typing-индикатор.',
    'Если хочешь, могу подсказать, как улучшить profile UX и визуал ленты.',
    'Да, и обязательно протестируй светлую тему — она тоже смотрится очень чисто.',
  ],
  dan: [
    'Онлайн-общение лучше всего работает, когда пользователь видит быстрый ответ и понятный статус собеседника.',
    'Сценарий хороший: открыл профиль → перешёл в чат → получил ответ.',
    'Можно дальше развить это в полноценные live-консультации и support-каналы.',
  ],
  mira: [
    'Игровые комнаты отлично сочетаются с чатами: люди пишут прямо во время мини-игр.',
    'Попробуй потом добавить leaderboard и игровые бейджи — это сильно оживит платформу.',
    'Онлайн-чаты хорошо работают, когда рядом есть и контент, и интерактив.',
  ],
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function getStoredState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

const storedState = getStoredState();
const state = {
  activeTab: storedState?.activeTab || 'feed',
  activeFilter: storedState?.activeFilter || 'all',
  activeChatId: storedState?.activeChatId || 'lisa',
  spotlightProfileId: storedState?.spotlightProfileId || 'ruslan',
  theme: storedState?.theme || 'dark',
  currentProfile: storedState?.currentProfile || clone(defaultProfiles[0]),
  posts: storedState?.posts || clone(defaultPosts),
  chats: storedState?.chats || clone(defaultChats),
};

const memoryState = {
  sequence: [],
  playerSequence: [],
  inputEnabled: false,
};

let tapRushScore = 0;
let tapRushCountdown = 0;
let tapRushInterval = null;
let autoReplyTimeout = null;

function saveState() {
  const snapshot = {
    activeTab: state.activeTab,
    activeFilter: state.activeFilter,
    activeChatId: state.activeChatId,
    spotlightProfileId: state.spotlightProfileId,
    theme: state.theme,
    currentProfile: state.currentProfile,
    posts: state.posts,
    chats: state.chats,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
}

function getInitials(name) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('') || 'NM';
}

function formatCounter(value, label) {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K ${label}`;
  }
  return `${value} ${label}`;
}

function getProfileById(profileId) {
  return defaultProfiles.find((profile) => profile.id === profileId);
}

function updateAvatar(element, profile, extraClass = '') {
  element.className = `avatar ${avatarThemes[profile.theme]}${extraClass ? ` ${extraClass}` : ''}`;
  element.textContent = profile.avatar || getInitials(profile.name);
}

function setTheme(isLight) {
  state.theme = isLight ? 'light' : 'dark';
  body.dataset.theme = state.theme;
  themeToggle.checked = isLight;
  saveState();
}

function renderCurrentProfile() {
  topbarName.textContent = state.currentProfile.name;
  topbarRole.textContent = state.currentProfile.role;
  profileName.textContent = state.currentProfile.name;
  profileBio.textContent = state.currentProfile.bio;
  heroStatus.textContent = state.currentProfile.status;
  postInput.placeholder = `Что нового, ${state.currentProfile.name.split(' ')[0]}?`;

  updateAvatar(topbarAvatar, state.currentProfile);
  updateAvatar(profileAvatar, state.currentProfile, 'avatar--xl');
  updateAvatar(composerAvatar, state.currentProfile);

  heroStatusDot.style.background =
    state.currentProfile.status === 'В студии' ? 'var(--accent-3)' : 'var(--success)';

  nameInput.value = state.currentProfile.name;
  bioInput.value = state.currentProfile.bio;
  themeSelect.value = state.currentProfile.theme;
  statusSelect.value = state.currentProfile.status;
}

function setActiveTab(tabId) {
  state.activeTab = tabId;
  navTabs.forEach((button) => {
    button.classList.toggle('active', button.dataset.tab === tabId);
  });
  tabPanels.forEach((panel) => {
    panel.classList.toggle('active', panel.dataset.panel === tabId);
  });
  saveState();
}

function renderFeed() {
  feedList.innerHTML = '';
  const visiblePosts = state.activeFilter === 'all'
    ? state.posts
    : state.posts.filter((post) => post.category === state.activeFilter);

  visiblePosts.forEach((post) => {
    const node = postTemplate.content.firstElementChild.cloneNode(true);
    node.dataset.postId = String(post.id);
    node.querySelector('[data-avatar]').className = `avatar ${post.avatarClass}`;
    node.querySelector('[data-avatar]').textContent = post.avatar;
    node.querySelector('[data-author]').textContent = post.author;
    node.querySelector('[data-meta]').textContent = post.meta;
    node.querySelector('[data-category-label]').textContent = categoryTitles[post.category] || 'General';
    node.querySelector('[data-status]').textContent = post.status;
    node.querySelector('[data-text]').textContent = post.text;
    node.querySelector('[data-visual-title]').textContent = post.visual[0];
    node.querySelector('[data-visual-accent]').textContent = post.visual[1];
    node.querySelector('[data-likes]').textContent = formatCounter(post.likes, 'likes');
    node.querySelector('[data-comments]').textContent = formatCounter(post.comments, 'comments');
    node.querySelector('[data-shares]').textContent = formatCounter(post.shares, 'shares');
    if (post.liked) {
      node.querySelector('[data-action="like"]').classList.add('is-active');
    }
    feedList.appendChild(node);
  });
}

function createPost() {
  const text = postInput.value.trim();
  const category = postCategory.value;
  if (!text) {
    postInput.focus();
    postInput.placeholder = 'Напиши сообщение для ленты';
    return;
  }

  state.posts.unshift({
    id: Date.now(),
    author: state.currentProfile.name,
    avatar: state.currentProfile.avatar,
    avatarClass: avatarThemes[state.currentProfile.theme],
    meta: `Только что · ${state.currentProfile.role}`,
    category,
    status: state.currentProfile.status,
    text,
    likes: 0,
    comments: 0,
    shares: 0,
    visual: visuals[category] || visuals.all,
    liked: false,
  });

  postInput.value = '';
  postCategory.value = 'all';
  renderFeed();
  saveState();
}

function toggleLike(postId) {
  const post = state.posts.find((item) => item.id === postId);
  if (!post) {
    return;
  }
  post.liked = !post.liked;
  post.likes += post.liked ? 1 : -1;
  renderFeed();
  saveState();
}

function setFilter(filter) {
  state.activeFilter = filter;
  filterChips.forEach((chip) => {
    chip.classList.toggle('active', chip.dataset.filter === filter);
  });
  renderFeed();
  saveState();
}

function applyProfileChanges() {
  state.currentProfile = {
    ...state.currentProfile,
    name: nameInput.value.trim() || state.currentProfile.name,
    bio: bioInput.value.trim() || state.currentProfile.bio,
    theme: themeSelect.value,
    status: statusSelect.value,
    avatar: getInitials(nameInput.value.trim() || state.currentProfile.name),
  };
  renderCurrentProfile();
  renderFeed();
  saveState();
}

function refreshLive() {
  const preset = livePresets[Math.floor(Math.random() * livePresets.length)];
  liveHeadline.textContent = preset.headline;
  liveDescription.textContent = preset.description;
  liveCreators.textContent = preset.creators;
  liveGames.textContent = preset.games;
  liveViewers.textContent = preset.viewers;
}

function renderChatList() {
  chatList.innerHTML = '';
  quickContactList.innerHTML = '';

  Object.keys(state.chats).forEach((chatId) => {
    const chat = state.chats[chatId];
    const profile = getProfileById(chat.profileId);
    const previewMessage = chat.messages[chat.messages.length - 1]?.text ?? 'Новый чат';

    const chatNode = chatListItemTemplate.content.firstElementChild.cloneNode(true);
    chatNode.dataset.chatId = chatId;
    chatNode.classList.toggle('active', state.activeChatId === chatId);
    chatNode.querySelector('[data-chat-avatar]').className = `avatar avatar--sm ${avatarThemes[profile.theme]}`;
    chatNode.querySelector('[data-chat-avatar]').textContent = profile.avatar;
    chatNode.querySelector('[data-chat-name]').textContent = profile.name;
    chatNode.querySelector('[data-chat-preview]').textContent = previewMessage;
    chatList.appendChild(chatNode);

    const quickContact = document.createElement('button');
    quickContact.className = 'contact-row';
    quickContact.dataset.chatId = chatId;
    quickContact.innerHTML = `<span class="avatar avatar--sm ${avatarThemes[profile.theme]}">${profile.avatar}</span><span>${profile.name}</span><small></small>`;
    quickContactList.appendChild(quickContact);
  });
}

function renderActiveChat() {
  const chat = state.chats[state.activeChatId];
  const profile = getProfileById(chat.profileId);
  activeChatName.textContent = profile.name;
  activeChatStatus.textContent = `${profile.status} • online`;
  activeChatAvatar.className = `avatar avatar--sm ${avatarThemes[profile.theme]}`;
  activeChatAvatar.textContent = profile.avatar;

  chatMessages.innerHTML = '';
  chat.messages.forEach((message) => {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble${message.mine ? ' mine' : ''}`;
    bubble.textContent = message.text;
    chatMessages.appendChild(bubble);
  });
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator(show, label = 'Собеседник печатает…') {
  typingIndicator.textContent = label;
  typingIndicator.classList.toggle('hidden', !show);
}

function buildAutoReply(chatId, userMessage) {
  const message = userMessage.toLowerCase();
  if (message.includes('эфир') || message.includes('live')) {
    return 'Следующий live стартует сегодня вечером. Я пришлю анонс прямо сюда в чат.';
  }
  if (message.includes('профиль')) {
    return 'Открой вкладку Profiles — там можно посмотреть spotlight-профили и даже сделать один из них активным.';
  }
  if (message.includes('игр') || message.includes('game')) {
    return 'Перейди в Games: там уже доступны Tap Rush и Color Match, и их можно развивать дальше.';
  }
  const replies = autoReplies[chatId] || autoReplies.lisa;
  return replies[Math.floor(Math.random() * replies.length)];
}

function scheduleAutoReply(chatId, userMessage) {
  clearTimeout(autoReplyTimeout);
  showTypingIndicator(true);
  autoReplyTimeout = setTimeout(() => {
    state.chats[chatId].messages.push({ mine: false, text: buildAutoReply(chatId, userMessage) });
    showTypingIndicator(false);
    if (state.activeChatId === chatId) {
      renderChatList();
      renderActiveChat();
    } else {
      renderChatList();
    }
    saveState();
  }, 900);
}

function sendChatMessage(prefilledText = '') {
  const value = (prefilledText || chatInput.value).trim();
  if (!value) {
    chatInput.focus();
    return;
  }
  state.chats[state.activeChatId].messages.push({ mine: true, text: value });
  chatInput.value = '';
  renderChatList();
  renderActiveChat();
  saveState();
  scheduleAutoReply(state.activeChatId, value);
}

function renderProfiles() {
  profileGrid.innerHTML = '';
  defaultProfiles.forEach((profile) => {
    const node = profileCardTemplate.content.firstElementChild.cloneNode(true);
    node.dataset.profileId = profile.id;
    node.classList.toggle('active', state.spotlightProfileId === profile.id);
    node.querySelector('[data-profile-avatar]').className = `avatar avatar--sm ${avatarThemes[profile.theme]}`;
    node.querySelector('[data-profile-avatar]').textContent = profile.avatar;
    node.querySelector('[data-profile-name]').textContent = profile.name;
    node.querySelector('[data-profile-role]').textContent = profile.role;
    profileGrid.appendChild(node);
  });

  const spotlight = getProfileById(state.spotlightProfileId);
  spotlightAvatar.className = `avatar avatar--xl ${avatarThemes[spotlight.theme]}`;
  spotlightAvatar.textContent = spotlight.avatar;
  spotlightName.textContent = spotlight.name;
  spotlightRole.textContent = spotlight.role;
  spotlightBio.textContent = spotlight.bio;
}

function useSpotlightAsCurrentProfile() {
  const spotlight = getProfileById(state.spotlightProfileId);
  state.currentProfile = { ...spotlight };
  renderCurrentProfile();
  renderFeed();
  saveState();
}

function finishTapRush() {
  clearInterval(tapRushInterval);
  tapRushInterval = null;
  tapRushButton.disabled = true;
  startTapRushButton.disabled = false;
  tapRushTimer.textContent = `Раунд окончен. Твой результат: ${tapRushScore}.`;
}

function startTapRush() {
  tapRushScore = 0;
  tapRushCountdown = 10;
  tapScore.textContent = '0';
  tapRushTimer.textContent = `Осталось ${tapRushCountdown} сек.`;
  tapRushButton.disabled = false;
  startTapRushButton.disabled = true;

  clearInterval(tapRushInterval);
  tapRushInterval = setInterval(() => {
    tapRushCountdown -= 1;
    if (tapRushCountdown <= 0) {
      finishTapRush();
      return;
    }
    tapRushTimer.textContent = `Осталось ${tapRushCountdown} сек.`;
  }, 1000);
}

function flashTile(index) {
  return new Promise((resolve) => {
    const tile = memoryTiles[index];
    tile.classList.add('is-lit');
    setTimeout(() => {
      tile.classList.remove('is-lit');
      setTimeout(resolve, 120);
    }, 420);
  });
}

async function playSequence() {
  memoryState.inputEnabled = false;
  for (const index of memoryState.sequence) {
    // eslint-disable-next-line no-await-in-loop
    await flashTile(index);
  }
  memoryState.inputEnabled = true;
  memoryStatus.textContent = `Твой ход: повтори ${memoryState.sequence.length} шаг(а).`;
}

async function startMemoryRound() {
  memoryState.playerSequence = [];
  memoryState.sequence.push(Math.floor(Math.random() * memoryTiles.length));
  memoryStatus.textContent = `Смотри внимательно: раунд ${memoryState.sequence.length}.`;
  await playSequence();
}

async function startMemoryGame() {
  memoryState.sequence = [];
  memoryState.playerSequence = [];
  memoryStatus.textContent = 'Новая игра началась.';
  await startMemoryRound();
}

function handleMemoryInput(index) {
  if (!memoryState.inputEnabled) {
    return;
  }
  memoryState.playerSequence.push(index);
  const stepIndex = memoryState.playerSequence.length - 1;
  if (memoryState.sequence[stepIndex] !== index) {
    memoryState.inputEnabled = false;
    memoryStatus.textContent = `Ошибка на раунде ${memoryState.sequence.length}. Попробуй ещё раз.`;
    return;
  }
  if (memoryState.playerSequence.length === memoryState.sequence.length) {
    memoryState.inputEnabled = false;
    memoryStatus.textContent = `Отлично! Ты прошёл раунд ${memoryState.sequence.length}.`;
    setTimeout(() => {
      startMemoryRound();
    }, 800);
  }
}

navTabs.forEach((button) => {
  button.addEventListener('click', () => setActiveTab(button.dataset.tab));
});

shortcutButtons.forEach((button) => {
  button.addEventListener('click', () => setActiveTab(button.dataset.tabTarget));
});

themeToggle.addEventListener('change', () => {
  setTheme(themeToggle.checked);
});

publishButton.addEventListener('click', createPost);
applyProfileButton.addEventListener('click', applyProfileChanges);
refreshLiveButton.addEventListener('click', refreshLive);
startTapRushButton.addEventListener('click', startTapRush);
startMemoryGameButton.addEventListener('click', startMemoryGame);
sendChatButton.addEventListener('click', () => sendChatMessage());
openSpotlightChatButton.addEventListener('click', () => {
  const targetChatId = state.spotlightProfileId === 'ruslan' ? 'lisa' : state.spotlightProfileId;
  state.activeChatId = targetChatId;
  renderChatList();
  renderActiveChat();
  setActiveTab('chats');
  saveState();
});
useSpotlightProfileButton.addEventListener('click', useSpotlightAsCurrentProfile);

postInput.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    createPost();
  }
});
chatInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    sendChatMessage();
  }
});

tapRushButton.addEventListener('click', () => {
  if (tapRushButton.disabled) {
    return;
  }
  tapRushScore += 1;
  tapScore.textContent = String(tapRushScore);
});

filterChips.forEach((chip) => {
  chip.addEventListener('click', () => setFilter(chip.dataset.filter));
});

feedList.addEventListener('click', (event) => {
  const likeButton = event.target.closest('[data-action="like"]');
  if (!likeButton) {
    return;
  }
  const postCard = likeButton.closest('[data-post-id]');
  if (!postCard) {
    return;
  }
  toggleLike(Number(postCard.dataset.postId));
});

chatList.addEventListener('click', (event) => {
  const chatButton = event.target.closest('[data-chat-id]');
  if (!chatButton) {
    return;
  }
  state.activeChatId = chatButton.dataset.chatId;
  showTypingIndicator(false);
  renderChatList();
  renderActiveChat();
  saveState();
});

quickContactList.addEventListener('click', (event) => {
  const contactButton = event.target.closest('[data-chat-id]');
  if (!contactButton) {
    return;
  }
  state.activeChatId = contactButton.dataset.chatId;
  showTypingIndicator(false);
  renderChatList();
  renderActiveChat();
  setActiveTab('chats');
  saveState();
});

profileGrid.addEventListener('click', (event) => {
  const profileButton = event.target.closest('[data-profile-id]');
  if (!profileButton) {
    return;
  }
  state.spotlightProfileId = profileButton.dataset.profileId;
  renderProfiles();
  saveState();
});

quickReplies.forEach((button) => {
  button.addEventListener('click', () => {
    sendChatMessage(button.dataset.quickReply || '');
  });
});

memoryTiles.forEach((tile) => {
  tile.addEventListener('click', () => {
    tile.classList.add('is-lit');
    setTimeout(() => tile.classList.remove('is-lit'), 180);
    handleMemoryInput(Number(tile.dataset.tile));
  });
});

renderCurrentProfile();
renderFeed();
renderChatList();
renderActiveChat();
renderProfiles();
refreshLive();
setTheme(state.theme === 'light');
setActiveTab(state.activeTab);
showTypingIndicator(false);
