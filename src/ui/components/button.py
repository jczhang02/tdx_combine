from typing import List, Optional, cast

import flet as ft
from omegaconf import DictConfig, OmegaConf
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core import (
    export_combinations,
    get_combination_count,
    import_mode_list,
    insert_mode_item,
)
from src.core.readers import get_modes
from src.utils import CONFIG_PATH
from src.utils.types import Response


@ft.control
class TdxPathButton(ft.Button):
    def __init__(
        self,
        cfg: DictConfig,
    ) -> None:
        super().__init__(
            content="选择路径",
        )
        self.cfg = cfg
        self.on_click = self.button_clicked

    async def button_clicked(self, __e__: ft.Event[ft.Button]):
        cur_install_dir: str = await cast(
            str, ft.FilePicker().get_directory_path()
        )

        self.cfg["TDX_INSTALL_DIR"] = cur_install_dir

        with open(CONFIG_PATH, "w", encoding="utf-8") as fp:
            OmegaConf.save(config=self.cfg, f=fp)

        ft.context.page.pubsub.send_all("path_refresh")


@ft.control
class ImportModeFileButton(ft.Button):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__()
        self.content = "导入需组合计算的板块文件"
        self.on_click = self.button_clicked
        self.async_session = async_session

        self.modeFileErrorAlertDialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.Icons.ERROR_OUTLINED, color=ft.Colors.ERROR),
            alignment=ft.Alignment.CENTER,
            actions=[
                ft.TextButton(
                    "确定", on_click=lambda __e__: ft.context.page.pop_dialog()
                ),
            ],
        )

        self.notFoundBlockBanner = ft.Banner(
            leading=ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.PRIMARY),
            content=ft.Text(""),
            actions=[
                ft.TextButton(
                    "确定",
                    on_click=lambda __e__: ft.context.page.pop_dialog(),
                ),
            ],
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            open=True,
        )

    async def button_clicked(self, __e__: ft.Event[ft.Button]) -> None:
        selected_files: List[ft.FilePickerFile] = await cast(
            ft.FilePickerFile,
            ft.FilePicker().pick_files(
                allow_multiple=False,
            ),
        )

        if selected_files:
            blocks = await get_modes(
                path=cast(str, selected_files[0].path),
            )

            status: Response = await import_mode_list(
                async_session=self.async_session,
                blocks=blocks,
            )

            if status["code"] != 200:
                self.modeFileErrorAlertDialog.content = ft.Text(
                    status["message"]
                )
                ft.context.page.show_dialog(self.modeFileErrorAlertDialog)

            else:
                ft.context.page.pubsub.send_all("refresh_mode_table")
                if status["data"] and status["data"]["not_found_codes"]:
                    self.notFoundBlockBanner.content = ft.Text(
                        f"未匹配的板块: {status['data']['not_found_codes']}",
                    )


class AddBlockButton(ft.FloatingActionButton):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
        dropdown_ref: ft.Dropdown,
    ):
        super().__init__(icon=ft.Icons.ADD, on_click=self.add_clicked)
        self.async_session = async_session
        self.dropdown_ref = dropdown_ref

        self.alertDialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.Icons.ERROR_OUTLINED, color=ft.Colors.ERROR),
            alignment=ft.Alignment.CENTER,
            actions=[
                ft.TextButton(
                    "确定", on_click=lambda __e__: ft.context.page.pop_dialog()
                ),
            ],
        )

    async def add_clicked(
        self,
        __e__: ft.Event[ft.FloatingActionButton],
    ) -> None:
        if self.dropdown_ref and self.dropdown_ref.value:
            value: str = self.dropdown_ref.value
            response = await insert_mode_item(
                async_session=self.async_session,
                value=value,
            )
            if response["code"] != 200:
                self.alertDialog.content = ft.Text(response["message"])
                ft.context.page.show_dialog(self.alertDialog)

            ft.context.page.pubsub.send_all("refresh_mode_table")


@ft.control
class CalcButton(ft.FilledButton):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ):
        super().__init__(
            content="计算",
            icon=ft.Icons.CALCULATE_ROUNDED,
        )
        self.async_session = async_session
        self.on_click = self.button_clicked
        self.calcAlertDialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.Icons.ERROR_OUTLINED, color=ft.Colors.ERROR),
            alignment=ft.Alignment.CENTER,
            actions=[
                ft.TextButton(
                    "确定", on_click=lambda __e__: ft.context.page.pop_dialog()
                ),
            ],
        )

    async def button_clicked(self, __e__: ft.Event[ft.Button]) -> None:
        response = await get_combination_count(
            async_session=self.async_session,
            top_n=3,
        )
        if response["code"] != 200:
            self.calcAlertDialog.content = ft.Text(response["message"])
            ft.context.page.show_dialog(self.calcAlertDialog)


@ft.control
class ExportResultButton(ft.Button):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ):
        super().__init__(
            content="导出计算结果",
            icon=ft.Icons.IMPORT_EXPORT_ROUNDED,
        )
        self.async_session = async_session
        self.on_click = self.button_clicked
        self.alertDialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.Icons.ERROR_OUTLINED, color=ft.Colors.ERROR),
            alignment=ft.Alignment.CENTER,
            actions=[
                ft.TextButton(
                    "确定", on_click=lambda __e__: ft.context.page.pop_dialog()
                ),
            ],
        )

    async def button_clicked(self, __e__: ft.Event[ft.Button]) -> None:
        print(1)
        saved_dir: Optional[str] = await ft.FilePicker().get_directory_path()
        if not saved_dir:
            return

        response = await export_combinations(
            async_session=self.async_session,
            path=saved_dir,
        )

        if response["code"] != 200:
            self.alertDialog.content = ft.Text(response["message"])
            ft.context.page.show_dialog(self.alertDialog)
