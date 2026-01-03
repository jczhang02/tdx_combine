import os
from typing import Optional

import flet as ft
from omegaconf import DictConfig


@ft.control
class TdxPathDisplay(ft.Container):
    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(
            width=500,
            height=50,
            padding=10,
            border=ft.border.all(1),
            border_radius=8,
            alignment=ft.Alignment.CENTER_LEFT,
        )
        self.cfg = cfg

        self.content = ft.Text(
            size=16,
            color=ft.Colors.BLACK,
            value=self.get_path_status(),
        )

        ft.context.page.pubsub.subscribe(handler=self._handle_refresh)

    def get_path_status(self) -> str:
        cur_install_dir: Optional[str] = self.cfg["TDX_INSTALL_DIR"]

        text = "未设置"

        if cur_install_dir:
            cur_cache_dir = os.path.join(
                cur_install_dir,
                "T0002",
                "hq_cache",
            )
            if os.path.exists(cur_cache_dir):
                text = cur_cache_dir
            else:
                text = "路径错误"

        return text

    async def _handle_refresh(self, msg: str) -> None:
        if msg == "path_refresh":
            self.text = self.get_path_status()
            self.content = ft.Text(
                size=16,
                color=ft.Colors.BLACK,
                value=self.text,
            )
            await self.update()


@ft.control
class DataInformationDisplay(ft.Container):
    def __init__(self) -> None:
        super().__init__()

        self.updateProgressRing = ft.ProgressRing(
            value=0.3,
            padding=ft.Padding.all(10),
        )

        self.updateDataStatus = ft.Text(
            spans=[
                ft.TextSpan(
                    text="最后更新时间：2025/12/31 05:36:28",
                    style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                ),
            ]
        )

        self.informationText = ft.Text("已读取板块数量: 1000")

        self.content = ft.Container(
            border=ft.Border.all(2, ft.Colors.BLACK_45),
            border_radius=ft.border_radius.all(30),
            content=ft.Column(
                width=500,
                height=120,
                spacing=12,
                controls=[
                    ft.Row(
                        controls=[
                            self.updateProgressRing,
                            self.updateDataStatus,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            self.informationText,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
