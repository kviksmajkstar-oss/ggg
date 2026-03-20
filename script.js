const postInput = document.getElementById('postInput');
const postCategory = document.getElementById('postCategory');
const publishButton = document.getElementById('publishButton');
const feedList = document.getElementById('feedList');
const postTemplate = document.getElementById('postTemplate');
const filterChips = document.querySelectorAll('.filter-chip');
const shufflePulseButton = document.getElementById('shufflePulse');

const categoryTitles = {
  all: 'General',
  tech: 'Tech',
  design: 'Design',
  community: 'Community',
};

const visuals = {
  all: ['Daily momentum', 'Fresh drop'],
  tech: ['Launch control', 'Build fast'],
  design: ['Visual system', 'Color wave'],
  community: ['Community pulse', 'Live together'],
};

const feedState = {
  filter: 'all',
  posts: [
    {
      id: 1,
      author: 'NOMERCY Official',
      avatar: 'NM',
      avatarClass: 'avatar--gradient',
      meta: 'Сегодня · Рекомендовано всем',
      category: 'community',
      text:
        'Мы сделали NOMERCY ближе к привычной логике Facebook: истории, живая лента, контакты, навигация и мгновенное создание постов. Но наша уникальность — Pulse Radar, который показывает, что реально зажигает твою аудиторию прямо сейчас.',
      likes: 12800,
      comments: 1400,
      shares: 312,
      visual: visuals.community,
      liked: false,
    },
    {
      id: 2,
      author: 'Lisa Stone',
      avatar: 'LS',
      avatarClass: 'avatar--pink',
      meta: '39 мин назад · Design loop',
      category: 'design',
      text:
        'Пересобрала интерфейс клиентского кабинета в стиле soft glass. Обожаю, когда знакомая структура работает как Facebook, но визуально ощущается как премиальный продукт 2026 года.',
      likes: 2140,
      comments: 148,
      shares: 27,
      visual: visuals.design,
      liked: false,
    },
    {
      id: 3,
      author: 'Dan North',
      avatar: 'DN',
      avatarClass: 'avatar--blue',
      meta: '1 час назад · Build in public',
      category: 'tech',
      text:
        'Запустили закрытую creator-room для фаундеров. Люди видят идеи, комментируют гипотезы и сразу договариваются о созвонах. Такой UX реально сильнее обычной ленты.',
      likes: 3890,
      comments: 264,
      shares: 88,
      visual: visuals.tech,
      liked: false,
    },
  ],
};

const pulsePresets = [
  { score: 87, design: '+18%', tech: '+24%', live: '12 city rooms' },
  { score: 91, design: '+26%', tech: '+19%', live: '16 city rooms' },
  { score: 84, design: '+14%', tech: '+31%', live: '10 city rooms' },
  { score: 93, design: '+22%', tech: '+29%', live: '18 city rooms' },
];

function formatCounter(value, label) {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(value >= 10000 ? 1 : 1)}K ${label}`;
  }

  return `${value} ${label}`;
}

function getVisiblePosts() {
  if (feedState.filter === 'all') {
    return feedState.posts;
  }

  return feedState.posts.filter((post) => post.category === feedState.filter);
}

function renderFeed() {
  feedList.innerHTML = '';

  const visiblePosts = getVisiblePosts();

  visiblePosts.forEach((post) => {
    const node = postTemplate.content.firstElementChild.cloneNode(true);
    node.dataset.postId = String(post.id);
    node.dataset.category = post.category;
    node.querySelector('[data-avatar]').textContent = post.avatar;
    node.querySelector('[data-avatar]').className = `avatar ${post.avatarClass}`;
    node.querySelector('[data-author]').textContent = post.author;
    node.querySelector('[data-meta]').textContent = post.meta;
    node.querySelector('[data-category-label]').textContent = categoryTitles[post.category] || 'General';
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
    postInput.placeholder = 'Напиши пост, чтобы твоя аудитория увидела тебя';
    return;
  }

  feedState.posts.unshift({
    id: Date.now(),
    author: 'Alex King',
    avatar: 'AK',
    avatarClass: 'avatar--gradient',
    meta: 'Только что · Creator mode',
    category,
    text,
    likes: 0,
    comments: 0,
    shares: 0,
    visual: visuals[category] || visuals.all,
    liked: false,
  });

  postInput.value = '';
  postInput.placeholder = 'Что нового, Alex?';
  postCategory.value = 'all';
  renderFeed();
}

function setFilter(nextFilter) {
  feedState.filter = nextFilter;

  filterChips.forEach((chip) => {
    chip.classList.toggle('active', chip.dataset.filter === nextFilter);
  });

  renderFeed();
}

function toggleLike(postId) {
  const targetPost = feedState.posts.find((post) => post.id === postId);

  if (!targetPost) {
    return;
  }

  targetPost.liked = !targetPost.liked;
  targetPost.likes += targetPost.liked ? 1 : -1;
  renderFeed();
}

function refreshPulse() {
  const preset = pulsePresets[Math.floor(Math.random() * pulsePresets.length)];
  document.getElementById('pulseScore').textContent = preset.score;
  document.getElementById('pulseDesign').textContent = preset.design;
  document.getElementById('pulseTech').textContent = preset.tech;
  document.getElementById('pulseLive').textContent = preset.live;
}

publishButton.addEventListener('click', createPost);
shufflePulseButton.addEventListener('click', refreshPulse);

postInput.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    createPost();
  }
});

filterChips.forEach((chip) => {
  chip.addEventListener('click', () => setFilter(chip.dataset.filter));
});

feedList.addEventListener('click', (event) => {
  const actionButton = event.target.closest('[data-action="like"]');

  if (!actionButton) {
    return;
  }

  const postCard = actionButton.closest('[data-post-id]');
  if (!postCard) {
    return;
  }

  toggleLike(Number(postCard.dataset.postId));
});

renderFeed();
