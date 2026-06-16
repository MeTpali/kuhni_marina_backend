from typing import Dict, List, Optional
import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.project_images import ProjectImage
from core.schemas.project_images import ProjectImageCreateRequest

logger = logging.getLogger(__name__)


class ProjectImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_project_images(self) -> List[ProjectImage]:
        """
        Получить список всех изображений проектов.
        """
        logger.info("Fetching all project images")
        query = select(ProjectImage).order_by(ProjectImage.project_id, ProjectImage.id)
        result = await self.session.execute(query)
        project_images = result.scalars().all()
        logger.info("Retrieved %d project images", len(project_images))
        return project_images

    async def get_project_image_by_id(self, project_image_id: int) -> Optional[ProjectImage]:
        """
        Получить изображение проекта по идентификатору.
        """
        logger.info("Fetching project image with id %s", project_image_id)
        query = select(ProjectImage).where(ProjectImage.id == project_image_id)
        result = await self.session.execute(query)
        project_image = result.scalar_one_or_none()

        if project_image is None:
            logger.warning("Project image with id %s not found", project_image_id)
        return project_image

    async def ensure_single_main_for_project(self, project_id: int, main_image_id: int) -> None:
        """
        Сделать главным только одно изображение проекта; у остальных сбросить is_main.
        """
        await self.session.execute(
            update(ProjectImage).where(ProjectImage.project_id == project_id).values(is_main=False)
        )
        await self.session.execute(
            update(ProjectImage).where(ProjectImage.id == main_image_id).values(is_main=True)
        )
        await self.session.commit()

    async def delete_all_by_project_id(self, project_id: int) -> None:
        """Удалить все изображения проекта."""
        await self.session.execute(delete(ProjectImage).where(ProjectImage.project_id == project_id))
        await self.session.commit()

    async def set_project_images(
        self, project_id: int, image_urls: List[str], main_index: Optional[int] = None
    ) -> List[ProjectImage]:
        """
        Заменить изображения проекта на новый список.
        main_index — порядковый номер (1-based). Если не задан или некорректен — главным первое.
        """
        await self.delete_all_by_project_id(project_id)
        urls_clean = [(u or "").strip() for u in image_urls if (u or "").strip()]
        if not urls_clean:
            return []
        n = len(urls_clean)
        effective = main_index if (main_index is not None and 1 <= main_index <= n) else 1
        main_zero = effective - 1
        created = []
        for i, url in enumerate(urls_clean):
            img = ProjectImage(
                project_id=project_id,
                image_url=url,
                is_main=(i == main_zero),
            )
            self.session.add(img)
            created.append(img)
        await self.session.commit()
        for img in created:
            await self.session.refresh(img)
        if len(created) > 1:
            main_id = created[main_zero].id
            await self.ensure_single_main_for_project(project_id, main_id)
        return created

    async def add_project_images(
        self, project_id: int, image_urls: List[str], main_index: Optional[int] = None
    ) -> List[ProjectImage]:
        """
        Добавить изображения к проекту (не удаляя существующие).
        main_index — порядковый номер среди новых (1-based); если задан, это новое изображение станет главным.
        """
        urls_clean = [(u or "").strip() for u in image_urls if (u or "").strip()]
        if not urls_clean:
            return []
        existing = await self.get_project_images_by_project_id(project_id)
        n = len(urls_clean)
        effective = main_index if (main_index is not None and 1 <= main_index <= n) else None
        main_zero = (effective - 1) if effective else None
        created = []
        for i, url in enumerate(urls_clean):
            is_main = False
            if len(existing) == 0 and i == 0:
                is_main = True
            elif main_zero is not None and i == main_zero:
                is_main = True
            img = ProjectImage(
                project_id=project_id,
                image_url=url,
                is_main=is_main,
            )
            self.session.add(img)
            created.append(img)
        await self.session.commit()
        for img in created:
            await self.session.refresh(img)
        if any(img.is_main for img in created):
            main_id = next(img.id for img in created if img.is_main)
            await self.ensure_single_main_for_project(project_id, main_id)
        return created

    async def get_primary_image_urls_by_project_ids(
        self, project_ids: List[int]
    ) -> Dict[int, str]:
        """
        Получить URL главного изображения для каждого проекта.
        Если главного нет — возвращается первое изображение по id.
        """
        if not project_ids:
            return {}

        logger.info("Fetching primary project images for %d projects", len(project_ids))
        query = (
            select(ProjectImage)
            .where(ProjectImage.project_id.in_(project_ids))
            .order_by(
                ProjectImage.project_id,
                ProjectImage.is_main.desc(),
                ProjectImage.id,
            )
        )
        result = await self.session.execute(query)
        project_images = result.scalars().all()

        urls: Dict[int, str] = {}
        for project_image in project_images:
            if project_image.project_id not in urls:
                urls[project_image.project_id] = project_image.image_url

        logger.info("Resolved primary images for %d projects", len(urls))
        return urls

    async def get_project_images_by_project_id(self, project_id: int) -> List[ProjectImage]:
        """
        Получить список изображений проекта по идентификатору проекта.
        """
        logger.info("Fetching project images for project_id %s", project_id)
        query = select(ProjectImage).where(ProjectImage.project_id == project_id).order_by(ProjectImage.id)
        result = await self.session.execute(query)
        project_images = result.scalars().all()
        logger.info("Retrieved %d project images for project_id %s", len(project_images), project_id)
        return project_images

    async def create_project_image(self, request: ProjectImageCreateRequest) -> ProjectImage:
        """
        Создать новое изображение проекта.
        Гарантирует, что только одно изображение проекта имеет is_main=True:
        - если у проекта ещё нет изображений — новое делаем главным;
        - если у нового is_main=True — у остальных изображений проекта сбрасываем is_main.
        """
        logger.info("Creating project image for project_id %s", request.project_id)
        existing = await self.get_project_images_by_project_id(request.project_id)
        is_main = request.is_main if request.is_main is not None else False
        if len(existing) == 0:
            is_main = True

        project_image = ProjectImage(
            project_id=request.project_id,
            image_url=request.image_url,
            is_main=is_main,
        )

        self.session.add(project_image)
        await self.session.commit()
        await self.session.refresh(project_image)

        if is_main and existing:
            await self.ensure_single_main_for_project(request.project_id, project_image.id)

        logger.info("Project image created with id %s", project_image.id)
        return project_image

    async def create_multiple_project_images(
        self, requests: List[ProjectImageCreateRequest]
    ) -> List[ProjectImage]:
        """
        Создать несколько изображений проекта.
        Гарантирует одно главное изображение: если у проекта не было изображений — первое
        делаем главным; иначе главным считается первое с is_main=True, у остальных сбрасываем.
        """
        if not requests:
            return []
        project_id = requests[0].project_id
        existing = await self.get_project_images_by_project_id(project_id)
        first_main_index = next(
            (i for i, r in enumerate(requests) if r.is_main),
            None,
        )
        if len(existing) == 0 and first_main_index is None:
            first_main_index = 0

        project_images = []
        main_created_id: Optional[int] = None
        for i, request in enumerate(requests):
            is_main = (
                (len(existing) == 0 and i == 0)
                or (first_main_index is not None and i == first_main_index)
            )
            project_image = ProjectImage(
                project_id=request.project_id,
                image_url=request.image_url,
                is_main=is_main,
            )
            project_images.append(project_image)
            self.session.add(project_image)

        await self.session.commit()
        for project_image in project_images:
            await self.session.refresh(project_image)
            if project_image.is_main:
                main_created_id = project_image.id
                break

        if main_created_id is not None and (existing or len(project_images) > 1):
            await self.ensure_single_main_for_project(project_id, main_created_id)

        logger.info("Successfully created %d project images", len(project_images))
        return project_images

    async def delete_project_image(self, project_image_id: int) -> bool:
        """
        Удалить изображение проекта по идентификатору.
        Если удаляется главное изображение (is_main=True), главным делается первое из оставшихся.
        """
        logger.info("Deleting project image with id %s", project_image_id)
        project_image = await self.get_project_image_by_id(project_image_id)
        if project_image is None:
            logger.warning("Project image with id %s not found for deletion", project_image_id)
            return False

        project_id = project_image.project_id
        was_main = project_image.is_main

        await self.session.delete(project_image)
        await self.session.commit()

        if was_main:
            remaining = await self.get_project_images_by_project_id(project_id)
            if remaining:
                await self.ensure_single_main_for_project(project_id, remaining[0].id)

        logger.info("Project image with id %s successfully deleted", project_image_id)
        return True

