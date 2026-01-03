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
            expand=False,
            heading_row_color=ft.Colors.SECONDARY_CONTAINER,
            sort_ascending=False,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            show_heading_checkbox=False,
            visible_horizontal_scroll_bar=None,
            border=ft.Border.all(1, ft.Colors.BLUE),
            columns=self.get_data_columns(),  # pyright: ignore
            # rows=self.get_initial_data_rows(),  # pyright: ignore
            empty=ft.Text("暂无可组合计算板块"),
        )

        ft.context.page.pubsub.subscribe(handler=self._handle_refresh)

        self.height = 400
        self.width = 600
        self.expand = False
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE

        self.content = ft.Column(
            controls=[
                self.data_table,
            ],
            height=400,
            width=600,
            scroll=ft.ScrollMode.ADAPTIVE,
        )

    async def _handle_refresh(self, msg: str):
        if msg == "refresh_mode_table":
            data = await helpers.get_mode_data(async_session=self.async_session)
            self.data_table.rows = self.get_data_rows(data=data)  # pyright: ignore
            self.update()

    def get_initial_data_rows(self) -> List[ftd.DataRow2]:
        return [
            ftd.DataRow2(
                specific_row_height=30,
                cells=[
                    ft.DataCell(content=ft.Text()),
                    ft.DataCell(content=ft.Text()),
                    ft.DataCell(content=ft.Text()),
                ],
            )
            for _ in range(10)
        ]

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
                        ft.DataCell(content=ft.Text(cast(str, row["code"]))),
                    ],
                )
            )
        return data_rows

    def get_data_columns(self) -> List[ftd.DataColumn2]:
        data_columns = [
            ftd.DataColumn2(
                label=ft.Text("板块代码"),
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
            ),
            ftd.DataColumn2(
                label=ft.Text("板块名称"),
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
            ),
            ftd.DataColumn2(
                label=ft.Text("股票数量"),
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
                numeric=True,
            ),
        ]
        return data_columns
