<template>
  <div class="messaging-container">
    <!-- Header with title -->
    <div class="messaging-header">
      <h2>{{ title }}</h2>
      <div v-if="status === 'connected'" class="status-indicator connected">Connected</div>
      <div v-else-if="status === 'connecting'" class="status-indicator connecting">Connecting...</div>
      <div v-else class="status-indicator disconnected">Disconnected</div>
    </div>
    
    <!-- Message thread container -->
    <div class="message-thread" ref="messageThread">
      <!-- System welcome message -->
      <div v-if="messages.length === 0" class="system-message">
        <div class="system-message-text">{{ welcomeMessage }}</div>
      </div>
      
      <!-- Message items -->
      <div v-for="(message, index) in messages" :key="message.id" class="message-item"
           :class="{'user-message': message.sender.type === 'user', 'agent-message': message.sender.type !== 'user'}">
        <!-- Sender info -->
        <div class="message-sender">
          {{ message.sender.type === 'user' ? 'You' : message.sender.type }}
        </div>
        
        <!-- Message content -->
        <div class="message-content">
          <!-- Text content -->
          <div v-if="message.content.text" class="message-text">{{ message.content.text }}</div>
          
          <!-- Visualizations -->
          <div v-if="message.content.visualizations && message.content.visualizations.length > 0" 
               class="visualization-container">
            <div v-for="(viz, vizIndex) in message.content.visualizations" :key="viz.id" 
                 class="visualization-item">
              <h4>{{ viz.title }}</h4>
              <!-- Visualization placeholder - in a real app, this would render the actual visualization -->
              <div class="visualization-placeholder" :data-type="viz.type">
                [{{ viz.type }} Visualization: {{ viz.title }}]
              </div>
            </div>
          </div>
          
          <!-- UI Components -->
          <div v-if="message.content.components && message.content.components.length > 0" 
               class="components-container">
            <div v-for="(component, compIndex) in message.content.components" :key="component.id" 
                 class="component-item">
              <!-- Component placeholder - in a real app, dynamic components would be rendered -->
              <div class="component-placeholder" :data-type="component.type">
                [{{ component.type }} Component]
              </div>
            </div>
          </div>
          
          <!-- Actions -->
          <div v-if="message.content.actions && message.content.actions.length > 0" 
               class="actions-container">
            <button v-for="action in message.content.actions" :key="action.id"
                    class="action-button" @click="handleAction(action)">
              {{ action.label }}
            </button>
          </div>
        </div>
        
        <!-- Timestamp -->
        <div class="message-timestamp">
          {{ formatTimestamp(message.timestamp) }}
        </div>
      </div>
      
      <!-- Loading indicator -->
      <div v-if="isLoading" class="loading-indicator">
        <div class="loading-dots">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>
    </div>
    
    <!-- Message input -->
    <div class="message-input-container">
      <textarea 
        v-model="userInput" 
        @keydown.enter.prevent="sendMessage"
        placeholder="Type your message..." 
        class="message-input"
        :disabled="isLoading || status !== 'connected'"
      ></textarea>
      <button 
        @click="sendMessage" 
        class="send-button"
        :disabled="isLoading || userInput.trim() === '' || status !== 'connected'"
      >
        <span>Send</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MessagingV1',
  
  props: {
    title: {
      type: String,
      default: 'Government Policy Assistant'
    },
    welcomeMessage: {
      type: String,
      default: 'Welcome to the Government Policy Assistant. How can I help you today?'
    },
    apiEndpoint: {
      type: String,
      default: '/api/messaging'
    },
    wsEndpoint: {
      type: String,
      default: null
    },
    useWebSocket: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      messages: [],
      userInput: '',
      isLoading: false,
      status: 'disconnected',
      webSocket: null
    };
  },
  
  created() {
    if (this.useWebSocket && this.wsEndpoint) {
      this.connectWebSocket();
    } else {
      this.status = 'connected';
    }
  },
  
  beforeDestroy() {
    if (this.webSocket) {
      this.webSocket.close();
    }
  },
  
  watch: {
    messages() {
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    }
  },
  
  methods: {
    /**
     * Connect to WebSocket if enabled
     */
    connectWebSocket() {
      this.status = 'connecting';
      
      try {
        this.webSocket = new WebSocket(this.wsEndpoint);
        
        this.webSocket.onopen = () => {
          this.status = 'connected';
        };
        
        this.webSocket.onmessage = (event) => {
          const message = JSON.parse(event.data);
          this.handleIncomingMessage(message);
        };
        
        this.webSocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.status = 'disconnected';
        };
        
        this.webSocket.onclose = () => {
          this.status = 'disconnected';
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
        this.status = 'disconnected';
      }
    },
    
    /**
     * Send a message
     */
    async sendMessage() {
      if (this.isLoading || this.userInput.trim() === '' || this.status !== 'connected') {
        return;
      }
      
      // Create user message
      const userMessage = {
        id: `user-${Date.now()}`,
        timestamp: new Date().toISOString(),
        sender: {
          id: 'user',
          type: 'user'
        },
        type: 'query',
        content: {
          text: this.userInput
        }
      };
      
      // Add message to thread
      this.messages.push(userMessage);
      
      // Clear input
      const userText = this.userInput;
      this.userInput = '';
      
      // Set loading state
      this.isLoading = true;
      
      try {
        // Send message via WebSocket or HTTP
        if (this.useWebSocket && this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
          this.webSocket.send(JSON.stringify(userMessage));
        } else {
          // Send via HTTP
          const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(userMessage)
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
          }
          
          const responseData = await response.json();
          this.handleIncomingMessage(responseData);
        }
      } catch (error) {
        console.error('Error sending message:', error);
        
        // Add error message to thread
        this.messages.push({
          id: `error-${Date.now()}`,
          timestamp: new Date().toISOString(),
          sender: {
            id: 'system',
            type: 'system'
          },
          type: 'response',
          content: {
            text: `Failed to send message: ${error.message}`
          },
          status: 'error'
        });
      } finally {
        // Clear loading state
        this.isLoading = false;
      }
    },
    
    /**
     * Handle incoming messages from the server
     */
    handleIncomingMessage(message) {
      // Add message to thread
      this.messages.push(message);
      
      // Emit event
      this.$emit('message-received', message);
    },
    
    /**
     * Handle action button clicks
     */
    handleAction(action) {
      // Emit action event
      this.$emit('action-clicked', action);
      
      // Handle special actions
      if (action.action === 'followUpQuestion') {
        // Focus on input
        this.$nextTick(() => {
          const inputEl = this.$el.querySelector('.message-input');
          if (inputEl) {
            inputEl.focus();
          }
        });
      }
    },
    
    /**
     * Format timestamp
     */
    formatTimestamp(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    /**
     * Scroll to bottom of message thread
     */
    scrollToBottom() {
      const container = this.$refs.messageThread;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }
};
</script>

<style scoped>
.messaging-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  overflow: hidden;
}

.messaging-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background-color: #f0f0f0;
  border-bottom: 1px solid #ddd;
}

.messaging-header h2 {
  margin: 0;
  font-size: 1.2rem;
}

.status-indicator {
  font-size: 0.8rem;
  padding: 4px 8px;
  border-radius: 12px;
}

.status-indicator.connected {
  background-color: #d4edda;
  color: #155724;
}

.status-indicator.connecting {
  background-color: #fff3cd;
  color: #856404;
}

.status-indicator.disconnected {
  background-color: #f8d7da;
  color: #721c24;
}

.message-thread {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  flex-direction: column;
  max-width: 85%;
  padding: 12px;
  border-radius: 8px;
  position: relative;
}

.user-message {
  align-self: flex-end;
  background-color: #e3f2fd;
  border: 1px solid #bbdefb;
}

.agent-message {
  align-self: flex-start;
  background-color: white;
  border: 1px solid #ddd;
}

.system-message {
  align-self: center;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  max-width: 80%;
}

.message-sender {
  font-weight: bold;
  font-size: 0.8rem;
  margin-bottom: 4px;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-text {
  word-break: break-word;
  white-space: pre-wrap;
}

.message-timestamp {
  align-self: flex-end;
  font-size: 0.7rem;
  color: #777;
  margin-top: 4px;
}

.visualization-container, 
.components-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 8px 0;
}

.visualization-placeholder, 
.component-placeholder {
  background-color: #f0f0f0;
  border: 1px dashed #aaa;
  border-radius: 4px;
  padding: 12px;
  text-align: center;
  color: #555;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.actions-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.action-button {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 16px;
  padding: 6px 12px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-button:hover {
  background-color: #e0e0e0;
}

.loading-indicator {
  align-self: center;
  margin: 8px 0;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots .dot {
  width: 8px;
  height: 8px;
  background-color: #aaa;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% { 
    transform: scale(0);
  } 40% { 
    transform: scale(1.0);
  }
}

.message-input-container {
  display: flex;
  padding: 12px;
  background-color: #fff;
  border-top: 1px solid #ddd;
  gap: 8px;
}

.message-input {
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  font-family: inherit;
  font-size: 0.9rem;
}

.send-button {
  padding: 0 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #3d8b40;
}

.send-button:disabled {
  background-color: #9e9e9e;
  cursor: not-allowed;
}
</style>