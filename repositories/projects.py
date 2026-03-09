from typing import List, Optional, Tuple
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.projects import Project
from core.schemas.projects import ProjectCreateRequest, ProjectUpdateRequest

logger = logging.getLogger(__name__)


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_projects(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Project], int]:
        """
        Получить список всех проектов с пагинацией.
        """
        logger.info("Fetching projects with pagination: page=%s, page_size=%s", page, page_size)
        offset = (page - 1) * page_size

        query = (
            select(Project)
            .order_by(Project.created_at.desc(), Project.id)
            .offset(offset)
            .limit(page_size)
        )
        count_query = select(func.count(Project.id))

        result = await self.session.execute(query)
        projects = result.scalars().all()
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        logger.info("Retrieved %d projects (total: %d)", len(projects), total)
        return projects, total

    async def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """
        Получить проект по идентификатору.
        """
        logger.info("Fetching project with id %s", project_id)
        query = select(Project).where(Project.id == project_id)
        result = await self.session.execute(query)
        project = result.scalar_one_or_none()

        if project is None:
            logger.warning("Project with id %s not found", project_id)
        return project

    async def create_project(self, request: ProjectCreateRequest) -> Project:
        """
        Создать новый проект.
        """
        logger.info("Creating project with name '%s'", request.name)
        project = Project(
            name=request.name,
            description=request.description,
            location=request.location,
        )

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)

        logger.info("Project created with id %s", project.id)
        return project

    async def update_project(
        self, project_id: int, request: ProjectUpdateRequest
    ) -> Optional[Project]:
        """
        Обновить проект по идентификатору.
        """
        logger.info("Updating project with id %s", project_id)
        project = await self.get_project_by_id(project_id)
        if project is None:
            logger.warning("Project with id %s not found for update", project_id)
            return None

        if request.name is not None:
            project.name = request.name
        if request.description is not None:
            project.description = request.description
        if request.location is not None:
            project.location = request.location

        await self.session.commit()
        await self.session.refresh(project)

        logger.info("Project with id %s successfully updated", project_id)
        return project

    async def delete_project(self, project_id: int) -> bool:
        """
        Удалить проект по идентификатору.
        """
        logger.info("Deleting project with id %s", project_id)
        project = await self.get_project_by_id(project_id)
        if project is None:
            logger.warning("Project with id %s not found for deletion", project_id)
            return False

        await self.session.delete(project)
        await self.session.commit()

        logger.info("Project with id %s successfully deleted", project_id)
        return True

