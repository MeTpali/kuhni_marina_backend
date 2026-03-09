-- SQL скрипт для создания таблицы campaigns (маркетинговые акции)
-- База данных: PostgreSQL

CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    slug VARCHAR NOT NULL UNIQUE,
    description TEXT,
    banner_image_url TEXT,
    landing_url TEXT,
    badge_text VARCHAR,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_slug ON campaigns(slug);
CREATE INDEX idx_campaigns_dates ON campaigns(start_date, end_date);
CREATE INDEX idx_campaigns_active ON campaigns(is_active);
CREATE INDEX idx_campaigns_priority ON campaigns(priority DESC);

COMMENT ON TABLE campaigns IS 'Маркетинговые кампании (акции)';
COMMENT ON COLUMN campaigns.name IS 'Название акции';
COMMENT ON COLUMN campaigns.slug IS 'Уникальный SEO-идентификатор';
COMMENT ON COLUMN campaigns.description IS 'Описание акции';
COMMENT ON COLUMN campaigns.banner_image_url IS 'Изображение для баннера акции';
COMMENT ON COLUMN campaigns.landing_url IS 'Ссылка на страницу акции';
COMMENT ON COLUMN campaigns.badge_text IS 'Короткий текст бейджа акции';
COMMENT ON COLUMN campaigns.start_date IS 'Дата начала действия акции';
COMMENT ON COLUMN campaigns.end_date IS 'Дата окончания действия акции';
COMMENT ON COLUMN campaigns.is_active IS 'Признак активности акции';
COMMENT ON COLUMN campaigns.priority IS 'Приоритет акции для сортировки';
