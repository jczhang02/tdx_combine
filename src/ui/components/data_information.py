import flet as ft


@ft.control
class DataInformationPanel(ft.Container):
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
