const cities = [
  "Ангарск","Байкальск","Балаково","Билибино","Волгодонск","Глазов","Десногорск","Димитровград",
  "Железногорск","ЗАТО Заречный","Заречный","Зеленогорск","Краснокаменск","Курчатов","Лесной","Неман",
  "Нововоронеж","Новоуральск","Обнинск","Озерск","Певек","Полярные Зори","Саров","Северск","Снежинск",
  "Советск","Сосновый Бор","Трехгорный","Удомля","Усолье-Сибирское","Электросталь","Энергодар"
];

const DEFAULT_CENTER = [55.76, 37.64];
const DEFAULT_ZOOM = 5;
const MARKER_ICON = 'assets/icons/marker.png';
const MARKER_SIZE = [30, 30];

// === JWT АВТОРИЗАЦИЯ ===
// Функция для получения токена
function getToken() {
    return localStorage.getItem('jwt_token');
}

// Функция для проверки авторизации
function isAuthenticated() {
    return !!getToken();
}

// Функция для получения информации о пользователе
function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// Функция для выхода
function logout() {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user');
    localStorage.removeItem('rd_user'); // удаляем старый формат
    window.location.href = 'index.html';
}

// Функция для авторизованных запросов
async function authFetch(url, options = {}) {
    const token = getToken();
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    return await fetch(url, options);
}

// Функция для проверки авторизации при загрузке
function checkAuthStatus() {
    const user = getUser();
    const authButton = document.getElementById('btn-login');
    
    if (user && authButton) {
        authButton.textContent = `Выйти (${user.first_name || user.email})`;
        authButton.onclick = logout;
        
        // Показываем кнопку добавления, если пользователь авторизован
        const addButton = document.getElementById('btn-add');
        if (addButton) {
            addButton.style.display = 'block';
        }
    }
}
// === КОНЕЦ JWT ФУНКЦИЙ ===

// Ждём, пока DOM построится; затем запускаем инициализацию карты, когда готов ymaps
document.addEventListener('DOMContentLoaded', () => {
  // Проверяем авторизацию при загрузке
  checkAuthStatus();
  
  if (typeof ymaps === 'undefined') {
    console.warn('ymaps не загружен. Проверьте подключение https://api-maps.yandex.ru/2.1/');
    return;
  }
  ymaps.ready(init);
});

function init() {
  // Кешируем DOM-элементы (теперь они точно есть)
  const citySelect = document.getElementById('city-select');
  const addCity = document.getElementById('add-city');
  const categoryListEl = document.getElementById('category-list');
  const nkoListEl = document.getElementById('nko-list');
  const searchInput = document.getElementById('search');

  const modalBackdrop = document.getElementById('modal-backdrop');
  const modalTitle = document.getElementById('modal-title');
  const modalDesc = document.getElementById('modal-desc');
  const modalPhone = document.getElementById('modal-phone');
  const modalAddress = document.getElementById('modal-address');
  const modalImg = document.getElementById('modal-img');
  const modalSite = document.getElementById('modal-site');

  // Безопасные проверки: если важные элементы отсутствуют — логируем и продолжаем (избегаем crash)
  if (!document.getElementById('map')) {
    console.error('Элемент #map не найден в DOM.');
    return;
  }
  if (!nkoListEl) console.warn('#nko-list не найден, список не будет отображён.');

  // populate city selects
  cities.forEach(c => {
    if (citySelect) {
      const o = document.createElement('option'); o.value = c; o.textContent = c; citySelect.appendChild(o);
    }
    if (addCity) {
      const o2 = document.createElement('option'); o2.value = c; o2.textContent = c; addCity.appendChild(o2);
    }
  });

  // Создаём карту
  const map = new ymaps.Map('map', {
    center: DEFAULT_CENTER,
    zoom: DEFAULT_ZOOM,
    controls: []
  });

  // Удаляем ненужные элементы с интерфейса я.карты
  try { map.controls.remove('geolocationControl'); } catch (e) {}
  try { map.controls.remove('searchControl'); } catch (e) {}
  try { map.controls.remove('trafficControl'); } catch (e) {}
  try { map.controls.remove('typeSelector'); } catch (e) {}
  try { map.controls.remove('fullscreenControl'); } catch (e) {}
  try { map.controls.remove('rulerControl'); } catch (e) {}

  // Кластеризатор
  const clusterer = new ymaps.Clusterer({
    clusterDisableClickZoom: false
  });
  map.geoObjects.add(clusterer);

  // Глобальное состояние
  window._items = [];

  // Загрузка и инициализация данных
  (async function loadAndInitData(){
    const items = await loadFromBackendOrDemo();
    window._items = items;
    buildCategories(items);
    renderList(items);
    renderMarkers(items);

    if (!items || items.length === 0) {
      if (nkoListEl) nkoListEl.innerHTML = '<p class="muted">Данные отсутствуют. Убедитесь, что backend запущен.</p>';
    }
  })();

  // --- Функции ---
  function buildCategories(items) {
    if (!categoryListEl) return;
    const categories = Array.from(new Set(items.map(n => n.cat).filter(Boolean)));
    categoryListEl.innerHTML = '';
    categories.forEach(cat => {
      const b = document.createElement('button');
      b.className = 'chip';
      b.textContent = cat;
      b.dataset.cat = cat;
      b.onclick = () => {
        b.classList.toggle('active');
        if (b.classList.contains('active')) b.style.background = 'var(--rosatom-blue)';
        else b.style.background = '';
        applyFilters();
      };
      categoryListEl.appendChild(b);
    });
  }

  function renderList(items) {
    if (!nkoListEl) return;
    nkoListEl.innerHTML = '';
    items.forEach(it => {
      const el = document.createElement('div');
      el.className = 'nko-item';
      el.innerHTML = `<img src="${it.img}" alt="${it.name}"><div style="flex:1"><h4>${it.name}</h4><div class="muted">${it.city} · ${it.cat}</div><div style="margin-top:6px">${it.desc}</div></div>`;
      el.onclick = () => {
        openModal(it);
        if (it.lat && it.lon) {
          map.setCenter([it.lat, it.lon], 12, { duration: 300 });
        }
      };
      nkoListEl.appendChild(el);
    });
  }


function renderMarkers(items) {
    clusterer.removeAll();
    const placemarks = [];
    // Проверка: поддерживает ли устройство hover (обычно true для настольных)
    const supportsHover = window.matchMedia && window.matchMedia('(hover: hover)').matches;
    const CLOSE_DELAY = 100; // мс задержки при закрытии, чтобы избежать мерцания

    items.forEach(it => {
        if (it.lat == null || it.lon == null) return;

        const placemark = new ymaps.Placemark([it.lat, it.lon], {
            //hintContent: it.name,
            balloonContentHeader: it.name,
            balloonContentBody: `<div>${it.city} · ${it.cat}</div><div style="margin-top:6px">${it.desc}</div>`
        }, {
            iconLayout: 'default#image',
            iconImageHref: MARKER_ICON,
            iconImageSize: MARKER_SIZE,
            iconImageOffset: [-MARKER_SIZE[0] / 2, -MARKER_SIZE[1] + 4],
            // Отключаем автоматическое открытие балуна по клику — будем управлять вручную
            openBalloonOnClick: false
        });

        // Таймер для отложенного закрытия (чтобы избежать мерцания)
        let closeTimer = null;

        function scheduleClose() {
            clearCloseTimer();
            closeTimer = setTimeout(() => {
                try { placemark.balloon.close(); } catch (e) { /* ignore */ }
                closeTimer = null;
            }, CLOSE_DELAY);
        }
        function clearCloseTimer() {
            if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
        }

        if (supportsHover) {
            // Открываем на hover маркера
            placemark.events.add('mouseenter', () => {
                clearCloseTimer();
                try { placemark.balloon.open(); } catch (e) { console.warn('Ошибка открытия балуна на hover:', e); }
            });

            // При уходе с маркера — ставим таймер на закрытие
            placemark.events.add('mouseleave', () => {
                scheduleClose();
            });

            // Если API позволяет — держим балун открытым, когда курсор над балуном
            // (иногда placemark.balloon.events может не существовать — поэтому в try/catch)
            try {
                placemark.balloon.events.add('mouseenter', () => {
                    clearCloseTimer();
                });
                placemark.balloon.events.add('mouseleave', () => {
                    scheduleClose();
                });
            } catch (e) {
                // Если не получилось повесить события на balloon — ничего страшного, оставим поведение только по метке
            }
        } else {
            // На устройствах без hover — оставляем клик для открытия балуна (и модалки при необходимости)
            placemark.events.add('click', () => {
                try { placemark.balloon.open(); } catch (e) { /* ignore */ }
            });
        }

        // Сохраняем старое поведение: клик по маркеру также открывает модалку с подробностями
        placemark.events.add('click', () => openModal(it));

        placemarks.push(placemark);
    });

    if (placemarks.length) clusterer.add(placemarks);
}



//   function renderMarkers(items) {
//     clusterer.removeAll();
//     const placemarks = [];
//     items.forEach(it => {
//       if (it.lat == null || it.lon == null) return;
//       const placemark = new ymaps.Placemark([it.lat, it.lon], {
//         hintContent: it.name,
//         balloonContentHeader: it.name,
//         balloonContentBody: `<div>${it.city} · ${it.cat}</div><div style="margin-top:6px">${it.desc}</div>`
//       }, {
//         iconLayout: 'default#image',
//         iconImageHref: MARKER_ICON,
//         iconImageSize: MARKER_SIZE,
//         iconImageOffset: [-MARKER_SIZE[0] / 2, -MARKER_SIZE[1] + 4]
//       });
//       placemark.events.add('click', () => openModal(it));
//       placemarks.push(placemark);
//     });
//     if (placemarks.length) clusterer.add(placemarks);
//   }

  function applyFilters() {
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    const city = citySelect ? citySelect.value : '';
    const activeCats = Array.from(document.querySelectorAll('#category-list .chip.active')).map(b => b.dataset.cat);
    const res = window._items.filter(n => {
      if (city && n.city !== city) return false;
      if (activeCats.length && !activeCats.includes(n.cat)) return false;
      if (q && !(n.name || '').toLowerCase().includes(q)) return false;
      return true;
    });
    renderList(res);
    renderMarkers(res);
  }

  // Модалка (безопасные проверки)
  function openModal(item) {
    if (modalTitle) modalTitle.textContent = item.name || '—';
    if (modalDesc) modalDesc.textContent = item.desc || '—';
    if (modalPhone) modalPhone.textContent = item.phone || '—';
    if (modalAddress) modalAddress.textContent = item.city || item.address || '—';
    if (modalImg) modalImg.src = item.img || '';
    if (modalSite) modalSite.href = item.site || '#';
    if (modalBackdrop) modalBackdrop.style.display = 'flex';
  }
  function closeModal() { if (modalBackdrop) modalBackdrop.style.display = 'none'; }

  if (document.getElementById('modal-close')) document.getElementById('modal-close').onclick = closeModal;
  if (document.getElementById('modal-close2')) document.getElementById('modal-close2').onclick = closeModal;

    // auth / add modal
  const addModal = document.getElementById('modal-add');
  
  function openAuth(){ 
    window.location.href = 'login.html';
  }
  
  function openAdd(){ 
    if(!isAuthenticated()){ 
      openAuth(); 
      return; 
    } 
    if (addModal) addModal.style.display='flex'; 
  }
  
  function closeAdd(){ if (addModal) addModal.style.display='none'; }

  if (document.getElementById('btn-login')) {
    document.getElementById('btn-login').onclick = openAuth;
  }

  if (document.getElementById('btn-add')) document.getElementById('btn-add').onclick = () => openAdd();
  if (document.getElementById('add-submit')) document.getElementById('add-submit').onclick = async () => {
    const name = (document.getElementById('add-name')?.value || '').trim();
    const cat = (document.getElementById('add-cat')?.value || '').trim();
    const desc = (document.getElementById('add-desc')?.value || '').trim();
    const phone = (document.getElementById('add-phone')?.value || '').trim();
    const city = (document.getElementById('add-city')?.value || '');
    if (!name || !cat || !city) { alert('Заполните название, категорию и город'); return; }

    try {
      const payload = { name, category: cat, description: desc, phone, city };
      const res = await authFetch('/api/organizations/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        closeAdd(); 
        alert('Организация отправлена на модерацию. Администратор проверит запись.');
        await initDataReload();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Ошибка отправки');
      }
    } catch (err) {
      console.error('Ошибка отправки организации:', err);
      alert('Ошибка: ' + err.message);
    }
  }

  if (document.getElementById('search-btn')) document.getElementById('search-btn').onclick = applyFilters;
  if (citySelect) citySelect.onchange = applyFilters;
  if (document.getElementById('btn-reset')) document.getElementById('btn-reset').onclick = () => {
    if (searchInput) searchInput.value = '';
    if (citySelect) citySelect.value = '';
    document.querySelectorAll('#category-list .chip').forEach(c => { c.classList.remove('active'); c.style.background = ''; });
    applyFilters();
  };
  if (document.getElementById('btn-show-list')) document.getElementById('btn-show-list').onclick = () => { if (nkoListEl) nkoListEl.scrollIntoView({ behavior: 'smooth' }); };

  window.addEventListener('keydown', e => { if (e.key === 'Escape') { closeModal(); closeAuth(); closeAdd(); } });

  async function initDataReload() {
    const items = await loadFromBackendOrDemo();
    window._items = items;
    buildCategories(items);
    renderList(items);
    renderMarkers(items);
  }

  async function loadFromBackendOrDemo() {
    try {
      const res = await authFetch('/api/organizations/');
      if (!res.ok) throw new Error('no data');
      const data = await res.json();
      const mapped = data.map((o, i) => ({
        id: o.id || i + 1,
        name: o.name,
        city: o.city || '',
        cat: o.category || o.cat || '',
        lat: o.lat,
        lon: o.lon,
        phone: o.phone || '',
        desc: o.description || '',
        img: ('https://picsum.photos/seed/' + (o.id || i) + '/200/200'),
        site: o.website || o.social_links || '#'
      }));
      return mapped;
    } catch (err) {
      console.warn('Backend not available or error fetching organizations:', err);
      return [];
    }
  }
}
