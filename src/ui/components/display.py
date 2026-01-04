import os
from typing import Optional

import flet as ft
from omegaconf import DictConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import src.core.database.helpers as helpers
from src.utils.types import Status


@ft.control
class TdxPathDisplay(ft.Container):
    def __init__(self, cfg: DictConfig) -> None:
        super().__init__(
            padding=10,
            border=ft.border.all(1),
            border_radius=8,
            blur=2,
            bgcolor=ft.Colors.GREY_50,
            alignment=ft.Alignment.CENTER_LEFT,
            expand=True,
        )
        self.cfg = cfg

        self.content = ft.Text(
            size=10,
            color=ft.Colors.BLACK,
            value=self.get_path_status(),
        )

        ft.context.page.pubsub.subscribe(handler=self._handle_refresh)

    def get_path_status(self) -> str:
        cur_install_dir: Optional[str] = self.cfg["TDX_INSTALL_DIR"]
        cur_cache_dir: Optional[str] = self.cfg["TDX_CACHE_DIR"]

        text = "未设置"

        if cur_install_dir and cur_cache_dir:
            if os.path.exists(cur_cache_dir):
                text = cur_install_dir
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
class DataInformationDisplay(ft.Card):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ):
        super().__init__()

        self.expand = True
        self.async_session = async_session

        self.elevation = 2
        self.shadow_color = ft.Colors.with_opacity(0.3, ft.Colors.BLACK)

    def did_mount(self) -> None:
        ft.context.page.pubsub.subscribe(self._subscriber)
        ft.context.page.pubsub.subscribe_topic(
            topic="calc",
            handler=self._subscriber_calc,
        )
        ft.context.page.run_task(self._load_inital_status)

    async def _subscriber_calc(self, topic: str, msg: str) -> None:
        if topic == "calc":
            if msg == "start":
                ft.context.page.run_task(self.calc_start)
            if msg == "error":
                ft.context.page.run_task(self.calc_error)
            if msg == "end":
                ft.context.page.run_task(self.calc_end)

    async def calc_start(self):
        self.status["calc"] = 1
        await self._handle_refresh()

    async def calc_error(self):
        self.status["calc"] = 2
        await self._handle_refresh()

    async def calc_end(self):
        self.status["calc"] = 3
        await self._handle_refresh()

    async def _subscriber(self, msg: str) -> None:
        if msg == "data_before_update":
            ft.context.page.run_task(self.data_before_update)
        if msg == "data_updated":
            ft.context.page.run_task(self.data_updated)
        if msg == "block_inserted":
            ft.context.page.run_task(self.data_updated)

    async def block_inserted(self):
        await self._handle_refresh()

    # topic: update_data
    async def data_before_update(self):
        self.status["status"] = 2
        await self._handle_refresh()

    async def data_updated(self):
        self.status = await helpers.get_status(
            async_session=self.async_session,
        )
        await self._handle_refresh()

    async def _handle_refresh(self) -> None:
        self._build_ui()
        self.update()

    async def _load_inital_status(self):
        try:
            self.status = await helpers.get_status(
                async_session=self.async_session,
            )

        except Exception:
            self.status = Status(
                status=0,
                block_count=0,
                stock_count=0,
                update_at=None,
                calc=0,
                block_valid_count=0,
            )
        finally:
            self._build_ui()
            self.update()

    def _build_ui(self) -> None:
        status_colors = {
            0: ft.Colors.RED,
            1: ft.Colors.GREEN,
            2: ft.Colors.BLUE,
        }
        status_mean = {
            0: "错误",
            1: "就绪",
            2: "更新中",
        }
        status_row = ft.Row(
            controls=[
                ft.Text("数据状态", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Container(width=0),
                        ft.Text(
                            status_mean[self.status["status"]],
                            size=14,
                            color=status_colors.get(
                                self.status["status"], ft.Colors.BLACK54
                            ),
                        ),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        block_row = ft.Row(
            controls=[
                ft.Text("板块数量:", size=14),
                ft.Text(
                    str(self.status["block_count"]),
                    size=14,
                    text_align=ft.TextAlign.RIGHT,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        block_valid_row = ft.Row(
            controls=[
                ft.Text("有效板块数量:", size=14),
                ft.Text(
                    str(self.status["block_valid_count"]),
                    size=14,
                    text_align=ft.TextAlign.RIGHT,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        stock_row = ft.Row(
            controls=[
                ft.Text("股票数量:", size=14),
                ft.Text(
                    str(self.status["stock_count"]),
                    size=14,
                    text_align=ft.TextAlign.RIGHT,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        update_row = ft.Row(
            controls=[
                ft.Text("最后更新:", size=14),
                ft.Text(
                    "-"
                    if not self.status["update_at"]
                    else self.status["update_at"].strftime("%x %X"),
                    size=14,
                    text_align=ft.TextAlign.RIGHT,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        calc_mean = {
            0: "-",
            1: "开始",
            2: "错误",
            3: "结束",
        }
        calc_color = {
            0: ft.Colors.BLACK,
            1: ft.Colors.BLUE,
            2: ft.Colors.RED,
            3: ft.Colors.ORANGE,
        }

        calc_row = ft.Row(
            controls=[
                ft.Text("计算状态", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Container(width=0),
                        ft.Text(
                            calc_mean[self.status["calc"]],
                            size=14,
                            color=calc_color.get(
                                self.status["calc"], ft.Colors.BLACK54
                            ),
                        ),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    status_row,
                    ft.Divider(height=1, thickness=1, color=ft.Colors.BLACK12),
                    block_row,
                    block_valid_row,
                    stock_row,
                    update_row,
                    ft.Divider(height=1, thickness=1, color=ft.Colors.BLACK12),
                    calc_row,
                ],
                spacing=12,
                tight=True,
            ),
            padding=ft.padding.all(16),
            border_radius=ft.border_radius.all(8),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate_opacity=300,
        )
