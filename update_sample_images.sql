-- Обновление тестовых данных:
-- - случайные изображения для баннеров, product_images, project_images и акций;
-- - каждый 10-й продукт помечается как мебель (FURNITURE).
--
-- Запуск: psql -d <db_name> -f update_sample_images.sql
--
-- Примечание: у продуктов изображения хранятся в таблице product_images,
-- а не в products.

BEGIN;

-- Общий массив URL (18 изображений категорий)
-- Используется в UPDATE через random() для каждой строки отдельно.

-- 1. Баннеры
UPDATE banners
SET image_url = (
    ARRAY[
        'https://storage.yandexcloud.net/kuhni-storage/categories/d3d60a7848894da19867a7351a6d40d5.png',
        'https://storage.yandexcloud.net/kuhni-storage/categories/c217fda240594906bbd4f3315e2db7a6.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/2d1fa55e338c49219d1525247885ecce.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/4e643214a7a14712a88a759ac6650c94.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/79d31490ba864068b6f15baeba39fcbd.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/82249ff610ed46a6ab4a0fdf4c9d6be3.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/a83d95ab998a4275b82e01fc25c7ef49.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/e6c0eb5fe0da453bb29c05a57f90a1f9.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/965dfe7a029c4d09a8a77d953a40c5b3.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/becc0c122eb94ea9aa1611002a44bb26.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/6a0946fc289d47a1944489693a40a1d4.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/bbfe578b43a84f2ba21ae4ac75758879.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/06431b727ce14bfc8ce20bff5ea54352.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/fd97b131b6b748cc887738bde9489675.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/b3b618f0c39d4b9cad8b6fd33adda82d.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/48b44748b8da4aab9968cca3820eb98e.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/3148cfefe27c4fb89eed495d7e32f5aa.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/e9b57853dfea46568718744211360b38.webp'
    ]
)[1 + floor(random() * 18)::int]
WHERE image_url IS NOT NULL;

-- 2. Изображения продуктов
UPDATE product_images
SET image_url = (
    ARRAY[
        'https://storage.yandexcloud.net/kuhni-storage/categories/d3d60a7848894da19867a7351a6d40d5.png',
        'https://storage.yandexcloud.net/kuhni-storage/categories/c217fda240594906bbd4f3315e2db7a6.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/2d1fa55e338c49219d1525247885ecce.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/4e643214a7a14712a88a759ac6650c94.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/79d31490ba864068b6f15baeba39fcbd.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/82249ff610ed46a6ab4a0fdf4c9d6be3.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/a83d95ab998a4275b82e01fc25c7ef49.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/e6c0eb5fe0da453bb29c05a57f90a1f9.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/965dfe7a029c4d09a8a77d953a40c5b3.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/becc0c122eb94ea9aa1611002a44bb26.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/6a0946fc289d47a1944489693a40a1d4.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/bbfe578b43a84f2ba21ae4ac75758879.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/06431b727ce14bfc8ce20bff5ea54352.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/fd97b131b6b748cc887738bde9489675.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/b3b618f0c39d4b9cad8b6fd33adda82d.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/48b44748b8da4aab9968cca3820eb98e.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/3148cfefe27c4fb89eed495d7e32f5aa.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/e9b57853dfea46568718744211360b38.webp'
    ]
)[1 + floor(random() * 18)::int]
WHERE image_url IS NOT NULL;

-- 3. Акции (campaigns)
UPDATE campaigns
SET banner_image_url = (
    ARRAY[
        'https://storage.yandexcloud.net/kuhni-storage/categories/d3d60a7848894da19867a7351a6d40d5.png',
        'https://storage.yandexcloud.net/kuhni-storage/categories/c217fda240594906bbd4f3315e2db7a6.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/2d1fa55e338c49219d1525247885ecce.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/4e643214a7a14712a88a759ac6650c94.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/79d31490ba864068b6f15baeba39fcbd.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/82249ff610ed46a6ab4a0fdf4c9d6be3.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/a83d95ab998a4275b82e01fc25c7ef49.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/e6c0eb5fe0da453bb29c05a57f90a1f9.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/965dfe7a029c4d09a8a77d953a40c5b3.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/becc0c122eb94ea9aa1611002a44bb26.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/6a0946fc289d47a1944489693a40a1d4.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/bbfe578b43a84f2ba21ae4ac75758879.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/06431b727ce14bfc8ce20bff5ea54352.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/fd97b131b6b748cc887738bde9489675.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/b3b618f0c39d4b9cad8b6fd33adda82d.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/48b44748b8da4aab9968cca3820eb98e.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/3148cfefe27c4fb89eed495d7e32f5aa.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/e9b57853dfea46568718744211360b38.webp'
    ]
)[1 + floor(random() * 18)::int]
WHERE banner_image_url IS NOT NULL;

-- 4. Изображения проектов
UPDATE project_images
SET image_url = (
    ARRAY[
        'https://storage.yandexcloud.net/kuhni-storage/categories/d3d60a7848894da19867a7351a6d40d5.png',
        'https://storage.yandexcloud.net/kuhni-storage/categories/c217fda240594906bbd4f3315e2db7a6.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/2d1fa55e338c49219d1525247885ecce.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/4e643214a7a14712a88a759ac6650c94.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/79d31490ba864068b6f15baeba39fcbd.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/82249ff610ed46a6ab4a0fdf4c9d6be3.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/a83d95ab998a4275b82e01fc25c7ef49.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/e6c0eb5fe0da453bb29c05a57f90a1f9.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/965dfe7a029c4d09a8a77d953a40c5b3.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/becc0c122eb94ea9aa1611002a44bb26.jpg',
        'https://storage.yandexcloud.net/kuhni-storage/categories/6a0946fc289d47a1944489693a40a1d4.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/bbfe578b43a84f2ba21ae4ac75758879.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/06431b727ce14bfc8ce20bff5ea54352.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/fd97b131b6b748cc887738bde9489675.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/b3b618f0c39d4b9cad8b6fd33adda82d.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/48b44748b8da4aab9968cca3820eb98e.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/3148cfefe27c4fb89eed495d7e32f5aa.webp',
        'https://storage.yandexcloud.net/kuhni-storage/categories/e9b57853dfea46568718744211360b38.webp'
    ]
)[1 + floor(random() * 18)::int]
WHERE image_url IS NOT NULL;

-- 5. Каждый 10-й продукт — мебель (id: 10, 20, 30, ...)
UPDATE products
SET type = 'FURNITURE'::category_type,
    updated_at = CURRENT_TIMESTAMP
WHERE id % 10 = 0;

COMMIT;
