import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from .models import Ticket, Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("\n=== WebSocket Connection Attempt ===")
        try:
            # Verify
            if not self.scope["user"].is_authenticated:
                print("Connection rejected: User not authenticated")
                await self.close()
                return

            self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
            self.room_group_name = f'chat_{self.ticket_id}'
            print(f"Connection attempt - User: {self.scope['user'].username}, Ticket: {self.ticket_id}")

            # Check access
            ticket = await self.get_ticket()
            if not ticket:
                print(f"Connection rejected: No access to ticket {self.ticket_id}")
                await self.close()
                return
            print(f"Access granted")

            await self.accept()
            print("WebSocket connection accepted")

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            print(f"Joined chat group: {self.room_group_name}")

        except Exception as e:
            print(f"WebSocket connect error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
        except Exception as e:
            print(f"WebSocket disconnect error: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
                return

            message = data.get('message', '').strip()
            if not message:
                return

            user = self.scope['user']
            if not user.is_authenticated:
                return

            # Save message
            saved_message = await self.save_message(message)
            if not saved_message:
                return

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username,
                    'timestamp': saved_message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'is_file': saved_message.is_file_message,
                    'file_name': saved_message.file_name if saved_message.is_file_message else None,
                    'file_size': saved_message.file_size_mb if saved_message.is_file_message else None
                }
            )
        except Exception as e:
            print(f"WebSocket receive error: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message'
            }))

    # Receive message from room group
    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'username': event['username'],
                'timestamp': event.get('timestamp'),
                'is_file': event.get('is_file', False),
                'file_name': event.get('file_name'),
                'file_url': event.get('file_url')
            }))
        except Exception as e:
            print(f"WebSocket chat_message error: {e}")

    @sync_to_async
    def get_ticket(self):
        try:
            ticket = Ticket.objects.get(id=self.ticket_id)
            user = self.scope['user']

            if user.groups.filter(name='Agents').exists() or ticket.creator == user:
                return ticket
            return None
        except Ticket.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, content):
        try:
            user = self.scope['user']
            ticket = Ticket.objects.get(id=self.ticket_id)
            return Message.objects.create(user=user, ticket=ticket, msg=content)
        except Exception as e:
            print(f"Error saving message: {e}")
            return None
