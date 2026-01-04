import flet as ft
from omegaconf import DictConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.ui.components.button import UpdateDataButton
from src.ui.components.display import DataInformationDisplay


@ft.control
class UpdateDataView(ft.Container):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
        cfg: DictConfig,
    ) -> None:
        super().__init__(expand=True)

        self.cfg: DictConfig = cfg
        self.async_session = async_session

        self.dataInformationDisplay = DataInformationDisplay(
            async_session=async_session,
        )
        self.updateDataButton = UpdateDataButton(
            async_session=async_session,
            cfg=cfg,
        )
        self.content = ft.Column(
            controls=[
                self.updateDataButton,
                self.dataInformationDisplay,
            ],
            spacing=15,
            tight=False,
            alignment=ft.MainAxisAlignment.START,
        )
