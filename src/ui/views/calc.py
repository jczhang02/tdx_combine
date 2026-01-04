import flet as ft
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.ui.components.button import CalcButton, ExportResultButton


@ft.control
class CalcView(ft.Container):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ):
        super().__init__()
        self.calcButton = CalcButton(async_session=async_session)
        self.exportResultButton = ExportResultButton(
            async_session=async_session
        )
        self.content = ft.Row(
            controls=[
                self.calcButton,
                self.exportResultButton,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        )
