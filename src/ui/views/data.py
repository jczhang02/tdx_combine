import flet as ft
from omegaconf import DictConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.ui.components.display import DataInformationDisplay


@ft.control
class UpdateDataView(ft.Container):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
        cfg: DictConfig,
    ) -> None:
        super().__init__()

        self.cfg: DictConfig = cfg
        self.async_session = async_session

        self.dataInformationDisplay = DataInformationDisplay()
        self.updateDataButton = ft.Button(
            content="更新数据",
        )

        self.content = ft.Column(
            controls=[
                self.updateDataButton,
                self.dataInformationDisplay,
            ],
        )
