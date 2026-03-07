"""
Стили, скрипты и шаблон HTML для страниц массового добавления изображений.
"""

BULK_IMAGES_CSS = """
:root {
  --bulk-bg: #f4f6f9;
  --bulk-card-bg: #fff;
  --bulk-border: #e2e8f0;
  --bulk-text: #1e293b;
  --bulk-muted: #64748b;
  --bulk-primary: #3b82f6;
  --bulk-primary-hover: #2563eb;
  --bulk-error: #dc2626;
  --bulk-success: #16a34a;
  --bulk-radius: 12px;
  --bulk-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.05);
}
.bulk-page { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bulk-bg); min-height: 100vh; padding: 2rem; color: var(--bulk-text); }
.bulk-container { max-width: 640px; margin: 0 auto; }
.bulk-card { background: var(--bulk-card-bg); border-radius: var(--bulk-radius); box-shadow: var(--bulk-shadow); border: 1px solid var(--bulk-border); padding: 2rem; margin-bottom: 1.5rem; }
.bulk-title { font-size: 1.5rem; font-weight: 600; margin: 0 0 0.5rem 0; color: var(--bulk-text); }
.bulk-subtitle { color: var(--bulk-muted); font-size: 0.9375rem; margin: 0 0 1.5rem 0; line-height: 1.5; }
.bulk-alert { padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1.25rem; font-size: 0.9375rem; }
.bulk-alert-error { background: #fef2f2; color: var(--bulk-error); border: 1px solid #fecaca; }
.bulk-alert-success { background: #f0fdf4; color: var(--bulk-success); border: 1px solid #bbf7d0; }
.bulk-form-group { margin-bottom: 1.25rem; }
.bulk-form-group label { display: block; font-weight: 500; font-size: 0.9375rem; margin-bottom: 0.5rem; color: var(--bulk-text); }
.bulk-input { width: 100%; padding: 0.625rem 0.875rem; border: 1px solid var(--bulk-border); border-radius: 8px; font-size: 0.9375rem; box-sizing: border-box; }
.bulk-input:focus { outline: none; border-color: var(--bulk-primary); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); }
.bulk-textarea { min-height: 200px; resize: vertical; }
.bulk-combo-wrap { position: relative; }
.bulk-combo-input { padding-right: 2.5rem; }
.bulk-combo-dropdown { position: absolute; left: 0; right: 0; top: 100%; margin-top: 2px; background: var(--bulk-card-bg); border: 1px solid var(--bulk-border); border-radius: 8px; box-shadow: var(--bulk-shadow); max-height: 260px; overflow-y: auto; z-index: 100; display: none; }
.bulk-combo-dropdown.show { display: block; }
.bulk-combo-item { padding: 0.625rem 0.875rem; cursor: pointer; font-size: 0.9375rem; border-bottom: 1px solid var(--bulk-border); }
.bulk-combo-item:last-child { border-bottom: none; }
.bulk-combo-item:hover, .bulk-combo-item.selected { background: #eff6ff; color: var(--bulk-primary); }
.bulk-combo-item small { color: var(--bulk-muted); margin-left: 0.5rem; }
.bulk-btn { padding: 0.625rem 1.25rem; background: var(--bulk-primary); color: #fff; border: none; border-radius: 8px; font-size: 0.9375rem; font-weight: 500; cursor: pointer; }
.bulk-btn:hover { background: var(--bulk-primary-hover); }
.bulk-back { display: inline-block; margin-top: 1rem; color: var(--bulk-muted); font-size: 0.9375rem; text-decoration: none; }
.bulk-back:hover { color: var(--bulk-primary); }
"""

BULK_IMAGES_JS_COMBO = """
function initSearchCombo(inputId, hiddenId, searchUrl, placeholder) {
  var input = document.getElementById(inputId);
  var hidden = document.getElementById(hiddenId);
  if (!input || !hidden) return;
  var dropdown = document.createElement('div');
  dropdown.className = 'bulk-combo-dropdown';
  dropdown.id = inputId + '-dropdown';
  input.parentNode.appendChild(dropdown);
  var debounce = null;
  input.placeholder = placeholder;
  input.addEventListener('input', function() {
    hidden.value = '';
    var q = (input.value || '').trim();
    if (q.length < 2) { dropdown.classList.remove('show'); dropdown.innerHTML = ''; return; }
    clearTimeout(debounce);
    debounce = setTimeout(function() {
      fetch(searchUrl + (searchUrl.indexOf('?') >= 0 ? '&' : '?') + 'q=' + encodeURIComponent(q))
        .then(function(r) { return r.json(); })
        .then(function(items) {
          dropdown.innerHTML = '';
          if (items.length === 0) { dropdown.innerHTML = '<div class="bulk-combo-item">Ничего не найдено</div>'; }
          else items.forEach(function(it) {
            var div = document.createElement('div');
            div.className = 'bulk-combo-item';
            div.dataset.id = it.id;
            div.dataset.name = it.name;
            div.innerHTML = it.name + '<small>id: ' + it.id + '</small>';
            div.addEventListener('mousedown', function(e) {
              e.preventDefault();
              e.stopPropagation();
              hidden.value = it.id;
              input.value = it.name;
              input.style.color = 'var(--bulk-text)';
              input.style.fontWeight = '500';
              dropdown.classList.remove('show');
            });
            dropdown.appendChild(div);
          });
          dropdown.classList.add('show');
        })
        .catch(function() { dropdown.classList.remove('show'); });
    }, 200);
  });
  input.addEventListener('focus', function() {
    if (dropdown.innerHTML) dropdown.classList.add('show');
    input.style.color = '';
    input.style.fontWeight = '';
  });
  input.addEventListener('blur', function() { setTimeout(function() { dropdown.classList.remove('show'); }, 200); });
  document.addEventListener('click', function(e) {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) dropdown.classList.remove('show');
  });
}
"""


def bulk_images_html(
    *,
    title: str,
    subtitle: str,
    entity_label: str,
    search_placeholder: str,
    search_api_url: str,
    input_id: str,
    hidden_name: str,
    error: str = "",
    success: str = "",
) -> str:
    alert_error = f'<div class="bulk-alert bulk-alert-error">{error}</div>' if error else ""
    alert_success = f'<div class="bulk-alert bulk-alert-success">{success}</div>' if success else ""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{BULK_IMAGES_CSS}</style>
</head>
<body class="bulk-page">
  <div class="bulk-container">
    <div class="bulk-card">
      <h1 class="bulk-title">{title}</h1>
      <p class="bulk-subtitle">{subtitle}</p>
      {alert_error}
      {alert_success}
      <form method="post" action="">
        <div class="bulk-form-group">
          <label for="{input_id}">{entity_label}</label>
          <div class="bulk-combo-wrap">
            <input type="text" id="{input_id}" class="bulk-input bulk-combo-input" autocomplete="off" required>
            <input type="hidden" name="{hidden_name}" id="{input_id}_id">
          </div>
        </div>
        <div class="bulk-form-group">
          <label for="image_urls">URL изображений (по одному на строку)</label>
          <textarea id="image_urls" name="image_urls" class="bulk-input bulk-textarea" placeholder="https://example.com/1.jpg&#10;https://example.com/2.jpg"></textarea>
        </div>
        <div class="bulk-form-group">
          <label for="main_index">Номер главного изображения (необязательно, 1 = первое)</label>
          <input type="number" id="main_index" name="main_index" class="bulk-input" min="1" placeholder="1">
        </div>
        <button type="submit" class="bulk-btn">Сохранить</button>
      </form>
    </div>
    <a href="/admin/" class="bulk-back">← Назад в админку</a>
  </div>
  <script>{BULK_IMAGES_JS_COMBO}</script>
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      initSearchCombo("{input_id}", "{input_id}_id", "{search_api_url}", "{search_placeholder}");
      document.querySelector('form').addEventListener('submit', function(e) {{
        if (!document.getElementById("{input_id}_id").value) {{
          e.preventDefault();
          alert("Выберите элемент из списка по подсказкам.");
        }}
      }});
    }});
  </script>
</body>
</html>"""
