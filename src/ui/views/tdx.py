import flet as ft
from omegaconf import DictConfig

from src.ui.components.button import TdxPathButton
from src.ui.components.display import TdxPathDisplay


@ft.control
class TdxPathView(ft.Container):
    def __init__(
        self,
        cfg: DictConfig,
    ):
        super().__init__()
        self.cfg: DictConfig = cfg
        self.tdxPathDisplay = TdxPathDisplay(
            cfg=cfg,
        )
        self.tdxPathButton = TdxPathButton(cfg=cfg)

        self.content = ft.Row(
            controls=[
                self.tdxPathDisplay,
                self.tdxPathButton,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        )
