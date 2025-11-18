-- SQL скрипт для создания всех таблиц базы данных проекта «Кухни Вязники»
-- Выполняйте команды в указанном порядке

-- 1. Создание ENUM типов

-- Тип роли пользователя
CREATE TYPE user_role AS ENUM ('ADMIN', 'MANAGER', 'CUSTOMER');

-- Тип категории/товара
CREATE TYPE category_type AS ENUM ('KITCHEN', 'FURNITURE');

-- Статус заявки на замер
CREATE TYPE measure_request_status AS ENUM ('NEW', 'IN_PROGRESS', 'DONE', 'CANCELLED');

-- 2. Создание таблицы users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name TEXT,
    phone TEXT,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role user_role NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- 3. Создание таблицы categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id),
    type category_type NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);

-- 4. Создание таблицы products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    price NUMERIC(10, 2),
    is_new BOOLEAN NOT NULL DEFAULT FALSE,
    is_hit BOOLEAN NOT NULL DEFAULT FALSE,
    type category_type NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_type ON products(type);

-- 5. Создание таблицы product_images
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    is_main BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_product_images_product_id ON product_images(product_id);

-- 6. Создание таблицы attributes
CREATE TABLE attributes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    unit TEXT
);

-- 7. Создание таблицы product_attributes
CREATE TABLE product_attributes (
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    attribute_id INTEGER NOT NULL REFERENCES attributes(id) ON DELETE CASCADE,
    value TEXT NOT NULL,
    PRIMARY KEY (product_id, attribute_id)
);

CREATE INDEX idx_product_attributes_product_id ON product_attributes(product_id);
CREATE INDEX idx_product_attributes_attribute_id ON product_attributes(attribute_id);

-- 8. Создание таблицы reviews
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    user_id INTEGER REFERENCES users(id),
    author_name TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_approved BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_is_approved ON reviews(is_approved);

-- 9. Создание таблицы projects
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 10. Создание таблицы project_images
CREATE TABLE project_images (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    is_main BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_project_images_project_id ON project_images(project_id);

-- 11. Создание таблицы project_products
CREATE TABLE project_products (
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    PRIMARY KEY (project_id, product_id)
);

CREATE INDEX idx_project_products_project_id ON project_products(project_id);
CREATE INDEX idx_project_products_product_id ON project_products(product_id);

-- 12. Создание таблицы measure_requests
CREATE TABLE measure_requests (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    preferred_date DATE,
    comment TEXT,
    status measure_request_status NOT NULL DEFAULT 'NEW',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measure_requests_status ON measure_requests(status);
CREATE INDEX idx_measure_requests_created_at ON measure_requests(created_at);

-- 13. Создание таблицы banners
CREATE TABLE banners (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    image_url TEXT NOT NULL,
    link_url TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_banners_position ON banners(position);
CREATE INDEX idx_banners_is_active ON banners(is_active);

