-- Массовое заполнение тестовыми данными (PostgreSQL)
-- ВНИМАНИЕ: скрипт очищает таблицы через TRUNCATE ... RESTART IDENTITY CASCADE
-- Запуск: psql -d <db_name> -f seed_large_test_data.sql

BEGIN;

TRUNCATE TABLE
    banners,
    measure_requests,
    project_products,
    project_images,
    projects,
    reviews,
    product_attributes,
    attributes,
    product_images,
    products,
    categories,
    users
RESTART IDENTITY CASCADE;

-- Если таблицы campaigns/discounts есть в базе, очищаем их.
DO $$
BEGIN
    IF to_regclass('public.campaigns') IS NOT NULL THEN
        EXECUTE 'TRUNCATE TABLE campaigns RESTART IDENTITY CASCADE';
    END IF;
    IF to_regclass('public.discounts') IS NOT NULL THEN
        EXECUTE 'TRUNCATE TABLE discounts RESTART IDENTITY CASCADE';
    END IF;
END $$;

-- ------------------------------------------------------------
-- USERS
-- ------------------------------------------------------------
INSERT INTO users (full_name, phone, email, password_hash, role, created_at, updated_at)
SELECT
    'Пользователь ' || g,
    '+7999' || lpad((1000000 + g)::text, 7, '0'),
    'user' || g || '@example.test',
    'test_hash_' || g,
    CASE
        WHEN g <= 10 THEN 'ADMIN'::user_role
        WHEN g <= 80 THEN 'MANAGER'::user_role
        ELSE 'CUSTOMER'::user_role
    END,
    NOW() - (random() * interval '365 days'),
    NOW()
FROM generate_series(1, 2000) AS g;

-- ------------------------------------------------------------
-- CATEGORIES (иерархия)
-- ------------------------------------------------------------
INSERT INTO categories (name, slug, parent_id, type, created_at, is_active)
VALUES
    ('Кухни', 'kitchen', NULL, 'KITCHEN', NOW(), TRUE),
    ('Корпусная мебель', 'furniture', NULL, 'FURNITURE', NOW(), TRUE),

    ('Угловые кухни', 'kitchen-corner', 1, 'KITCHEN', NOW(), TRUE),
    ('Прямые кухни', 'kitchen-linear', 1, 'KITCHEN', NOW(), TRUE),
    ('П-образные кухни', 'kitchen-u-shaped', 1, 'KITCHEN', NOW(), TRUE),
    ('Кухни с островом', 'kitchen-island', 1, 'KITCHEN', NOW(), TRUE),
    ('Кухни МДФ', 'kitchen-mdf', 1, 'KITCHEN', NOW(), TRUE),
    ('Кухни эмаль', 'kitchen-enamel', 1, 'KITCHEN', NOW(), TRUE),
    ('Классические кухни', 'kitchen-classic', 1, 'KITCHEN', NOW(), TRUE),
    ('Современные кухни', 'kitchen-modern', 1, 'KITCHEN', NOW(), TRUE),

    ('Шкафы-купе', 'furniture-wardrobes', 2, 'FURNITURE', NOW(), TRUE),
    ('Распашные шкафы', 'furniture-cabinets', 2, 'FURNITURE', NOW(), TRUE),
    ('Прихожие', 'furniture-hallway', 2, 'FURNITURE', NOW(), TRUE),
    ('Гардеробные', 'furniture-dressing', 2, 'FURNITURE', NOW(), TRUE),
    ('ТВ-тумбы', 'furniture-tv-stands', 2, 'FURNITURE', NOW(), TRUE),
    ('Комоды', 'furniture-dressers', 2, 'FURNITURE', NOW(), TRUE),
    ('Стеллажи', 'furniture-shelves', 2, 'FURNITURE', NOW(), TRUE),
    ('Офисная мебель', 'furniture-office', 2, 'FURNITURE', NOW(), TRUE);

-- ------------------------------------------------------------
-- ATTRIBUTES
-- ------------------------------------------------------------
INSERT INTO attributes (name, unit)
VALUES
    ('Ширина', 'см'),
    ('Высота', 'см'),
    ('Глубина', 'см'),
    ('Материал фасада', NULL),
    ('Материал корпуса', NULL),
    ('Цвет', NULL),
    ('Фурнитура', NULL),
    ('Количество модулей', 'шт'),
    ('Толщина столешницы', 'мм'),
    ('Стиль', NULL),
    ('Гарантия', 'мес'),
    ('Срок изготовления', 'дней');

-- ------------------------------------------------------------
-- PRODUCTS
-- ------------------------------------------------------------
INSERT INTO products (
    category_id,
    name,
    slug,
    description,
    price,
    is_new,
    is_hit,
    type,
    is_active,
    created_at,
    updated_at
)
SELECT
    c.id,
    CASE
        WHEN c.type = 'KITCHEN'::category_type THEN 'Кухня модель #' || g
        ELSE 'Мебель модель #' || g
    END,
    CASE
        WHEN c.type = 'KITCHEN'::category_type THEN 'kitchen-product-' || g
        ELSE 'furniture-product-' || g
    END,
    'Тестовое описание товара #' || g,
    round((15000 + random() * 285000)::numeric, 2),
    (random() < 0.20),
    (random() < 0.12),
    c.type,
    (random() < 0.96),
    NOW() - (random() * interval '730 days'),
    NOW()
FROM generate_series(1, 12000) AS g
CROSS JOIN LATERAL (
    SELECT id, type
    FROM categories
    WHERE parent_id IS NOT NULL
    ORDER BY random()
    LIMIT 1
) AS c;

-- ------------------------------------------------------------
-- PRODUCT IMAGES (по 2-5 изображений на товар)
-- ------------------------------------------------------------
INSERT INTO product_images (product_id, image_url, is_main)
SELECT
    p.id,
    ip.url,
    (i.img_index = 1)
FROM products p
CROSS JOIN LATERAL (
    SELECT generate_series(1, 2 + floor(random() * 4)::int) AS img_index
) AS i
CROSS JOIN LATERAL (
    SELECT url
    FROM (
        SELECT *
        FROM unnest(
            ARRAY[
                'https://media.2x2tv.ru/content/images/size/w1440h1440/2024/10/Satoru_Gojo_arrives_on_the_battlefield_28Anime29-2.jpg',
                'https://static.kinoafisha.info/k/articles/1200/upload/editor/image-20251125130603-1.jpg.webp',
                'https://icdn.lenta.ru/images/2025/03/04/13/20250304135448840/detail_3226c506cc282f7188c2730bfc75013a.jpg',
                'https://external-preview.redd.it/jujutsu-kaisen-gojo-satoru-blue-aura-live-wallpaper-v0-9XpIB_Gxut2AyJkjyNOGjJQrHUZIPcYLTxp3KRokD5I.jpg?auto=webp&s=28bb304bcbcea27063d9b4960ecb61ff39b341bc',
                'https://cdn.ongaku.one/post_media/48dfdd16-7af6-11ee-a798-1649692e8fbe/max1000',
                'https://photobooth.cdn.sports.ru/preset/message/6/ee/3e8089cdb4aecbc39b79c3fa79cab.webp?f=webp&q=90&s=2x&w=730',
                'https://photobooth.cdn.sports.ru/preset/message/5/b9/f6d4f6f9a492dbec41815aad7f23f.jpeg?f=webp&q=90&s=2x&w=730',
                'https://photobooth.cdn.sports.ru/preset/message/6/ae/8e35a1ac94e02ae62e25c76a1f90e.jpeg?f=webp&q=90&s=2x&w=730',
                'https://preview.redd.it/aura-moments-from-gojo-what-did-i-miss-v0-pj5nreiycfhf1.png?width=1280&format=png&auto=webp&s=f8f6c268a21c9e4fd30015dad43a43212babaf64'
            ]
        ) WITH ORDINALITY AS t(url, idx)
    ) pool
    WHERE pool.idx = 1 + ((p.id + i.img_index - 1) % 9)
) AS ip;

-- ------------------------------------------------------------
-- PRODUCT ATTRIBUTES (8 характеристик на товар)
-- ------------------------------------------------------------
INSERT INTO product_attributes (product_id, attribute_id, value)
SELECT
    p.id,
    pa.attribute_id,
    CASE pa.attribute_id
        WHEN 1 THEN (180 + floor(random() * 241))::int::text
        WHEN 2 THEN (200 + floor(random() * 61))::int::text
        WHEN 3 THEN (45 + floor(random() * 26))::int::text
        WHEN 4 THEN (ARRAY['МДФ', 'Массив', 'Пластик', 'Шпон'])[1 + floor(random() * 4)::int]
        WHEN 5 THEN (ARRAY['ЛДСП', 'МДФ', 'Фанера'])[1 + floor(random() * 3)::int]
        WHEN 6 THEN (ARRAY['Белый', 'Графит', 'Дуб', 'Бежевый', 'Черный'])[1 + floor(random() * 5)::int]
        WHEN 7 THEN (ARRAY['Blum', 'Hettich', 'Boyard', 'GTV'])[1 + floor(random() * 4)::int]
        WHEN 8 THEN (3 + floor(random() * 8))::int::text
        WHEN 9 THEN (26 + floor(random() * 13))::int::text
        WHEN 10 THEN (ARRAY['Современный', 'Классический', 'Сканди', 'Лофт'])[1 + floor(random() * 4)::int]
        WHEN 11 THEN (12 + floor(random() * 49))::int::text
        WHEN 12 THEN (10 + floor(random() * 41))::int::text
        ELSE 'N/A'
    END
FROM products p
CROSS JOIN LATERAL (
    SELECT attribute_id
    FROM (
        SELECT id AS attribute_id
        FROM attributes
        ORDER BY random()
        LIMIT 8
    ) a
) pa;

-- ------------------------------------------------------------
-- REVIEWS
-- ------------------------------------------------------------
INSERT INTO reviews (product_id, user_id, author_name, rating, text, created_at, is_approved)
SELECT
    rp.product_id,
    u.id,
    COALESCE(u.full_name, 'Покупатель #' || u.id),
    1 + floor(random() * 5)::int,
    'Тестовый отзыв #' || gs.n || ' для товара #' || rp.product_id || '. Качество и сервис проверяем в нагрузочном сценарии.',
    NOW() - (random() * interval '540 days'),
    (random() < 0.88)
FROM (
    SELECT
        p.id AS product_id,
        CASE
            WHEN row_number() OVER (ORDER BY p.id) % 3 = 1 THEN 0
            WHEN row_number() OVER (ORDER BY p.id) % 3 = 2 THEN 10
            ELSE 30
        END AS review_count
    FROM products p
) rp
JOIN LATERAL generate_series(1, rp.review_count) AS gs(n) ON rp.review_count > 0
JOIN users u ON u.id = 1 + ((rp.product_id * 37 + gs.n * 13) % 2000);

-- ------------------------------------------------------------
-- PROJECTS
-- ------------------------------------------------------------
INSERT INTO projects (name, description, location, created_at)
SELECT
    'Проект #' || g,
    'Тестовый реализованный проект #' || g || ' для проверки витрины и карточек.',
    (ARRAY['Вязники', 'Владимир', 'Ковров', 'Муром', 'Гусь-Хрустальный'])[1 + floor(random() * 5)::int],
    NOW() - (random() * interval '900 days')
FROM generate_series(1, 1200) AS g;

-- ------------------------------------------------------------
-- PROJECT IMAGES (по 2-5 изображений на проект)
-- ------------------------------------------------------------
INSERT INTO project_images (project_id, image_url, is_main)
SELECT
    pr.id,
    ip.url,
    (i.img_index = 1)
FROM projects pr
CROSS JOIN LATERAL (
    SELECT generate_series(1, 2 + floor(random() * 4)::int) AS img_index
) AS i
CROSS JOIN LATERAL (
    SELECT url
    FROM (
        SELECT *
        FROM unnest(
            ARRAY[
                'https://media.2x2tv.ru/content/images/size/w1440h1440/2024/10/Satoru_Gojo_arrives_on_the_battlefield_28Anime29-2.jpg',
                'https://static.kinoafisha.info/k/articles/1200/upload/editor/image-20251125130603-1.jpg.webp',
                'https://icdn.lenta.ru/images/2025/03/04/13/20250304135448840/detail_3226c506cc282f7188c2730bfc75013a.jpg',
                'https://external-preview.redd.it/jujutsu-kaisen-gojo-satoru-blue-aura-live-wallpaper-v0-9XpIB_Gxut2AyJkjyNOGjJQrHUZIPcYLTxp3KRokD5I.jpg?auto=webp&s=28bb304bcbcea27063d9b4960ecb61ff39b341bc',
                'https://cdn.ongaku.one/post_media/48dfdd16-7af6-11ee-a798-1649692e8fbe/max1000',
                'https://photobooth.cdn.sports.ru/preset/message/6/ee/3e8089cdb4aecbc39b79c3fa79cab.webp?f=webp&q=90&s=2x&w=730',
                'https://photobooth.cdn.sports.ru/preset/message/5/b9/f6d4f6f9a492dbec41815aad7f23f.jpeg?f=webp&q=90&s=2x&w=730',
                'https://photobooth.cdn.sports.ru/preset/message/6/ae/8e35a1ac94e02ae62e25c76a1f90e.jpeg?f=webp&q=90&s=2x&w=730',
                'https://preview.redd.it/aura-moments-from-gojo-what-did-i-miss-v0-pj5nreiycfhf1.png?width=1280&format=png&auto=webp&s=f8f6c268a21c9e4fd30015dad43a43212babaf64'
            ]
        ) WITH ORDINALITY AS t(url, idx)
    ) pool
    WHERE pool.idx = 1 + ((pr.id + i.img_index - 1) % 9)
) AS ip;

-- ------------------------------------------------------------
-- PROJECT PRODUCTS (2-10 товаров для половины проектов, из первых 100 товаров)
-- ------------------------------------------------------------
INSERT INTO project_products (project_id, product_id)
SELECT
    sp.project_id,
    fp.product_id
FROM (
    SELECT
        p.id AS project_id,
        2 + ((p.id * 7) % 9) AS product_count,
        1 + ((p.id * 13) % 100) AS start_idx
    FROM (
        SELECT
            id,
            row_number() OVER (ORDER BY id) AS rn,
            count(*) OVER () AS total_count
        FROM projects
    ) p
    WHERE p.rn <= p.total_count / 2
) sp
JOIN generate_series(0, 9) AS gs(step) ON gs.step < sp.product_count
JOIN (
    SELECT
        pp.id AS product_id,
        row_number() OVER (ORDER BY pp.id) AS rn
    FROM (
        SELECT id
        FROM products
        ORDER BY id
        LIMIT 100
    ) pp
) fp ON fp.rn = 1 + ((sp.start_idx - 1 + gs.step) % 100);

-- ------------------------------------------------------------
-- MEASURE REQUESTS
-- ------------------------------------------------------------
INSERT INTO measure_requests (full_name, phone, address, preferred_date, comment, status, created_at)
SELECT
    'Клиент ' || g,
    '+7999' || lpad((2000000 + g)::text, 7, '0'),
    'г. Вязники, ул. Тестовая, д. ' || (1 + floor(random() * 180))::int,
    CURRENT_DATE + (floor(random() * 45)::int - 15),
    CASE
        WHEN random() < 0.4 THEN 'Нужен выезд в вечернее время'
        WHEN random() < 0.7 THEN 'Есть технический план помещения'
        ELSE NULL
    END,
    (ARRAY['NEW', 'IN_PROGRESS', 'DONE', 'CANCELLED'])[1 + floor(random() * 4)::int]::measure_request_status,
    NOW() - (random() * interval '365 days')
FROM generate_series(1, 7000) AS g;

-- ------------------------------------------------------------
-- BANNERS
-- ------------------------------------------------------------
INSERT INTO banners (title, image_url, link_url, position, is_active)
SELECT
    'Баннер #' || g,
    (
        ARRAY[
            'https://abrakadabra.fun/uploads/posts/2022-03/1646387750_5-abrakadabra-fun-p-magicheskaya-bitva-zastavka-na-telefon-8.png',
            'https://vsthemes.org/uploads/posts/2024-07/satoru-gojo.webp',
            'https://vsthemes.org/uploads/posts/2021-09/1632783838_1141570-2.webp',
            'https://i.redd.it/y6gjfxwu6zn71.jpg',
            'https://abrakadabra.fun/uploads/posts/2021-12/1639950507_1-abrakadabra-fun-p-oboi-magicheskaya-bitva-na-pk-1.jpg'
        ]
    )[1 + ((g - 1) % 5)],
    CASE
        WHEN g % 3 = 0 THEN '/catalog/kitchen'
        WHEN g % 3 = 1 THEN '/catalog/furniture'
        ELSE '/projects'
    END,
    g,
    (random() < 0.85)
FROM generate_series(1, 60) AS g;

-- ------------------------------------------------------------
-- CAMPAIGNS (если таблица существует)
-- ------------------------------------------------------------
DO $$
BEGIN
    IF to_regclass('public.campaigns') IS NOT NULL THEN
        INSERT INTO campaigns (
            name,
            slug,
            description,
            banner_image_url,
            landing_url,
            badge_text,
            start_date,
            end_date,
            is_active,
            priority,
            created_at,
            updated_at
        )
        VALUES
            ('Весенняя распродажа', 'spring-sale', 'Сезонная распродажа на популярные позиции.', 'https://vsthemes.org/uploads/posts/2024-07/satoru-gojo.webp', '/campaigns/spring-sale', '-15%', NOW() - interval '10 days', NOW() + interval '45 days', TRUE, 50, NOW(), NOW()),
            ('Новинки месяца', 'new-month', 'Спецусловия на новые модели.', 'https://i.redd.it/y6gjfxwu6zn71.jpg', '/campaigns/new-month', 'NEW', NOW() - interval '5 days', NOW() + interval '30 days', TRUE, 40, NOW(), NOW()),
            ('Суперцены на кухни', 'kitchen-hot', 'Акция на кухни под заказ.', 'https://abrakadabra.fun/uploads/posts/2022-03/1646387750_5-abrakadabra-fun-p-magicheskaya-bitva-zastavka-na-telefon-8.png', '/campaigns/kitchen-hot', '-20%', NOW() - interval '2 days', NOW() + interval '60 days', TRUE, 60, NOW(), NOW()),
            ('Мебель для гостиной', 'living-room', 'Предложение для гостиных и ТВ-зон.', 'https://vsthemes.org/uploads/posts/2021-09/1632783838_1141570-2.webp', '/campaigns/living-room', 'ХИТ', NOW() - interval '1 days', NOW() + interval '35 days', TRUE, 35, NOW(), NOW()),
            ('Скидка на шкафы', 'wardrobe-deals', 'Скидки на шкафы и гардеробные системы.', 'https://vsthemes.org/uploads/posts/2024-07/satoru-gojo.webp', '/campaigns/wardrobe-deals', '-12%', NOW() - interval '7 days', NOW() + interval '28 days', TRUE, 32, NOW(), NOW()),
            ('Комплект недели', 'weekly-set', 'Специальная цена на комплект мебели.', 'https://i.redd.it/y6gjfxwu6zn71.jpg', '/campaigns/weekly-set', 'WEEK', NOW() - interval '3 days', NOW() + interval '11 days', TRUE, 25, NOW(), NOW()),
            ('Осенний марафон', 'autumn-marathon', 'Серия скидок на популярные коллекции.', 'https://abrakadabra.fun/uploads/posts/2021-12/1639950507_1-abrakadabra-fun-p-oboi-magicheskaya-bitva-na-pk-1.jpg', '/campaigns/autumn-marathon', '-10%', NOW() - interval '20 days', NOW() + interval '20 days', TRUE, 30, NOW(), NOW()),
            ('Черная пятница', 'black-friday', 'Краткосрочная распродажа с максимальной выгодой.', 'https://vsthemes.org/uploads/posts/2021-09/1632783838_1141570-2.webp', '/campaigns/black-friday', '-30%', NOW() + interval '15 days', NOW() + interval '18 days', TRUE, 90, NOW(), NOW()),
            ('Архивная акция', 'archive-sale', 'Истекшая акция для тестов.', 'https://abrakadabra.fun/uploads/posts/2021-12/1639950507_1-abrakadabra-fun-p-oboi-magicheskaya-bitva-na-pk-1.jpg', '/campaigns/archive-sale', 'ARCHIVE', NOW() - interval '90 days', NOW() - interval '30 days', FALSE, 5, NOW(), NOW()),
            ('Зимний разогрев', 'winter-warmup', 'Подготовка к зимнему сезону: специальные условия.', 'https://abrakadabra.fun/uploads/posts/2022-03/1646387750_5-abrakadabra-fun-p-magicheskaya-bitva-zastavka-na-telefon-8.png', '/campaigns/winter-warmup', '-8%', NOW() + interval '40 days', NOW() + interval '90 days', TRUE, 22, NOW(), NOW());
    END IF;
END $$;

-- ------------------------------------------------------------
-- DISCOUNTS (если таблица существует)
-- ------------------------------------------------------------
DO $$
DECLARE
    v_has_discounts boolean := (to_regclass('public.discounts') IS NOT NULL);
    v_has_campaigns boolean := (to_regclass('public.campaigns') IS NOT NULL);
BEGIN
    IF v_has_discounts THEN
        INSERT INTO discounts (
            name,
            discount_type,
            value,
            scope,
            campaign_id,
            product_id,
            category_id,
            product_type,
            start_date,
            end_date,
            is_active,
            priority,
            created_at,
            updated_at
        )
        SELECT
            'Скидка на товар #' || p.id,
            CASE
                WHEN p.id % 4 = 0 THEN 'FIXED'::discount_type
                ELSE 'PERCENTAGE'::discount_type
            END,
            CASE
                WHEN p.id % 4 = 0 THEN (1000 + (p.id % 9) * 500)::numeric(10, 2)
                ELSE (5 + (p.id % 21))::numeric(10, 2)
            END,
            'PRODUCT'::discount_scope,
            CASE
                WHEN v_has_campaigns AND p.rn <= 100 THEN (1 + floor(random() * 10)::int)
                ELSE NULL
            END,
            p.id,
            NULL,
            NULL,
            NOW() - interval '10 days',
            NOW() + interval '60 days',
            TRUE,
            100,
            NOW(),
            NOW()
        FROM (
            SELECT
                id,
                row_number() OVER (ORDER BY id) AS rn
            FROM products
            WHERE id % 2 = 0
        ) p;
    END IF;
END $$;

COMMIT;
