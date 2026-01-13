import flet as ft
import requests
import json
import asyncio
import websockets
from datetime import datetime

# Configuration
API_BASE_URL = "http://your-server-ip:8000/api/v1"
WS_BASE_URL = "ws://your-server-ip:8000/ws"

class ChatApp:
    def __init__(self):
        self.page = None
        self.auth_token = None
        self.current_user = None
        self.websocket = None
        self.current_room_id = None
        
    def main(self, page: ft.Page):
        self.page = page
        page.title = "ChatApp"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        
        # Check if already logged in
        if self.auth_token:
            self.show_chat_list()
        else:
            self.show_login()
    
    # ==================== AUTH VIEWS ====================
    
    def show_login(self):
        username_field = ft.TextField(
            label="Username",
            border_radius=10
        )
        password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border_radius=10
        )
        error_text = ft.Text(color="red", visible=False)
        
        def login_click(e):
            error_text.visible = False
            self.page.update()
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/token/",
                    json={
                        "username": username_field.value,
                        "password": password_field.value
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data['access']
                    self.current_user = username_field.value
                    self.show_chat_list()
                else:
                    error_text.value = "Invalid credentials"
                    error_text.visible = True
                    self.page.update()
            except Exception as ex:
                error_text.value = f"Connection error: {str(ex)}"
                error_text.visible = True
                self.page.update()
        
        def register_click(e):
            self.show_register()
        
        login_view = ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=50),
                    ft.Text("💬", size=80),
                    ft.Text("ChatApp", size=32, weight=ft.FontWeight.BOLD),
                    ft.Container(height=30),
                    username_field,
                    password_field,
                    error_text,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Login",
                        on_click=login_click,
                        width=200,
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    ft.TextButton(
                        "Don't have an account? Register",
                        on_click=register_click
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=20
        )
        
        self.page.controls.clear()
        self.page.add(login_view)
    
    def show_register(self):
        username_field = ft.TextField(label="Username", border_radius=10)
        email_field = ft.TextField(label="Email", border_radius=10)
        password_field = ft.TextField(label="Password", password=True, border_radius=10)
        password2_field = ft.TextField(label="Confirm Password", password=True, border_radius=10)
        error_text = ft.Text(color="red", visible=False)
        
        def register_submit(e):
            error_text.visible = False
            
            if password_field.value != password2_field.value:
                error_text.value = "Passwords don't match"
                error_text.visible = True
                self.page.update()
                return
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/register/",
                    json={
                        "username": username_field.value,
                        "email": email_field.value,
                        "password": password_field.value,
                        "password2": password2_field.value
                    }
                )
                
                if response.status_code == 201:
                    # Auto-login after registration
                    login_response = requests.post(
                        f"{API_BASE_URL}/token/",
                        json={
                            "username": username_field.value,
                            "password": password_field.value
                        }
                    )
                    if login_response.status_code == 200:
                        data = login_response.json()
                        self.auth_token = data['access']
                        self.current_user = username_field.value
                        self.show_chat_list()
                else:
                    error_text.value = response.json().get('error', 'Registration failed')
                    error_text.visible = True
                    self.page.update()
            except Exception as ex:
                error_text.value = f"Error: {str(ex)}"
                error_text.visible = True
                self.page.update()
        
        register_view = ft.Container(
            content=ft.Column(
                [
                    ft.TextButton(
                        "← Back",
                        on_click=lambda e: self.show_login()
                    ),
                    ft.Text("Create Account", size=28, weight=ft.FontWeight.BOLD),
                    username_field,
                    email_field,
                    password_field,
                    password2_field,
                    error_text,
                    ft.ElevatedButton(
                        "Register",
                        on_click=register_submit,
                        width=200,
                        height=50
                    )
                ],
                spacing=15
            ),
            padding=20
        )
        
        self.page.controls.clear()
        self.page.add(register_view)
    
    # ==================== CHAT LIST VIEW ====================
    
    def show_chat_list(self):
        chat_rooms = []
        
        def load_rooms():
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.get(f"{API_BASE_URL}/rooms/", headers=headers)
                
                if response.status_code == 200:
                    rooms = response.json()
                    chat_rooms.clear()
                    
                    for room in rooms:
                        chat_rooms.append(
                            ft.ListTile(
                                leading=ft.CircleAvatar(
                                    content=ft.Text(room['name'][0].upper()),
                                    bgcolor="lightblue"
                                ),
                                title=ft.Text(room['name'], weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(
                                    room.get('last_message', 'No messages yet')[:50]
                                ),
                                on_click=lambda e, room_id=room['id']: self.open_chat_room(room_id),
                                trailing=ft.Text("›", size=24)
                            )
                        )
                    
                    room_list.controls = chat_rooms
                    self.page.update()
            except Exception as ex:
                print(f"Error loading rooms: {ex}")
        
        def logout_click(e):
            self.auth_token = None
            self.current_user = None
            self.show_login()
        
        def new_chat_click(e):
            self.show_new_chat_dialog()
        
        room_list = ft.ListView(
            spacing=0,
            padding=10,
            expand=True
        )
        
        app_bar = ft.AppBar(
            title=ft.Text("Chats"),
            center_title=False,
            bgcolor="blue",
            actions=[
                ft.TextButton("➕", on_click=new_chat_click, style=ft.ButtonStyle(color="white")),
                ft.TextButton("🚪", on_click=logout_click, style=ft.ButtonStyle(color="white"))
            ]
        )
        
        self.page.controls.clear()
        self.page.appbar = app_bar
        self.page.add(room_list)
        
        # Load rooms
        load_rooms()
    
    def show_new_chat_dialog(self):
        room_name_field = ft.TextField(label="Room Name", hint_text="Enter room name")
        
        def create_room(e):
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.post(
                    f"{API_BASE_URL}/rooms/",
                    headers=headers,
                    json={"name": room_name_field.value}
                )
                
                if response.status_code == 201:
                    self.page.dialog.open = False
                    self.page.update()
                    self.show_chat_list()
            except Exception as ex:
                print(f"Error creating room: {ex}")
        
        dialog = ft.AlertDialog(
            title=ft.Text("New Chat Room"),
            content=room_name_field,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog()),
                ft.TextButton("Create", on_click=create_room)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()
    
    # ==================== CHAT ROOM VIEW ====================
    
    def open_chat_room(self, room_id):
        self.current_room_id = room_id
        messages_list = ft.ListView(
            spacing=10,
            padding=10,
            auto_scroll=True,
            expand=True
        )
        
        message_input = ft.TextField(
            hint_text="Type a message...",
            expand=True,
            border_radius=20,
            filled=True
        )
        
        async def websocket_handler():
            uri = f"{WS_BASE_URL}/chat/{room_id}/"
            try:
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    
                    # Listen for messages
                    async for message in websocket:
                        data = json.loads(message)
                        
                        is_me = data['username'] == self.current_user
                        
                        msg_bubble = ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    data['username'],
                                    size=11,
                                    color="grey"
                                ) if not is_me else ft.Container(),
                                ft.Text(data['message']),
                                ft.Text(
                                    datetime.fromisoformat(data['timestamp']).strftime("%H:%M"),
                                    size=10,
                                    color="grey"
                                )
                            ], spacing=2),
                            bgcolor="lightblue" if is_me else "lightgrey",
                            border_radius=15,
                            padding=10,
                            alignment=ft.alignment.center_right if is_me else ft.alignment.center_left
                        )
                        
                        messages_list.controls.append(
                            ft.Row(
                                [msg_bubble],
                                alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START
                            )
                        )
                        self.page.update()
            except Exception as ex:
                print(f"WebSocket error: {ex}")
        
        async def send_message(e):
            if message_input.value and self.websocket:
                try:
                    await self.websocket.send(json.dumps({
                        'message': message_input.value,
                        'username': self.current_user
                    }))
                    message_input.value = ""
                    self.page.update()
                except Exception as ex:
                    print(f"Send error: {ex}")
        
        def back_click(e):
            if self.websocket:
                asyncio.create_task(self.websocket.close())
            self.show_chat_list()
        
        # Start WebSocket connection
        asyncio.create_task(websocket_handler())
        
        chat_view = ft.Column(
            [
                ft.AppBar(
                    leading=ft.TextButton(
                        "←",
                        on_click=back_click,
                        style=ft.ButtonStyle(color="white")
                    ),
                    title=ft.Text(f"Room {room_id}"),
                    bgcolor="blue"
                ),
                messages_list,
                ft.Container(
                    content=ft.Row(
                        [
                            message_input,
                            ft.ElevatedButton(
                                "📤",
                                bgcolor="blue",
                                color="white",
                                on_click=lambda e: asyncio.create_task(send_message(e))
                            )
                        ],
                        spacing=10
                    ),
                    padding=10,
                    bgcolor="white"
                )
            ],
            spacing=0,
            expand=True
        )
        
        self.page.controls.clear()
        self.page.appbar = None
        self.page.add(chat_view)


# Run the app
if __name__ == "__main__":
    app = ChatApp()
    ft.app(target=app.main)