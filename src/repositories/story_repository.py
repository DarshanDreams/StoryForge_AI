from datetime import datetime

from sqlalchemy import DateTime, Text, String, select
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.models import StoryRecord
from src.repositories.database import Base


class StoryORM(Base):

    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    summary: Mapped[str] = mapped_column(
        Text
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class StoryRepository:

    def __init__(
        self,
        session_factory,
    ):
        self.session_factory = session_factory

    def create(
        self,
        title: str,
        summary: str,
        content: str,
    ) -> StoryRecord:

        with self.session_factory() as session:

            story = StoryORM(
                title=title,
                summary=summary,
                content=content,
            )

            session.add(story)
            session.commit()
            session.refresh(story)

            return self._to_model(
                story
            )

    def list_all(
        self,
    ) -> list[StoryRecord]:

        with self.session_factory() as session:

            result = session.execute(
                select(StoryORM)
                .order_by(
                    StoryORM.created_at.desc()
                )
            )

            return [
                self._to_model(row)
                for row in result.scalars()
            ]

    @staticmethod
    def _to_model(
        story: StoryORM,
    ) -> StoryRecord:

        return StoryRecord(
            id=story.id,
            title=story.title,
            summary=story.summary,
            content=story.content,
            created_at=story.created_at,
        )