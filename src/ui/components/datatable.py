from typing import Dict, List, cast

import flet as ft
import flet_datatable2 as ftd
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.readers import helpers


# TODO: Disable scroll
class ModeDataTable(ft.Container):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__()

        self.async_session = async_session

        self.data_table = ftd.DataTable2(
            show_checkbox_column=False,
            heading_row_color=ft.Colors.SECONDARY_CONTAINER,
            sort_ascending=False,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            show_heading_checkbox=False,
            visible_horizontal_scroll_bar=None,
            columns=self.get_data_columns(),  # pyright: ignore
            empty=ft.Container(
                height=300,
                expand=False,
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.TABLE_VIEW,
                                size=40,
                                align=ft.Alignment.TOP_CENTER,
                            ),
                            ft.Text(
                                "暂无数据",
                                size=20,
                                align=ft.Alignment.CENTER,
                            ),
                            ft.Text(
                                "请导入或添加需要计算的板块",
                                size=20,
                                align=ft.Alignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ),
                alignment=ft.Alignment.CENTER,
            ),
        )

        ft.context.page.pubsub.subscribe(handler=self._handle_refresh)

        self.expand = True
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE

        self.content = self.data_table

    async def _handle_refresh(self, msg: str):
        if msg == "refresh_mode_table":
            data = await helpers.get_mode_data(async_session=self.async_session)
            self.data_table.rows = self.get_data_rows(data=data)  # pyright: ignore
            self.update()

    def get_data_rows(
        self, data: List[Dict[str, str | int]]
    ) -> List[ftd.DataRow2]:
        data_rows = []
        for row in data:
            data_rows.append(
                ftd.DataRow2(
                    specific_row_height=30,
                    cells=[
                        ft.DataCell(content=ft.Text(cast(str, row["code"]))),
                        ft.DataCell(content=ft.Text(cast(str, row["name"]))),
                        ft.DataCell(content=ft.Text(cast(str, row["count"]))),
                    ],
                )
            )
        return data_rows

    def get_data_columns(self) -> List[ftd.DataColumn2]:
        data_columns = [
            ftd.DataColumn2(
                label=ft.Text("板块代码"),
            ),
            ftd.DataColumn2(
                label=ft.Text("板块名称"),
            ),
            ftd.DataColumn2(
                label=ft.Text("股票数量"),
                numeric=True,
            ),
        ]
        return data_columns
