/**
 * WebSocket Communicator
 * 
 * Implements a WebSocket-based communication system between TypeScript and Python components
 * for more efficient data transfer compared to file-based communication.
 */

import * as WebSocket from 'ws';
import { EventEmitter } from 'events';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Communication message types
 */
export enum MessageType {
  INITIALIZE = 'initialize',
  EVOLVE = 'evolve',
  REFINE = 'refine',
  EVALUATE = 'evaluate',
  RESULT = 'result',
  ERROR = 'error',
  PROGRESS = 'progress',
  CLOSE = 'close'
}

/**
 * Communication message interface
 */
export interface CommunicationMessage {
  type: MessageType;
  id: string;
  payload: any;
  timestamp: number;
}

/**
 * Communication options interface
 */
export interface CommunicationOptions {
  pythonPath?: string;
  scriptPath?: string;
  port?: number;
  verbose?: boolean;
  timeout?: number;
  retries?: number;
}

/**
 * WebSocket Communicator class for efficient TypeScript-Python communication
 */
export class WebSocketCommunicator extends EventEmitter {
  private server: WebSocket.Server | null = null;
  private client: WebSocket | null = null;
  private pythonProcess: ChildProcess | null = null;
  private isServerRunning: boolean = false;
  private isConnected: boolean = false;
  private messageCallbacks: Map<string, { resolve: Function; reject: Function; timer: NodeJS.Timeout }> = new Map();
  private options: CommunicationOptions;
  private defaultOptions: CommunicationOptions = {
    pythonPath: 'python3',
    scriptPath: path.join(__dirname, '..', '..', 'recursive_thinking', 'websocket_server.py'),
    port: 8765,
    verbose: false,
    timeout: 60000, // 1 minute
    retries: 3
  };

  /**
   * Constructor
   * @param options Communication options
   */
  constructor(options: CommunicationOptions = {}) {
    super();
    this.options = { ...this.defaultOptions, ...options };
  }

  /**
   * Initialize the WebSocket communicator
   */
  async initialize(): Promise<void> {
    if (this.isServerRunning) {
      return;
    }

    // Check if Python script exists
    if (!fs.existsSync(this.options.scriptPath)) {
      throw new Error(`Python WebSocket server script not found at ${this.options.scriptPath}`);
    }

    // Start Python WebSocket server
    await this.startPythonServer();

    // Create WebSocket client
    await this.connectToServer();

    // Listen for messages
    this.setupMessageHandling();

    this.isServerRunning = true;
    
    if (this.options.verbose) {
      console.log('WebSocket communicator initialized successfully');
    }
  }

  /**
   * Start the Python WebSocket server
   */
  private async startPythonServer(): Promise<void> {
    return new Promise((resolve, reject) => {
      const port = this.options.port.toString();
      const args = [
        this.options.scriptPath,
        '--port', port
      ];

      if (this.options.verbose) {
        args.push('--verbose');
      }

      this.pythonProcess = spawn(this.options.pythonPath, args);

      // Handle output
      let serverOutput = '';
      this.pythonProcess.stdout.on('data', (data) => {
        serverOutput += data.toString();
        if (this.options.verbose) {
          console.log(`[Python Server] ${data.toString().trim()}`);
        }

        // Check if server is running
        if (serverOutput.includes('WebSocket server running on port')) {
          resolve();
        }
      });

      // Handle errors
      this.pythonProcess.stderr.on('data', (data) => {
        console.error(`[Python Server Error] ${data.toString().trim()}`);
        if (!this.isServerRunning) {
          reject(new Error(`Failed to start Python WebSocket server: ${data.toString()}`));
        }
      });

      // Handle process exit
      this.pythonProcess.on('close', (code) => {
        if (code !== 0 && !this.isServerRunning) {
          reject(new Error(`Python WebSocket server exited with code ${code}`));
        }
        this.isServerRunning = false;
      });

      // Set a timeout
      setTimeout(() => {
        if (!this.isServerRunning) {
          reject(new Error('Timed out waiting for Python WebSocket server to start'));
        }
      }, 10000);
    });
  }

  /**
   * Connect to the WebSocket server
   */
  private async connectToServer(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.client = new WebSocket(`ws://localhost:${this.options.port}`);

      this.client.on('open', () => {
        this.isConnected = true;
        if (this.options.verbose) {
          console.log('Connected to Python WebSocket server');
        }
        resolve();
      });

      this.client.on('error', (error) => {
        console.error('WebSocket client error:', error);
        if (!this.isConnected) {
          reject(error);
        }
      });

      this.client.on('close', () => {
        this.isConnected = false;
        if (this.options.verbose) {
          console.log('Disconnected from Python WebSocket server');
        }
      });

      // Set a timeout
      setTimeout(() => {
        if (!this.isConnected) {
          reject(new Error('Timed out waiting to connect to Python WebSocket server'));
        }
      }, 10000);
    });
  }

  /**
   * Set up message handling
   */
  private setupMessageHandling(): void {
    if (!this.client) {
      throw new Error('WebSocket client not initialized');
    }

    this.client.on('message', (data: WebSocket.Data) => {
      try {
        const message: CommunicationMessage = JSON.parse(data.toString());
        
        if (this.options.verbose) {
          console.log(`Received message of type ${message.type} with ID ${message.id}`);
        }

        // Emit progress events
        if (message.type === MessageType.PROGRESS) {
          this.emit('progress', message.payload);
          return;
        }

        // Handle results and errors
        const callback = this.messageCallbacks.get(message.id);
        if (callback) {
          clearTimeout(callback.timer);
          this.messageCallbacks.delete(message.id);

          if (message.type === MessageType.ERROR) {
            callback.reject(new Error(message.payload.message));
          } else {
            callback.resolve(message.payload);
          }
        }

        // Emit message event
        this.emit('message', message);
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });
  }

  /**
   * Send a message to the Python server
   * @param type Message type
   * @param payload Message payload
   * @returns Promise resolving to the response
   */
  async sendMessage(type: MessageType, payload: any): Promise<any> {
    if (!this.isConnected || !this.client) {
      throw new Error('Not connected to Python WebSocket server');
    }

    return new Promise((resolve, reject) => {
      // Generate a unique message ID
      const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);

      // Create message
      const message: CommunicationMessage = {
        type,
        id,
        payload,
        timestamp: Date.now()
      };

      // Set up timeout
      const timer = setTimeout(() => {
        this.messageCallbacks.delete(id);
        reject(new Error(`Message ${id} timed out after ${this.options.timeout}ms`));
      }, this.options.timeout);

      // Store callback
      this.messageCallbacks.set(id, { resolve, reject, timer });

      // Send message
      this.client.send(JSON.stringify(message));

      if (this.options.verbose) {
        console.log(`Sent message of type ${type} with ID ${id}`);
      }
    });
  }

  /**
   * Close the connection and stop the server
   */
  async close(): Promise<void> {
    // Send close message to server
    if (this.isConnected && this.client) {
      try {
        await this.sendMessage(MessageType.CLOSE, {});
      } catch (error) {
        console.error('Error sending close message:', error);
      }
    }

    // Close client
    if (this.client) {
      this.client.close();
      this.client = null;
    }

    // Close server
    if (this.server) {
      this.server.close();
      this.server = null;
    }

    // Kill Python process
    if (this.pythonProcess) {
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }

    this.isServerRunning = false;
    this.isConnected = false;

    if (this.options.verbose) {
      console.log('WebSocket communicator closed');
    }
  }

  /**
   * Evolve a solution using the hybrid approach
   * @param candidates Initial candidate solutions
   * @param constraints Constraints for solution validation
   * @param fitnessFunction Function to evaluate solution fitness
   * @param recursionRounds Number of recursive thinking rounds
   * @returns Promise resolving to the hybrid solution
   */
  async evolve(
    candidates: string[],
    constraints: any[],
    // Placeholder for fitness function - we'll handle this specially
    fitnessCallback: string,
    recursionRounds: number = 2
  ): Promise<any> {
    try {
      const result = await this.sendMessage(MessageType.EVOLVE, {
        candidates,
        constraints,
        fitness_function: fitnessCallback,
        recursion_rounds: recursionRounds
      });

      return result;
    } catch (error) {
      throw new Error(`Evolution failed: ${error.message}`);
    }
  }

  /**
   * Refine a solution using recursive thinking
   * @param solution Solution to refine
   * @param constraints Constraints for solution validation
   * @returns Promise resolving to the refined solution
   */
  async refine(solution: string, constraints: any[] = []): Promise<any> {
    try {
      const result = await this.sendMessage(MessageType.REFINE, {
        solution,
        constraints
      });

      return result;
    } catch (error) {
      throw new Error(`Refinement failed: ${error.message}`);
    }
  }

  /**
   * Evaluate solutions using the fitness function
   * @param solutions Solutions to evaluate
   * @param fitnessCallback Callback for fitness evaluation
   * @returns Promise resolving to evaluated solutions
   */
  async evaluate(solutions: string[], fitnessCallback: string): Promise<any> {
    try {
      const result = await this.sendMessage(MessageType.EVALUATE, {
        solutions,
        fitness_function: fitnessCallback
      });

      return result;
    } catch (error) {
      throw new Error(`Evaluation failed: ${error.message}`);
    }
  }
}