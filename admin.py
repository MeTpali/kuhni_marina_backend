from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.db_helper import db_helper
from core.config import settings
from core.models.categories import Category, CategoryType
from core.models.products import Product, ProductType
from core.models.attributes import Attribute
from core.models.product_images import ProductImage
from core.models.product_attributes import ProductAttribute
from core.models.reviews import Review
from core.models.projects import Project
from core.models.project_images import ProjectImage
from core.models.project_products import ProjectProduct
from core.models.banners import Banner
from core.models.measure_requests import MeasureRequest, MeasureRequestStatus
from core.models.discounts import Discount, DiscountType, DiscountScope
from core.utils.slug import generate_unique_slug


# ==================== Аутентификация ====================
class AdminAuth(AuthenticationBackend):
    """
    Класс аутентификации для админ-панели.
    Проверяет логин и пароль из переменных окружения.
    """
    async def login(self, request: Request) -> bool:
        """
        Обработка входа в админ-панель.
        """
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        # Проверяем учетные данные
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            # Сохраняем сессию
            request.session.update({"authenticated": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        """
        Обработка выхода из админ-панели.
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        Проверка аутентификации для защищенных страниц.
        """
        return request.session.get("authenticated", False)


# ==================== Категории ====================
class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-folder"
    column_list = [Category.id, Category.name, Category.slug, Category.type, Category.parent_id, Category.is_active, Category.created_at]
    column_details_list = [Category.id, Category.name, Category.slug, Category.type, Category.parent_id, Category.is_active, Category.created_at]
    column_searchable_list = [Category.name, Category.slug]
    column_sortable_list = [Category.id, Category.name, Category.created_at]
    column_labels = {
        Category.id: "ID",
        Category.name: "Название",
        Category.slug: "Slug",
        Category.type: "Тип",
        Category.parent_id: "Родительская категория",
        Category.is_active: "Активна",
        Category.created_at: "Дата создания",
    }
    form_columns = [Category.name, Category.slug, Category.type, Category.parent, Category.is_active]
    form_ajax_refs = {
        "parent": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }
    form_args = {
        "type": {
            "choices": [(cat_type.value, cat_type.name) for cat_type in CategoryType],
        }
    }


# ==================== Продукты ====================
class ProductAdmin(ModelView, model=Product):
    name = "Продукт"
    name_plural = "Продукты"
    icon = "fa-solid fa-box"
    column_list = [Product.id, Product.name, Product.slug, Product.category_id, Product.price, Product.type, Product.is_active, Product.created_at]
    column_details_list = [Product.id, Product.name, Product.slug, Product.category_id, Product.description, Product.price, Product.is_new, Product.is_hit, Product.type, Product.is_active, Product.created_at, Product.updated_at, Product.discounts]
    column_searchable_list = [Product.name, Product.slug, Product.description]
    column_sortable_list = [Product.id, Product.name, Product.price, Product.created_at]
    column_labels = {
        Product.id: "ID",
        Product.name: "Название",
        Product.slug: "Slug",
        Product.category_id: "Категория",
        Product.description: "Описание",
        Product.price: "Цена",
        Product.is_new: "Новинка",
        Product.is_hit: "Хит продаж",
        Product.type: "Тип",
        Product.is_active: "Активен",
        Product.created_at: "Дата создания",
        Product.updated_at: "Дата обновления",
        Product.discounts: "Скидки",
    }
    form_columns = [Product.name, Product.category, Product.description, Product.price, Product.is_new, Product.is_hit, Product.type, Product.is_active]
    form_ajax_refs = {
        "category": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }
    form_args = {
        "type": {
            "choices": [(prod_type.value, prod_type.name) for prod_type in ProductType],
        }
    }

    async def insert_model(self, request: Request, data: dict) -> Product:
        """
        Переопределяем метод создания продукта для автоматической генерации slug.
        """
        # Если slug не указан или пустой, генерируем его из названия
        if not data.get("slug") or not str(data.get("slug")).strip():
            name = data.get("name", "")
            if name:
                # Получаем сессию через engine для проверки уникальности slug
                async with AsyncSession(bind=db_helper.engine) as session:
                    from sqlalchemy import text
                    await session.execute(text("SET search_path TO kuhni_marina, public"))
                    slug = await generate_unique_slug(session, Product, name)
                    data["slug"] = slug
        
        # Вызываем родительский метод для создания
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: int, data: dict) -> Product:
        """
        Переопределяем метод обновления продукта для автоматической генерации slug при изменении названия.
        """
        # Получаем текущий продукт и генерируем slug через сессию
        async with AsyncSession(bind=db_helper.engine) as session:
            from sqlalchemy import select, text
            await session.execute(text("SET search_path TO kuhni_marina, public"))
            result = await session.execute(select(Product).where(Product.id == pk))
            current_product = result.scalar_one_or_none()
            
            if current_product:
                # Если изменилось название, но slug не указан, генерируем новый slug
                if "name" in data and data["name"] != current_product.name:
                    if "slug" not in data or not data.get("slug") or not str(data.get("slug")).strip():
                        slug = await generate_unique_slug(session, Product, data["name"], exclude_id=pk)
                        data["slug"] = slug
                # Если slug указан явно, проверяем его уникальность
                elif "slug" in data and data.get("slug"):
                    slug = await generate_unique_slug(session, Product, data["slug"], exclude_id=pk)
                    data["slug"] = slug
        
        # Вызываем родительский метод для обновления
        return await super().update_model(request, pk, data)


# ==================== Атрибуты ====================
class AttributeAdmin(ModelView, model=Attribute):
    name = "Атрибут"
    name_plural = "Атрибуты"
    icon = "fa-solid fa-tag"
    column_list = [Attribute.id, Attribute.name, Attribute.unit]
    column_details_list = [Attribute.id, Attribute.name, Attribute.unit]
    column_searchable_list = [Attribute.name]
    column_sortable_list = [Attribute.id, Attribute.name]
    column_labels = {
        Attribute.id: "ID",
        Attribute.name: "Название",
        Attribute.unit: "Единица измерения",
    }
    form_columns = [Attribute.name, Attribute.unit]


# ==================== Изображения продуктов ====================
class ProductImageAdmin(ModelView, model=ProductImage):
    name = "Изображение продукта"
    name_plural = "Изображения продуктов"
    icon = "fa-solid fa-image"
    column_list = [ProductImage.id, ProductImage.product_id, ProductImage.image_url, ProductImage.is_main]
    column_details_list = [ProductImage.id, ProductImage.product_id, ProductImage.image_url, ProductImage.is_main]
    column_searchable_list = [ProductImage.image_url]
    column_sortable_list = [ProductImage.id, ProductImage.product_id]
    column_labels = {
        ProductImage.id: "ID",
        ProductImage.product_id: "Продукт",
        ProductImage.image_url: "URL изображения",
        ProductImage.is_main: "Главное",
    }
    form_columns = [ProductImage.product, ProductImage.image_url, ProductImage.is_main]
    form_ajax_refs = {
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }


# ==================== Атрибуты продуктов ====================
class ProductAttributeAdmin(ModelView, model=ProductAttribute):
    name = "Атрибут продукта"
    name_plural = "Атрибуты продуктов"
    icon = "fa-solid fa-list"
    column_list = [ProductAttribute.product_id, ProductAttribute.attribute_id, ProductAttribute.value]
    column_details_list = [ProductAttribute.product_id, ProductAttribute.attribute_id, ProductAttribute.value]
    column_searchable_list = [ProductAttribute.value]
    column_sortable_list = [ProductAttribute.product_id, ProductAttribute.attribute_id]
    column_labels = {
        ProductAttribute.product_id: "Продукт",
        ProductAttribute.attribute_id: "Атрибут",
        ProductAttribute.value: "Значение",
    }
    form_columns = [ProductAttribute.product, ProductAttribute.attribute, ProductAttribute.value]
    form_ajax_refs = {
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "attribute": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }


# ==================== Отзывы ====================
class ReviewAdmin(ModelView, model=Review):
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-star"
    column_list = [Review.id, Review.author_name, Review.rating, Review.product_id, Review.is_approved, Review.created_at]
    column_details_list = [Review.id, Review.author_name, Review.rating, Review.text, Review.product_id, Review.is_approved, Review.created_at]
    column_searchable_list = [Review.author_name, Review.text]
    column_sortable_list = [Review.id, Review.rating, Review.created_at]
    column_labels = {
        Review.id: "ID",
        Review.author_name: "Имя автора",
        Review.rating: "Оценка",
        Review.text: "Текст",
        Review.product_id: "Продукт",
        Review.is_approved: "Одобрен",
        Review.created_at: "Дата создания",
    }
    form_columns = [Review.author_name, Review.rating, Review.text, Review.product, Review.is_approved]
    form_ajax_refs = {
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "user": {
            "fields": ("full_name", "id"),
            "order_by": "full_name",
        }
    }


# ==================== Проекты ====================
class ProjectAdmin(ModelView, model=Project):
    name = "Проект"
    name_plural = "Проекты"
    icon = "fa-solid fa-folder-open"
    column_list = [Project.id, Project.name, Project.location, Project.created_at]
    column_details_list = [Project.id, Project.name, Project.description, Project.location, Project.created_at]
    column_searchable_list = [Project.name, Project.description, Project.location]
    column_sortable_list = [Project.id, Project.name, Project.created_at]
    column_labels = {
        Project.id: "ID",
        Project.name: "Название",
        Project.description: "Описание",
        Project.location: "Местоположение",
        Project.created_at: "Дата создания",
    }
    form_columns = [Project.name, Project.description, Project.location]


# ==================== Изображения проектов ====================
class ProjectImageAdmin(ModelView, model=ProjectImage):
    name = "Изображение проекта"
    name_plural = "Изображения проектов"
    icon = "fa-solid fa-images"
    column_list = [ProjectImage.id, ProjectImage.project_id, ProjectImage.image_url, ProjectImage.is_main]
    column_details_list = [ProjectImage.id, ProjectImage.project_id, ProjectImage.image_url, ProjectImage.is_main]
    column_searchable_list = [ProjectImage.image_url]
    column_sortable_list = [ProjectImage.id, ProjectImage.project_id]
    column_labels = {
        ProjectImage.id: "ID",
        ProjectImage.project_id: "Проект",
        ProjectImage.image_url: "URL изображения",
        ProjectImage.is_main: "Главное",
    }
    form_columns = [ProjectImage.project, ProjectImage.image_url, ProjectImage.is_main]
    form_ajax_refs = {
        "project": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }


# ==================== Продукты в проектах ====================
class ProjectProductAdmin(ModelView, model=ProjectProduct):
    name = "Продукт в проекте"
    name_plural = "Продукты в проектах"
    icon = "fa-solid fa-link"
    column_list = [ProjectProduct.project_id, ProjectProduct.product_id]
    column_details_list = [ProjectProduct.project_id, ProjectProduct.product_id]
    column_sortable_list = [ProjectProduct.project_id, ProjectProduct.product_id]
    column_labels = {
        ProjectProduct.project_id: "Проект",
        ProjectProduct.product_id: "Продукт",
    }
    form_columns = [ProjectProduct.project, ProjectProduct.product]
    form_ajax_refs = {
        "project": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }


# ==================== Баннеры ====================
class BannerAdmin(ModelView, model=Banner):
    name = "Баннер"
    name_plural = "Баннеры"
    icon = "fa-solid fa-image"
    column_list = [Banner.id, Banner.title, Banner.position, Banner.is_active]
    column_details_list = [Banner.id, Banner.title, Banner.image_url, Banner.link_url, Banner.position, Banner.is_active]
    column_searchable_list = [Banner.title]
    column_sortable_list = [Banner.id, Banner.position]
    column_labels = {
        Banner.id: "ID",
        Banner.title: "Заголовок",
        Banner.image_url: "URL изображения",
        Banner.link_url: "URL ссылки",
        Banner.position: "Позиция",
        Banner.is_active: "Активен",
    }
    form_columns = [Banner.title, Banner.image_url, Banner.link_url, Banner.position, Banner.is_active]


# ==================== Скидки ====================
class DiscountAdmin(ModelView, model=Discount):
    name = "Скидка"
    name_plural = "Скидки"
    icon = "fa-solid fa-percent"
    column_list = [Discount.id, Discount.name, Discount.discount_type, Discount.value, Discount.scope, Discount.is_active, Discount.start_date, Discount.end_date, Discount.priority]
    column_details_list = [Discount.id, Discount.name, Discount.discount_type, Discount.value, Discount.scope, Discount.product_id, Discount.category_id, Discount.product_type, Discount.start_date, Discount.end_date, Discount.is_active, Discount.priority, Discount.created_at, Discount.updated_at]
    column_searchable_list = [Discount.name]
    column_sortable_list = [Discount.id, Discount.name, Discount.priority, Discount.start_date, Discount.end_date, Discount.created_at]
    column_labels = {
        Discount.id: "ID",
        Discount.name: "Название",
        Discount.discount_type: "Тип скидки",
        Discount.value: "Значение",
        Discount.scope: "Область применения",
        Discount.product_id: "Продукт",
        Discount.category_id: "Категория",
        Discount.product_type: "Тип продукта",
        Discount.start_date: "Дата начала",
        Discount.end_date: "Дата окончания",
        Discount.is_active: "Активна",
        Discount.priority: "Приоритет",
        Discount.created_at: "Дата создания",
        Discount.updated_at: "Дата обновления",
    }
    form_columns = [Discount.name, Discount.discount_type, Discount.value, Discount.scope, Discount.product, Discount.category, Discount.product_type, Discount.start_date, Discount.end_date, Discount.is_active, Discount.priority]
    form_ajax_refs = {
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "category": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }
    form_args = {
        "discount_type": {
            "choices": [(disc_type.value, disc_type.name) for disc_type in DiscountType],
        },
        "scope": {
            "choices": [(scope.value, scope.name) for scope in DiscountScope],
        },
        "product_type": {
            "choices": [(prod_type.value, prod_type.name) for prod_type in ProductType],
        }
    }


# ==================== Заявки на замер ====================
class MeasureRequestAdmin(ModelView, model=MeasureRequest):
    name = "Заявка на замер"
    name_plural = "Заявки на замер"
    icon = "fa-solid fa-ruler"
    column_list = [MeasureRequest.id, MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.status, MeasureRequest.created_at]
    column_details_list = [MeasureRequest.id, MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.address, MeasureRequest.preferred_date, MeasureRequest.comment, MeasureRequest.status, MeasureRequest.created_at]
    column_searchable_list = [MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.address]
    column_sortable_list = [MeasureRequest.id, MeasureRequest.status, MeasureRequest.created_at]
    column_labels = {
        MeasureRequest.id: "ID",
        MeasureRequest.full_name: "Имя клиента",
        MeasureRequest.phone: "Телефон",
        MeasureRequest.address: "Адрес",
        MeasureRequest.preferred_date: "Предпочтительная дата",
        MeasureRequest.comment: "Комментарий",
        MeasureRequest.status: "Статус",
        MeasureRequest.created_at: "Дата создания",
    }
    form_columns = [MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.address, MeasureRequest.preferred_date, MeasureRequest.comment, MeasureRequest.status]
    form_args = {
        "status": {
            "choices": [(status.value, status.name) for status in MeasureRequestStatus],
        }
    }


def setup_admin(app: FastAPI):
    """
    Настройка SQLAdmin для приложения.
    """
    # Создаем экземпляр аутентификации
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    
    admin = Admin(
        app,
        engine=db_helper.engine,
        title="Админ-панель - Кухни Вязники",
        base_url="/admin",
        authentication_backend=authentication_backend,
    )

    # Регистрируем все модели
    admin.add_view(CategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(AttributeAdmin)
    admin.add_view(ProductImageAdmin)
    admin.add_view(ProductAttributeAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(ProjectImageAdmin)
    admin.add_view(ProjectProductAdmin)
    admin.add_view(BannerAdmin)
    admin.add_view(DiscountAdmin)
    admin.add_view(MeasureRequestAdmin)

    return admin
