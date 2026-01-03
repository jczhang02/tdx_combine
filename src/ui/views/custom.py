import flet as ft
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.ui.components.dropdown import BlocksDropdown


@ft.control
class CustomBlockView(ft.Container):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__()
        self.blocksDropdown = BlocksDropdown(async_session=async_session)
        self.importBlockDataButton = ft.Button(content="导入")

        self.content = ft.Row(
            controls=[
                self.blocksDropdown,
                self.importBlockDataButton,
            ]
        )
