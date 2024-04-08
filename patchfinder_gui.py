import flet as ft


def find_unused_ports(e, page):
    result_view.value = "Function to find unused ports goes here."
    page.update()


def main(page: ft.Page):
    # def page_resize(e):
    #     print(f"{page.height} x {page.width} px")
    # page.on_resize = page_resize

    page.window_height = 300
    page.window_width = 615
    
    page.title = "PatchFinder"
    page.vertical_alignment = "start"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Header
    header_container = ft.Container(
        content=ft.Text("PatchFinder", size="30", weight="BOLD"),
        margin=ft.Margin(0, 0, 0, 8)
    )
    
    # Input fields
    ip_address = ft.TextField(label="IP Address", autofocus=True)
    
    # Username and Password Fields on the same row
    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True)
    creds_row = ft.ResponsiveRow([ft.Column(col={"sm": 6}, controls=[username]),
                                  ft.Column(col={"sm": 6}, controls=[password])])  # Arrange them in a Row
    
    # Button to find unused ports
    find_ports_button = ft.ElevatedButton(text="Find unused ports", on_click=find_unused_ports)
    
    # Container for results
    global result_view
    result_view = ft.Text()
    
    # Grouping elements together in a Column layout
    inputs_column = ft.Column([
        header_container,
        ip_address,
        creds_row,
        find_ports_button,
        result_view
    ], spacing=10)  # Adjust spacing as needed
    
    # Adding the Column to the page instead of individual elements
    page.add(inputs_column)


ft.app(target=main)
