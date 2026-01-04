import flet as ft
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database import Block


@ft.control
class BlocksDropdown(ft.Dropdown):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(
            editable=True,
            label="板块信息",
            menu_height=200,
            expand=False,
            width=240,
            enable_filter=False,
            enable_search=True,
            text_align=ft.TextAlign.CENTER,
            on_text_change=self.build_options,
        )
        self.async_session = async_session

    async def build_options(self, __e__: ft.Event[ft.Dropdown]):
        query = __e__.control.text
        async with self.async_session() as session:
            if query:
                stmt = (
                    select(Block.code, Block.name)
                    .where(Block.code.like(f"%{query}%"))
                    .limit(20)
                )
                result = await session.execute(stmt)
                matching = result.all()
                self.options = [
                    ft.DropdownOption(
                        key=code,
                        content=ft.Text(
                            spans=[
                                ft.TextSpan(
                                    text=f"{code}",
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.UNDERLINE
                                    ),
                                ),
                                ft.TextSpan(text=" "),
                                ft.TextSpan(text=f"{name}"),
                            ]
                        ),
                    )
                    for (code, name) in matching
                ]
            else:
                self.options = []
