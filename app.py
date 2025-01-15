import flet as ft
import calendar
from datetime import datetime

cal = calendar.Calendar()



# pre-definied calendar maps ...
date_class: dict[int, str] = {
    0: "Mo",
    1: "Tu",
    2: "We",
    3: "Th",
    4: "Fr",
    5: "Sa",
    6: "Su"}

month_class: dict[int, str] = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"}

# Date class to handle calendar logic...
class Settings:
    # in this class we'll use datetime module to handle dates...
    year: int = datetime.now().year
    month: int = datetime.now().month
    
    # static method to return the !year
    @staticmethod
    def get_year() -> int:
        return Settings.year
    
    # static method to return the !month
    @staticmethod
    def get_month() -> int:
        return Settings.month
    
    # static method to calculate month changes (user event)
    @staticmethod
    def get_date(delta: int):
        # the following logic handles changes in the month
        # If the user triggers back, we check whether the limit of 1 has been exceeded and handle it accordingly. The same applies to the "next" trigger...
        if delta == 1:
            if Settings.month + delta > 12:
                Settings.month = 1
                Settings.year += 1
            else:
                Settings.month += 1
        if delta == -1:
            if Settings.month + delta < 1:
                Settings.month = 12
                Settings.year -= 1
            else:
                Settings.month -= 1
            



# Custom Container class to display days...
date_box_style = {
    "width": 30, "height": 30, "alignment": ft.alignment.center, "shape": ft.BoxShape("rectangle"), "animate": ft.Animation(400, "ease"), "border_radius": 5}

class DateBox(ft.Container):
    def __init__(
        self,
        day: int,
        date: str = None,
        date_instance: ft.Column = None,
        task_instance: ft.Column = None,
        opacity_: float | int = None
    ) -> None:
        super(DateBox, self).__init__(
            **date_box_style,
            data=date,
            opacity=opacity_, 
            # add a on_click trigger to select days
            on_click=self.selected,
            bgcolor="#696A71" if date != None and datetime.strptime(date, "%B %d, %Y").date() == datetime.today().date() else None
        )
        
        self.day: int = day
        self.date_instance: ft.Column = date_instance
        self.task_instance: ft.Column = task_instance
        
        self.content = ft.Text(self.day, text_align="center")

    def selected(self, e: ft.TapEvent):
        # because each BoxDay has the !grid instance, we can loop over the row and check see which day is being clicked and update the UI...
        if self.date_instance: # to bypass any errors
            # [1:] because we skip over the weekday row
            for row in self.date_instance.controls[1:]:
                for date in row.controls:
                    
                    # Checking conditions...
                    is_today = datetime.strptime(date.data, "%B %d, %Y").date() == datetime.today().date() if date.data != None else False
                    is_selected = date == e.control

                    # Set the background color based on the conditions...
                    if is_selected:
                        date.bgcolor = "#696A71" if is_today else "#20303e"
                    else:
                        date.bgcolor = "#696A71" if is_today else None

                    date.border = ft.border.all(0.5, "#4fadf9") if is_selected else None
                    
                    # we can add one more line of code to display the clicked date into the text field
                    if date == e.control:
                        # recall that we passed in a formatted date, under the method called !format_date
                        self.task_instance.date.value = e.control.data
            
            self.date_instance.update()
            self.task_instance.update()

# Calendar class that sets up UI for year/month...
class DateGrid(ft.Column):
    # data grid takes in !year and !month as well as the task
    def __init__(self, year: int, month: int, task_instance: object) -> None:
        super(DateGrid, self).__init__()
        
        self.year: int = year
        self.month: int = month
        self.task_manager: object = task_instance
        
        self.date = ft.Text(f"{month_class[self.month]} {self.year}")
        
        self.year_and_month = ft.Container(
            bgcolor="#20303e",
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
            content=ft.Row(
                alignment="center",
                controls=[
                    ft.IconButton(
                        "chevron_left",
                        on_click=lambda e: self.update_date_grid(e, -1)
                    ),
                    ft.Container(
                        width=150, 
                        content=self.date, 
                        alignment=ft.alignment.center
                    ),
                    ft.IconButton(
                        "chevron_right",
                        on_click=lambda e: self.update_date_grid(e, 1)
                    )
                ]
            ))

        self.controls.insert(1, self.year_and_month)
        
        week_days = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            controls=[
                DateBox(day=date_class[index], opacity_=0.7) for index in range(7)
            ])
        
        self.controls.insert(1, week_days)
        self.populate_date_grid(self.year, self.month)
        
    # this method adds the days of each week accordingly...
    def populate_date_grid(self, year: int, month: int) -> None:
        # delete all controls after the list of days of the week row
        del self.controls[2:]
        
        for week in cal.monthdayscalendar(year, month):
            row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY)
            for day in week:
                if day != 0:
                    row.controls.append(
                        DateBox(
                            day, self.format_date(day), self, self.task_manager
                        )
                    )
                else:
                    row.controls.append(DateBox(" "))
                    
            self.controls.append(row)
    
    # We neeed a method to update the UI when user triggers back or next for !month
    def update_date_grid(self, e: ft.TapEvent, delta: int):
        # We need to pass delta (either 1 or -1) to settings and get current year and month changes...
        # The logic is set up, we can trigger the method first...
        Settings.get_date(delta) # make sure to pass in delta...
        
        self.update_year_and_month(
            Settings.get_year(), Settings.get_month()
        )
        
        self.populate_date_grid(
            Settings.get_year(), Settings.get_month()
        )
        
        self.update()
    
    # Another helper method to insert the changes post-event trigger
    def update_year_and_month(self, year: int, month: int):
        self.year: int = year
        self.month: int = month
        self.date.value = f"{month_class[self.month]} {self.year}"
    
    # A helper method to format and return the day...      
    def format_date(self, day: int) -> str:
        return f"{month_class[self.month]} {day}, {self.year}"



# some styling for the inputs we will use...
def input_style(height: int) -> dict[str, any]:
    return {
        "height": height,
        "focused_border_color": "blue",
        "border_radius": 5,
        "cursor_height": 16,
        "cursor_color": "white",
        "content_padding": 10,
        "border_width": 1.5,
        "text_size": 12
    }

# Task manager class to handle tasks (if app is a to-do app)
class TaskManager(ft.Column):
    def __init__(self) -> None:
        super(TaskManager, self).__init__()

        self.date = ft.TextField(
            label="Date", read_only=True, value=" ", **input_style(38)
        )
        
        self.controls = [
            self.date
        ]


def main(page: ft.Page) -> None:
    # page settings...
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1f2128"

    task_manager = TaskManager()
    
    # first instance, we need to pass current month and year...
    grid = DateGrid(
        year=Settings.get_year(),
        month=Settings.get_month(),
        task_instance=task_manager
    )
    
    page.add(
        ft.Container(
            height=350,
            border=ft.border.all(0.75, "#4fadf9"),
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=grid
        ),
        ft.Divider(color="transparent", height=20),
        task_manager
    )

    page.update()
    
ft.app(main)
    