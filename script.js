const postInput = document.getElementById('postInput');
const postCategory = document.getElementById('postCategory');
const publishButton = document.getElementById('publishButton');
const feedList = document.getElementById('feedList');
const postTemplate = document.getElementById('postTemplate');
const filterChips = document.querySelectorAll('.filter-chip');

const nameInput = document.getElementById('nameInput');
const bioInput = document.getElementById('bioInput');
const themeSelect = document.getElementById('themeSelect');
const statusSelect = document.getElementById('statusSelect');
const applyProfileButton = document.getElementById('applyProfile');

const topbarName = document.getElementById('topbarName');
const topbarAvatar = document.getElementById('topbarAvatar');
const profileName = document.getElementById('profileName');
const profileAvatar = document.getElementById('profileAvatar');
const profileBio = document.getElementById('profileBio');
const composerAvatar = document.getElementById('composerAvatar');
const heroStatus = document.getElementById('heroStatus');
const pulseStatus = document.getElementById('heroStatusDot');

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

const categoryTitles = {
  all: 'General',
  tech: 'Tech',
  design: 'Design',
  community: 'Community',
  gaming: 'Gaming',
};

const visuals = {
  all: ['Fresh feed', 'Live profile'],
  tech: ['Launch control', 'Build faster'],
  design: ['Visual motion', 'Style system'],
  community: ['Creator room', 'Pulse together'],
  gaming: ['Arcade mode', 'High score'],
};

const themeClasses = {
  gradient: 'avatar--gradient',
  sunset: 'avatar--sunset',
  neo: 'avatar--neo',
  night: 'avatar--night',
};

const state = {
  profile: {
    name: 'Alex King',
    bio:
      'Делаю digital-продукты, веду creator-комьюнити и собираю вокруг себя людей, которые любят сильный дизайн, tech и новые онлайн-форматы общения.',
    theme: 'gradient',
    status: 'В онлайне',
  },
  filter: 'all',
  posts: [
    {
      id: 1,
      author: 'NOMERCY Official',
      avatar: 'NM',
      avatarClass: 'avatar--gradient',
      meta: 'Сегодня · для всех',
      category: 'community',
      status: 'Live now',
      text:
        'NOMERCY теперь не просто лента в стиле Facebook. Это соцсеть нового типа: здесь можно кастомизировать профиль, следить за live-активностью и играть в собственные мини-игры прямо внутри платформы.',
      likes: 14820,
      comments: 1820,
      shares: 406,
      visual: visuals.community,
      liked: false,
    },
    {
      id: 2,
      author: 'Lisa Stone',
      avatar: 'LS',
      avatarClass: 'avatar--pink',
      meta: '42 мин назад · design room',
      category: 'design',
      status: 'В эфире',
      text:
        'Мне нравится, что интерфейс NOMERCY выглядит современно и атмосферно, но по структуре пользователю всё интуитивно знакомо: stories, лента, online, контакты и creator-комнаты.',
      likes: 2190,
      comments: 176,
      shares: 38,
      visual: visuals.design,
      liked: false,
    },
    {
      id: 3,
      author: 'Dan North',
      avatar: 'DN',
      avatarClass: 'avatar--blue',
      meta: '1 час назад · tech stream',
      category: 'tech',
      status: 'На связи',
      text:
        'Закинул прототип игры в игровую комнату — люди играют, обсуждают и сразу пишут фидбек. Это очень сильная смесь соцсети, live-продукта и creator-platform.',
      likes: 3974,
      comments: 287,
      shares: 94,
      visual: visuals.tech,
      liked: false,
    },
    {
      id: 4,
      author: 'Arcade Club',
      avatar: 'AC',
      avatarClass: 'avatar--neo',
      meta: '2 часа назад · gaming hub',
      category: 'gaming',
      status: 'Играют сейчас',
      text:
        'Устроили челлендж по Tap Rush прямо в NOMERCY Arcade. Кто набьёт 120+ кликов за раунд — получает место в weekly top creators.',
      likes: 5120,
      comments: 421,
      shares: 133,
      visual: visuals.gaming,
      liked: false,
    },
  ],
};

const livePresets = [
  {
    headline: '12 creator rooms активны',
    description: 'Сейчас активнее всего обсуждают запуск продуктов, AI-дизайн и стримы с играми.',
    creators: '284',
    games: '7',
    viewers: '19.8K',
  },
  {
    headline: '16 rooms в прямом эфире',
    description: 'Пошёл рост игровых стримов, product review и community brainstorm-сессий.',
    creators: '352',
    games: '11',
    viewers: '24.1K',
  },
  {
    headline: '9 live-потоков прямо сейчас',
    description: 'Дизайнеры показывают кейсы, а игровые румы запускают вечерние баттлы.',
    creators: '218',
    games: '5',
    viewers: '15.2K',
  },
];

const memoryState = {
  sequence: [],
  playerSequence: [],
  inputEnabled: false,
};

let tapRushScore = 0;
let tapRushCountdown = 0;
let tapRushInterval = null;

function formatCounter(value, label) {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K ${label}`;
  }

  return `${value} ${label}`;
}

function getInitials(name) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('') || 'NM';
}

function updateAvatarTheme(element, initials) {
  element.className = `avatar ${themeClasses[state.profile.theme]}`;
  if (element.id === 'profileAvatar') {
    element.className += ' avatar--xl';
  }
  element.textContent = initials;
}

function renderProfile() {
  const initials = getInitials(state.profile.name);
  topbarName.textContent = state.profile.name;
  profileName.textContent = state.profile.name;
  profileBio.textContent = state.profile.bio;
  heroStatus.textContent = state.profile.status;

  updateAvatarTheme(topbarAvatar, initials);
  updateAvatarTheme(profileAvatar, initials);
  updateAvatarTheme(composerAvatar, initials);

  postInput.placeholder = `Что нового, ${state.profile.name.split(' ')[0]}?`;
  if (state.profile.status === 'В онлайне' || state.profile.status === 'В эфире') {
    pulseStatus.style.background = 'var(--success)';
  } else if (state.profile.status === 'Играю') {
    pulseStatus.style.background = 'var(--accent-3)';
  } else {
    pulseStatus.style.background = 'var(--accent)';
  }
}

function getVisiblePosts() {
  if (state.filter === 'all') {
    return state.posts;
  }

  return state.posts.filter((post) => post.category === state.filter);
}

function renderFeed() {
  feedList.innerHTML = '';

  getVisiblePosts().forEach((post) => {
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

    const likeButton = node.querySelector('[data-action="like"]');
    if (post.liked) {
      likeButton.classList.add('is-active');
    }

    feedList.appendChild(node);
  });
}

function createPost() {
  const text = postInput.value.trim();
  const category = postCategory.value;

  if (!text) {
    postInput.focus();
    postInput.placeholder = 'Напиши пост, чтобы он появился в ленте';
    return;
  }

  state.posts.unshift({
    id: Date.now(),
    author: state.profile.name,
    avatar: getInitials(state.profile.name),
    avatarClass: themeClasses[state.profile.theme],
    meta: `Только что · ${state.profile.status}`,
    category,
    status: state.profile.status,
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
}

function setFilter(nextFilter) {
  state.filter = nextFilter;
  filterChips.forEach((chip) => {
    chip.classList.toggle('active', chip.dataset.filter === nextFilter);
  });
  renderFeed();
}

function toggleLike(postId) {
  const post = state.posts.find((item) => item.id === postId);
  if (!post) {
    return;
  }

  post.liked = !post.liked;
  post.likes += post.liked ? 1 : -1;
  renderFeed();
}

function applyProfileChanges() {
  state.profile.name = nameInput.value.trim() || 'Alex King';
  state.profile.bio = bioInput.value.trim() || state.profile.bio;
  state.profile.theme = themeSelect.value;
  state.profile.status = statusSelect.value;
  renderProfile();
  renderFeed();
}

function refreshLive() {
  const preset = livePresets[Math.floor(Math.random() * livePresets.length)];
  liveHeadline.textContent = preset.headline;
  liveDescription.textContent = preset.description;
  liveCreators.textContent = preset.creators;
  liveGames.textContent = preset.games;
  liveViewers.textContent = preset.viewers;
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

publishButton.addEventListener('click', createPost);
applyProfileButton.addEventListener('click', applyProfileChanges);
refreshLiveButton.addEventListener('click', refreshLive);
startTapRushButton.addEventListener('click', startTapRush);
startMemoryGameButton.addEventListener('click', startMemoryGame);

tapRushButton.addEventListener('click', () => {
  if (tapRushButton.disabled) {
    return;
  }

  tapRushScore += 1;
  tapScore.textContent = String(tapRushScore);
});

postInput.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    createPost();
  }
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

memoryTiles.forEach((tile) => {
  tile.addEventListener('click', () => {
    tile.classList.add('is-lit');
    setTimeout(() => tile.classList.remove('is-lit'), 180);
    handleMemoryInput(Number(tile.dataset.tile));
  });
});

renderProfile();
renderFeed();
refreshLive();
