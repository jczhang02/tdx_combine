import flet as ft
from omegaconf import DictConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.ui.views import (
    CalcView,
    CustomBlockView,
    ModeView,
    TdxPathView,
    UpdateDataView,
)


@ft.control
class App(ft.Container):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
        cfg: DictConfig,
    ) -> None:
        super().__init__()
        self.expand = True
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20

        self.tdxPathView = TdxPathView(cfg=cfg)
        self.custom_block = CustomBlockView(async_session=async_session)
        self.update_data = UpdateDataView(
            async_session=async_session,
            cfg=cfg,
        )
        self.mode = ModeView(async_session=async_session)
        self.calc = CalcView(async_session=async_session)
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                self.tdxPathView,
                                self.custom_block,
                                self.update_data,
                            ],
                            expand=1,
                            spacing=10,
                        ),
                        ft.Column(
                            controls=[
                                self.mode,
                                self.calc,
                            ],
                            expand=3,
                            spacing=10,
                        ),
                    ],
                    expand=True,
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            expand=True,
        )
