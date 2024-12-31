import json
from machine import UART
from collections import deque
import time
import asyncio
from micropython import const

# Communication constants
UART_BUFFER_SIZE = const(1024)
MSG_DELIMITER = b'\n'
RETRY_DELAY = const(100)  # ms
MAX_RETRIES = const(3)

class MessageType:
    STATE = 'state'
    EVENT = 'event'
    COMMAND = 'command'
    ERROR = 'error'
    ACK = 'ack'

class CommHandler:
    def __init__(self, uart_id=0, baudrate=115200):
        # Initialize UART
        self.uart = UART(uart_id)
        self.uart.init(baudrate=baudrate, 
                      bits=8, 
                      parity=None, 
                      stop=1, 
                      timeout=1000,
                      rxbuf=UART_BUFFER_SIZE,
                      txbuf=UART_BUFFER_SIZE)
        
        # Message queues
        self.outgoing_queue = deque(maxlen=100)
        self.retry_queue = deque(maxlen=50)
        
        # State tracking
        self.connected = False
        self.last_send = 0
        self.last_receive = 0
        self.message_id = 0
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'retries': 0
        }

    async def send_state(self, state_data):
        """Send state update"""
        message = {
            'type': MessageType.STATE,
            'id': self._get_message_id(),
            'timestamp': time.time(),
            'data': state_data
        }
        await self._send_message(message)

    async def send_event(self, event_type, event_data):
        """Send event notification"""
        message = {
            'type': MessageType.EVENT,
            'id': self._get_message_id(),
            'timestamp': time.time(),
            'event_type': event_type,
            'data': event_data
        }
        await self._send_message(message)

    async def check_messages(self):
        """Check for incoming messages"""
        if self.uart.any():
            try:
                raw_data = self.uart.readline()
                if raw_data:
                    message = json.loads(raw_data.decode().strip())
                    self.last_receive = time.time()
                    self.stats['messages_received'] += 1
                    
                    # Handle acknowledgments
                    if message.get('type') == MessageType.ACK:
                        self._handle_ack(message)
                    
                    return message
            except Exception as e:
                print(f"Message read error: {e}")
                self.stats['errors'] += 1
        return None

    async def _send_message(self, message, retry=True):
        """Send a message with optional retry"""
        try:
            json_str = json.dumps(message) + '\n'
            self.uart.write(json_str.encode())
            self.last_send = time.time()
            self.stats['messages_sent'] += 1
            
            if retry:
                # Add to retry queue if acknowledgment needed
                message['retries'] = 0
                message['sent_time'] = self.last_send
                self.retry_queue.append(message)
                
        except Exception as e:
            print(f"Send error: {e}")
            self.stats['errors'] += 1
            if retry:
                self.outgoing_queue.append(message)

    async def process_retries(self):
        """Process message retries"""
        current_time = time.time()
        
        # Check retry queue
        for _ in range(len(self.retry_queue)):
            message = self.retry_queue.popleft()
            
            # Check if message is too old or too many retries
            if (message['retries'] >= MAX_RETRIES or 
                current_time - message['sent_time'] > 10):
                continue
                
            # Retry sending
            message['retries'] += 1
            self.stats['retries'] += 1
            await self._send_message(message, retry=False)
            
        # Process outgoing queue
        while self.outgoing_queue:
            message = self.outgoing_queue.popleft()
            await self._send_message(message)
            await asyncio.sleep_ms(RETRY_DELAY)

    def _handle_ack(self, ack_message):
        """Handle acknowledgment messages"""
        msg_id = ack_message.get('ack_id')
        if msg_id:
            # Remove message from retry queue
            self.retry_queue = deque(
                msg for msg in self.retry_queue 
                if msg['id'] != msg_id
            )

    def _get_message_id(self):
        """Generate unique message ID"""
        self.message_id += 1
        return f"{time.time()}-{self.message_id}"

    def get_stats(self):
        """Get communication statistics"""
        return {
            **self.stats,
            'connected': self.connected,
            'last_send': self.last_send,
            'last_receive': self.last_receive,
            'outgoing_queue': len(self.outgoing_queue),
            'retry_queue': len(self.retry_queue)
        }

    def check_connection(self):
        """Check if connection is active"""
        current_time = time.time()
        self.connected = (current_time - self.last_receive) < 5
        return self.connected