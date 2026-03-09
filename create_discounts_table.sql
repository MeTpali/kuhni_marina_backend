-- SQL скрипт для создания таблицы discounts (скидки)
-- База данных: PostgreSQL

-- 1. Создание ENUM типов для скидок (если еще не созданы)

-- Тип скидки
CREATE TYPE discount_type AS ENUM ('PERCENTAGE', 'FIXED');

-- Область применения скидки
CREATE TYPE discount_scope AS ENUM ('PRODUCT', 'CATEGORY', 'TYPE', 'ALL');

-- Примечание: category_type уже должен быть создан (используется для product_type)
-- Если нет, создайте его:
-- CREATE TYPE category_type AS ENUM ('KITCHEN', 'FURNITURE');

-- 2. Создание таблицы discounts
CREATE TABLE discounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    discount_type discount_type NOT NULL,
    value NUMERIC(10, 2) NOT NULL,
    scope discount_scope NOT NULL,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    product_type category_type,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Создание индексов для оптимизации запросов

-- Составной индекс для фильтрации по датам
CREATE INDEX idx_discount_dates ON discounts(start_date, end_date);

-- Индекс для фильтрации по активности
CREATE INDEX idx_discount_active ON discounts(is_active);

-- Индекс для фильтрации по области применения
CREATE INDEX idx_discount_scope ON discounts(scope);

-- Индекс для сортировки по приоритету
CREATE INDEX idx_discount_priority ON discounts(priority DESC);

-- Индексы для внешних ключей (для быстрых JOIN)
CREATE INDEX idx_discount_campaign_id ON discounts(campaign_id) WHERE campaign_id IS NOT NULL;
CREATE INDEX idx_discount_product_id ON discounts(product_id) WHERE product_id IS NOT NULL;
CREATE INDEX idx_discount_category_id ON discounts(category_id) WHERE category_id IS NOT NULL;

-- 4. Создание триггера для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_discounts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_discounts_updated_at
    BEFORE UPDATE ON discounts
    FOR EACH ROW
    EXECUTE FUNCTION update_discounts_updated_at();

-- 5. Комментарии к таблице и полям (опционально)
COMMENT ON TABLE discounts IS 'Таблица скидок на продукты';
COMMENT ON COLUMN discounts.id IS 'Уникальный идентификатор скидки';
COMMENT ON COLUMN discounts.name IS 'Название акции/скидки';
COMMENT ON COLUMN discounts.discount_type IS 'Тип скидки: PERCENTAGE (процентная) или FIXED (фиксированная)';
COMMENT ON COLUMN discounts.value IS 'Значение скидки (процент или сумма)';
COMMENT ON COLUMN discounts.scope IS 'Область применения: PRODUCT, CATEGORY, TYPE, ALL';
COMMENT ON COLUMN discounts.campaign_id IS 'ID маркетинговой акции, к которой относится скидка';
COMMENT ON COLUMN discounts.product_id IS 'ID продукта (если scope = PRODUCT)';
COMMENT ON COLUMN discounts.category_id IS 'ID категории (если scope = CATEGORY)';
COMMENT ON COLUMN discounts.product_type IS 'Тип продукта (если scope = TYPE)';
COMMENT ON COLUMN discounts.start_date IS 'Дата начала действия скидки';
COMMENT ON COLUMN discounts.end_date IS 'Дата окончания действия скидки';
COMMENT ON COLUMN discounts.is_active IS 'Признак активности скидки';
COMMENT ON COLUMN discounts.priority IS 'Приоритет скидки (чем больше, тем выше приоритет)';
COMMENT ON COLUMN discounts.created_at IS 'Дата создания записи';
COMMENT ON COLUMN discounts.updated_at IS 'Дата последнего обновления записи';
