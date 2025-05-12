/**
 * Tool Types
 * 
 * Defines the types and interfaces for the tool system.
 * Tools are capabilities that agents can expose and invoke.
 */

/**
 * Type for tool parameters.
 */
export type ToolParameters = Record<string, any>;

/**
 * Type for tool response.
 */
export type ToolResponse = any;

/**
 * Interface for a tool that can be registered with an agent.
 */
export interface Tool {
  /**
   * Gets the unique identifier for this tool.
   * 
   * @returns The tool ID
   */
  getId(): string;
  
  /**
   * Gets the name of this tool.
   * 
   * @returns The tool name
   */
  getName(): string;
  
  /**
   * Gets the description of this tool.
   * 
   * @returns The tool description
   */
  getDescription(): string;
  
  /**
   * Gets the parameter schema for this tool.
   * 
   * @returns The parameter schema
   */
  getParameterSchema(): Record<string, any>;
  
  /**
   * Gets the response schema for this tool.
   * 
   * @returns The response schema
   */
  getResponseSchema(): Record<string, any>;
  
  /**
   * Executes this tool with the given parameters.
   * 
   * @param parameters The parameters to use for execution
   * @returns A promise that resolves to the tool response
   */
  execute(parameters: ToolParameters): Promise<ToolResponse>;
}

/**
 * Base class for implementing tools.
 */
export abstract class BaseTool implements Tool {
  protected id: string;
  protected name: string;
  protected description: string;
  protected parameterSchema: Record<string, any>;
  protected responseSchema: Record<string, any>;
  
  /**
   * Creates a new BaseTool instance.
   * 
   * @param id Tool ID
   * @param name Tool name
   * @param description Tool description
   * @param parameterSchema Parameter schema
   * @param responseSchema Response schema
   */
  constructor(
    id: string,
    name: string,
    description: string,
    parameterSchema: Record<string, any>,
    responseSchema: Record<string, any>
  ) {
    this.id = id;
    this.name = name;
    this.description = description;
    this.parameterSchema = parameterSchema;
    this.responseSchema = responseSchema;
  }
  
  /**
   * Gets the unique identifier for this tool.
   * 
   * @returns The tool ID
   */
  getId(): string {
    return this.id;
  }
  
  /**
   * Gets the name of this tool.
   * 
   * @returns The tool name
   */
  getName(): string {
    return this.name;
  }
  
  /**
   * Gets the description of this tool.
   * 
   * @returns The tool description
   */
  getDescription(): string {
    return this.description;
  }
  
  /**
   * Gets the parameter schema for this tool.
   * 
   * @returns The parameter schema
   */
  getParameterSchema(): Record<string, any> {
    return this.parameterSchema;
  }
  
  /**
   * Gets the response schema for this tool.
   * 
   * @returns The response schema
   */
  getResponseSchema(): Record<string, any> {
    return this.responseSchema;
  }
  
  /**
   * Validates the parameters against the parameter schema.
   * 
   * @param parameters The parameters to validate
   * @returns True if the parameters are valid, false otherwise
   */
  validateParameters(parameters: ToolParameters): boolean {
    // Basic validation - check that required parameters are present
    // In a real implementation, this would use a schema validation library
    
    const required = this.parameterSchema.required || [];
    for (const param of required) {
      if (!(param in parameters)) {
        console.error(`Missing required parameter: ${param}`);
        return false;
      }
    }
    
    return true;
  }
  
  /**
   * Executes this tool with the given parameters.
   * 
   * @param parameters The parameters to use for execution
   * @returns A promise that resolves to the tool response
   */
  async execute(parameters: ToolParameters): Promise<ToolResponse> {
    // Validate parameters
    if (!this.validateParameters(parameters)) {
      throw new Error(`Invalid parameters for tool ${this.id}`);
    }
    
    // Execute the tool-specific implementation
    return await this.executeImpl(parameters);
  }
  
  /**
   * Implements the tool-specific execution logic.
   * Subclasses must override this method.
   * 
   * @param parameters The parameters to use for execution
   * @returns A promise that resolves to the tool response
   */
  protected abstract executeImpl(parameters: ToolParameters): Promise<ToolResponse>;
}