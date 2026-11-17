document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('menu-toggle');
  const nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const opened = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(opened));
      toggle.setAttribute('aria-label', opened ? 'Закрыть меню' : 'Открыть меню');
    });
  }

  // Dynamic interaction #1: inline client-side form validation.
  document.querySelectorAll('.validated-form').forEach(form => {
    const fields = [...form.querySelectorAll('input, textarea, select')];
    function validate(field) {
      const error = field.closest('.field')?.querySelector('.client-error');
      if (!error) return true;
      let message = '';
      const value = field.value.trim();
      if (field.required && !field.checkValidity()) message = 'Заполните поле корректно.';
      else if (field.type === 'email' && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) message = 'Проверьте адрес электронной почты.';
      else if (field.type === 'tel' && value && !/^\+?[\d\s()\-]+$/.test(value)) message = 'Телефон содержит недопустимые символы.';
      else if (field.type === 'tel' && value && !/^\d{10,15}$/.test(value.replace(/\D/g, ''))) message = 'Телефон должен содержать 10–15 цифр.';
      else if (field.minLength > 0 && value && value.length < field.minLength) message = `Минимум ${field.minLength} символов.`;
      else if (field.maxLength > 0 && value.length > field.maxLength) message = `Максимум ${field.maxLength} символов.`;
      error.textContent = message;
      field.setAttribute('aria-invalid', String(Boolean(message)));
      return !message;
    }
    fields.forEach(field => {
      field.addEventListener('blur', () => validate(field));
      field.addEventListener('input', () => {
        const error = field.closest('.field')?.querySelector('.client-error');
        if (error) error.textContent = '';
        field.removeAttribute('aria-invalid');
      });
    });
    form.addEventListener('submit', event => {
      const invalid = fields.filter(field => !validate(field));
      if (invalid.length) { event.preventDefault(); invalid[0].focus(); }
    });
  });

  // Dynamic interaction #2: live catalog search + filters via own JSON endpoint.
  const filters = document.getElementById('catalog-filter');
  if (!filters) return;
  const output = document.getElementById('live-results');
  const status = document.getElementById('live-status');
  const serverResults = document.getElementById('server-results');
  const pagination = document.querySelector('.pagination');
  const apiUrl = filters.dataset.apiUrl;
  const detailTemplate = filters.dataset.courseUrlTemplate;
  let controller;
  let timer;
  async function refresh() {
    if (controller) controller.abort();
    controller = new AbortController();
    status.textContent = 'Загрузка курсов…';
    status.setAttribute('role', 'status');
    const params = new URLSearchParams(new FormData(filters));
    try {
      const response = await fetch(`${apiUrl}?${params}`, {signal: controller.signal});
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json();
      output.replaceChildren();
      for (const item of data.results) {
        const article = document.createElement('article');
        article.className = 'live-card';
        const link = document.createElement('a');
        link.href = detailTemplate.replace('999999', String(item.id));
        link.textContent = `${item.title} · ${item.language__name} · ${item.level__code}`;
        article.append(link);
        output.append(article);
      }
      status.textContent = data.count ? `Найдено курсов: ${data.count}. Показано: ${data.results.length}.` : 'Ничего не найдено. Измените фильтры.';
      serverResults.hidden = true;
      if (pagination) pagination.hidden = true;
    } catch (error) {
      if (error.name !== 'AbortError') status.textContent = 'Не удалось загрузить курсы. Отправьте форму кнопкой «Найти».';
    }
  }
  filters.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(refresh, 350); });
  filters.addEventListener('change', () => { clearTimeout(timer); refresh(); });
});
