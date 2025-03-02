import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        await self.channel_layer.group_add(
            f"notifications_{self.user_id}",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"notifications_{self.user_id}",
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"Received message: {text_data}")

    async def send_notification(self, event):
        print(f"Sending notification: {event['message']}")
        await self.send(text_data=event['message'])
