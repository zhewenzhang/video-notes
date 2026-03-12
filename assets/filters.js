/**
 * 视频笔记筛选功能
 * 支持频道筛选、标签筛选、日期筛选、排序和统计
 */

// 全局状态
const FilterState = {
  channel: 'all',
  tag: 'all',
  dateRange: 'all',
  sortBy: 'date-desc',
  notes: []
};

// 初始化筛选器
function initFilters(notes) {
  FilterState.notes = notes;
  renderFilters();
  applyFilters();
  setupURLHashListener();
  
  // 初始加载 URL 哈希
  loadFromURLHash();
}

// 渲染筛选器 UI
function renderFilters() {
  const channels = getAllChannels();
  const tags = getAllTags();
  
  const filtersHTML = `
    <div class="filters-container">
      <!-- 移动端展开/收起按钮 -->
      <button class="filters-toggle" id="filtersToggle" onclick="toggleFilters()">
        <span class="toggle-icon">▼</span>
        <span>筛选器</span>
        <span class="result-count" id="resultCount"></span>
      </button>
      
      <div class="filters-panel" id="filtersPanel">
        <!-- 统计面板 -->
        <div class="stats-panel">
          <div class="stat-item">
            <span class="stat-value" id="totalNotes">${notes.length}</span>
            <span class="stat-label">总笔记</span>
          </div>
          <div class="stat-item">
            <span class="stat-value" id="totalChannels">${channels.length}</span>
            <span class="stat-label">频道</span>
          </div>
          <div class="stat-item">
            <span class="stat-value" id="totalTags">${tags.length}</span>
            <span class="stat-label">标签</span>
          </div>
        </div>
        
        <!-- 频道筛选 -->
        <div class="filter-section">
          <h3 class="filter-title">📺 频道</h3>
          <div class="filter-buttons" id="channelFilters">
            <button class="filter-btn active" data-filter="channel" data-value="all">全部</button>
            ${channels.map(ch => `
              <button class="filter-btn" data-filter="channel" data-value="${escapeHtml(ch)}">${escapeHtml(ch)}</button>
            `).join('')}
          </div>
        </div>
        
        <!-- 标签筛选 -->
        <div class="filter-section">
          <h3 class="filter-title">🏷️ 标签</h3>
          <div class="tag-cloud" id="tagFilters">
            <button class="tag-btn active" data-filter="tag" data-value="all">全部</button>
            ${tags.slice(0, 30).map(tag => `
              <button class="tag-btn" data-filter="tag" data-value="${escapeHtml(tag)}">${escapeHtml(tag)}</button>
            `).join('')}
          </div>
          ${tags.length > 30 ? `<p class="tag-more">显示前 30 个热门标签</p>` : ''}
        </div>
        
        <!-- 日期筛选 -->
        <div class="filter-section">
          <h3 class="filter-title">📅 日期</h3>
          <div class="filter-buttons" id="dateFilters">
            <button class="filter-btn active" data-filter="date" data-value="all">全部</button>
            <button class="filter-btn" data-filter="date" data-value="week">本周</button>
            <button class="filter-btn" data-filter="date" data-value="month">本月</button>
          </div>
        </div>
        
        <!-- 排序 -->
        <div class="filter-section">
          <h3 class="filter-title">🔀 排序</h3>
          <div class="filter-buttons" id="sortFilters">
            <button class="filter-btn active" data-filter="sort" data-value="date-desc">最新优先</button>
            <button class="filter-btn" data-filter="sort" data-value="date-asc">最旧优先</button>
            <button class="filter-btn" data-filter="sort" data-value="channel">按频道</button>
          </div>
        </div>
        
        <!-- 清除筛选 -->
        <div class="filter-actions">
          <button class="clear-filters" onclick="clearAllFilters()">清除所有筛选</button>
        </div>
      </div>
    </div>
  `;
  
  // 插入到搜索框之后
  const searchBox = document.getElementById('searchInput');
  if (searchBox) {
    const div = document.createElement('div');
    div.innerHTML = filtersHTML;
    searchBox.parentNode.insertBefore(div.firstChild, searchBox.nextSibling);
  }
  
  // 绑定事件
  setupFilterEvents();
}

// 设置筛选器事件
function setupFilterEvents() {
  document.querySelectorAll('.filter-btn, .tag-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const filter = e.target.dataset.filter;
      const value = e.target.dataset.value;
      
      // 更新状态
      if (filter === 'channel') FilterState.channel = value;
      if (filter === 'tag') FilterState.tag = value;
      if (filter === 'date') FilterState.dateRange = value;
      if (filter === 'sort') FilterState.sortBy = value;
      
      // 更新 UI
      document.querySelectorAll(`[data-filter="${filter}"]`).forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      
      // 应用筛选
      applyFilters();
      updateURLHash();
    });
  });
}

// 切换筛选器面板（移动端）
function toggleFilters() {
  const panel = document.getElementById('filtersPanel');
  const icon = document.querySelector('.toggle-icon');
  panel.classList.toggle('collapsed');
  icon.textContent = panel.classList.contains('collapsed') ? '▶' : '▼';
}

// 获取所有频道
function getAllChannels() {
  const channels = new Set();
  FilterState.notes.forEach(note => {
    if (note.channel) {
      // 简化频道名
      const simpleChannel = note.channel.split('(')[0].trim();
      channels.add(simpleChannel);
    }
  });
  return Array.from(channels).sort();
}

// 获取所有标签
function getAllTags() {
  const tags = new Map();
  FilterState.notes.forEach(note => {
    note.tags.forEach(tag => {
      tags.set(tag, (tags.get(tag) || 0) + 1);
    });
  });
  // 按频率排序
  return Array.from(tags.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([tag]) => tag);
}

// 应用筛选
function applyFilters() {
  const now = new Date();
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  
  let filtered = FilterState.notes.filter(note => {
    // 频道筛选
    if (FilterState.channel !== 'all') {
      const noteChannel = note.channel ? note.channel.split('(')[0].trim() : '';
      if (noteChannel !== FilterState.channel) return false;
    }
    
    // 标签筛选
    if (FilterState.tag !== 'all') {
      if (!note.tags.includes(FilterState.tag)) return false;
    }
    
    // 日期筛选
    if (FilterState.dateRange !== 'all') {
      const noteDate = note.date ? new Date(note.date) : new Date(0);
      if (FilterState.dateRange === 'week' && noteDate < weekAgo) return false;
      if (FilterState.dateRange === 'month' && noteDate < monthAgo) return false;
    }
    
    return true;
  });
  
  // 排序
  filtered.sort((a, b) => {
    if (FilterState.sortBy === 'date-desc') {
      return new Date(b.date || 0) - new Date(a.date || 0);
    } else if (FilterState.sortBy === 'date-asc') {
      return new Date(a.date || 0) - new Date(b.date || 0);
    } else if (FilterState.sortBy === 'channel') {
      return (a.channel || '').localeCompare(b.channel || '');
    }
    return 0;
  });
  
  // 更新显示
  updateNoteCards(filtered);
  updateStats(filtered);
  updateResultCount(filtered.length);
}

// 更新笔记卡片显示
function updateNoteCards(notes) {
  const cards = document.querySelectorAll('.note-card');
  const noteGrid = document.querySelector('.note-grid');
  
  if (!noteGrid) return;
  
  // 隐藏所有卡片
  cards.forEach(card => card.style.display = 'none');
  
  // 显示匹配的卡片
  notes.forEach(note => {
    const htmlName = note.filename.replace('.md', '.html');
    const card = Array.from(cards).find(c => 
      c.querySelector(`a[href="./insights/${htmlName}"]`)
    );
    if (card) card.style.display = 'block';
  });
  
  // 如果没有匹配的笔记
  const existingEmpty = noteGrid.querySelector('.empty-message');
  if (existingEmpty) existingEmpty.remove();
  
  if (notes.length === 0) {
    const emptyMsg = document.createElement('div');
    emptyMsg.className = 'empty-message';
    emptyMsg.innerHTML = '<p>😕 没有找到匹配的笔记</p><p>尝试清除筛选条件</p>';
    noteGrid.appendChild(emptyMsg);
  }
}

// 更新统计
function updateStats(notes) {
  const channels = new Set();
  const tags = new Map();
  
  notes.forEach(note => {
    if (note.channel) {
      channels.add(note.channel.split('(')[0].trim());
    }
    note.tags.forEach(tag => {
      tags.set(tag, (tags.get(tag) || 0) + 1);
    });
  });
  
  document.getElementById('totalNotes').textContent = notes.length;
  document.getElementById('totalChannels').textContent = channels.size;
  document.getElementById('totalTags').textContent = tags.size;
}

// 更新结果计数
function updateResultCount(count) {
  const countEl = document.getElementById('resultCount');
  if (countEl) {
    countEl.textContent = `${count}篇`;
  }
}

// 清除所有筛选
function clearAllFilters() {
  FilterState.channel = 'all';
  FilterState.tag = 'all';
  FilterState.dateRange = 'all';
  FilterState.sortBy = 'date-desc';
  
  // 重置 UI
  document.querySelectorAll('.filter-btn, .tag-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.value === 'all') btn.classList.add('active');
  });
  
  applyFilters();
  updateURLHash();
}

// URL 哈希处理
function updateURLHash() {
  const params = new URLSearchParams();
  if (FilterState.channel !== 'all') params.set('channel', FilterState.channel);
  if (FilterState.tag !== 'all') params.set('tag', FilterState.tag);
  if (FilterState.dateRange !== 'all') params.set('date', FilterState.dateRange);
  if (FilterState.sortBy !== 'date-desc') params.set('sort', FilterState.sortBy);
  
  const hash = params.toString();
  if (hash) {
    window.history.pushState({}, '', '#' + hash);
  } else {
    window.history.pushState({}, '', window.location.pathname);
  }
}

function loadFromURLHash() {
  const hash = window.location.hash.slice(1);
  if (!hash) return;
  
  const params = new URLSearchParams(hash);
  
  if (params.get('channel')) {
    FilterState.channel = params.get('channel');
    setActiveButton('channel', FilterState.channel);
  }
  if (params.get('tag')) {
    FilterState.tag = params.get('tag');
    setActiveButton('tag', FilterState.tag);
  }
  if (params.get('date')) {
    FilterState.dateRange = params.get('date');
    setActiveButton('date', FilterState.dateRange);
  }
  if (params.get('sort')) {
    FilterState.sortBy = params.get('sort');
    setActiveButton('sort', FilterState.sortBy);
  }
  
  applyFilters();
}

function setupURLHashListener() {
  window.addEventListener('popstate', () => {
    loadFromURLHash();
  });
}

function setActiveButton(filter, value) {
  document.querySelectorAll(`[data-filter="${filter}"]`).forEach(btn => {
    btn.classList.toggle('active', btn.dataset.value === value);
  });
}

// HTML 转义
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// 导出到全局
window.initFilters = initFilters;
window.toggleFilters = toggleFilters;
window.clearAllFilters = clearAllFilters;
