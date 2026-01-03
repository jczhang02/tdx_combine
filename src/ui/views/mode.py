import flet as ft
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.ui.components.button import AddBlockButton, ImportModeFileButton
from src.ui.components.datatable import ModeDataTable
from src.ui.components.dropdown import BlocksDropdown


@ft.control
class ModeView(ft.Container):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__()
        self.importModeFileButton = ImportModeFileButton(
            async_session=async_session,
        )
        self.modeDataTable = ModeDataTable(
            async_session=async_session,
        )
        self.blocksDropdown = BlocksDropdown(
            async_session=async_session,
        )
        self.addBlockButton = AddBlockButton(
            async_session=async_session,
            dropdown_ref=self.blocksDropdown,
        )

        self.content = ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                self.importModeFileButton,
                                self.blocksDropdown,
                                self.addBlockButton,
                            ]
                        ),
                        self.modeDataTable,
                    ]
                )
            ]
        )
