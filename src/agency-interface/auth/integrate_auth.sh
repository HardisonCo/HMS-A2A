#!/bin/bash
# Integration script for the authentication module
# Adds authentication capabilities to the AI agency CLI

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
AUTH_MODULE_DIR="$SCRIPT_DIR"
INTERFACE_DIR="$SCRIPT_DIR/.."

# Ensure auth directory exists
mkdir -p "$AUTH_MODULE_DIR/web"
mkdir -p "$HOME/.codex/auth"

# Create a symlink to auth_cli.js in the bin directory
mkdir -p "$INTERFACE_DIR/bin"
ln -sf "$AUTH_MODULE_DIR/auth_cli.js" "$INTERFACE_DIR/bin/ai-agency-auth"
chmod +x "$AUTH_MODULE_DIR/auth_cli.js"

# Install required dependencies
echo "Installing required dependencies..."
cd "$INTERFACE_DIR" 
npm install --save axios open commander chalk crypto-js

# Create package.json if it doesn't exist
if [ ! -f "$INTERFACE_DIR/package.json" ]; then
  cat > "$INTERFACE_DIR/package.json" << 'EOF'
{
  "name": "ai-agency-interface",
  "version": "1.0.0",
  "description": "AI Agency Domain Interface CLI",
  "bin": {
    "ai-agency": "./bin/ai-agency",
    "ai-agency-auth": "./bin/ai-agency-auth"
  },
  "scripts": {
    "auth": "node ./auth/auth_cli.js",
    "start": "node ./bin/ai-agency"
  },
  "author": "",
  "license": "MIT",
  "dependencies": {
    "axios": "^1.6.2",
    "chalk": "^4.1.2",
    "commander": "^11.1.0",
    "crypto-js": "^4.2.0",
    "open": "^8.4.2"
  }
}
EOF
fi

# Create main CLI launcher if it doesn't exist
if [ ! -f "$INTERFACE_DIR/bin/ai-agency" ]; then
  cat > "$INTERFACE_DIR/bin/ai-agency" << 'EOF'
#!/usr/bin/env node

const { program } = require('commander');
const chalk = require('chalk');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configure CLI
program
  .name('ai-agency')
  .description('AI Agency Domain Interface CLI')
  .version('1.0.0');

// Auth command
program
  .command('auth')
  .description('Authentication commands')
  .argument('[cmd]', 'Auth command: login, status, request-domain, domains, logout')
  .argument('[options...]', 'Command options')
  .action((cmd, options) => {
    // Run auth CLI with the provided arguments
    const authCliPath = path.join(__dirname, 'ai-agency-auth');
    const args = [cmd, ...options].filter(Boolean);
    
    const authProcess = spawn(authCliPath, args, { 
      stdio: 'inherit',
      shell: process.platform === 'win32'
    });
    
    authProcess.on('error', (err) => {
      console.error(chalk.red(`Error executing auth command: ${err.message}`));
      process.exit(1);
    });
  });

// Launch command
program
  .command('launch')
  .description('Launch an AI agency domain interface')
  .argument('[domain]', 'Domain to launch')
  .option('-d, --demo', 'Run in demo mode')
  .action((domain, options) => {
    // Path to the launch script
    const launchScriptPath = path.join(__dirname, '..', 'enhanced_launch_ai_agency.sh');
    
    // Check for auth if domain is specified
    if (domain) {
      const authModule = require('../auth/auth_module');
      
      // Check if authenticated and authorized for domain
      const status = authModule.checkStatus(domain);
      
      if (!status.authenticated) {
        console.log(chalk.yellow('You need to authenticate before launching a domain interface'));
        console.log(chalk.cyan(`Run: ai-agency auth login`));
        process.exit(1);
      }
      
      if (domain && !status.domain_authorized) {
        console.log(chalk.yellow(`You are not authorized for domain: ${domain}`));
        console.log(chalk.cyan(`Run: ai-agency auth request-domain ${domain}`));
        process.exit(1);
      }
      
      console.log(chalk.green(`✓ Authenticated and authorized for ${domain}`));
    }
    
    // Check if the launch script exists
    if (!fs.existsSync(launchScriptPath)) {
      console.error(chalk.red(`Launch script not found: ${launchScriptPath}`));
      process.exit(1);
    }
    
    // Build the command arguments
    const args = [];
    if (domain) args.push(domain);
    if (options.demo) args.push('--demo');
    
    // Launch the script
    const launchProcess = spawn(launchScriptPath, args, { 
      stdio: 'inherit',
      shell: true
    });
    
    launchProcess.on('error', (err) => {
      console.error(chalk.red(`Error launching agency interface: ${err.message}`));
      process.exit(1);
    });
  });

// Demo command
program
  .command('demo')
  .description('Run the AI agency domain demonstration')
  .action(() => {
    const demoScriptPath = path.join(__dirname, '..', 'enhanced_demo.sh');
    
    // Check if the demo script exists
    if (!fs.existsSync(demoScriptPath)) {
      console.error(chalk.red(`Demo script not found: ${demoScriptPath}`));
      process.exit(1);
    }
    
    // Run the demo script
    const demoProcess = spawn(demoScriptPath, [], { 
      stdio: 'inherit',
      shell: true
    });
    
    demoProcess.on('error', (err) => {
      console.error(chalk.red(`Error running demonstration: ${err.message}`));
      process.exit(1);
    });
  });

// Execute CLI
program.parse();
EOF

  chmod +x "$INTERFACE_DIR/bin/ai-agency"
fi

# Create a simpler launcher script
cat > "$INTERFACE_DIR/ai-agency" << 'EOF'
#!/bin/bash
# AI Agency CLI launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CLI_PATH="$SCRIPT_DIR/bin/ai-agency"

# Make sure CLI is executable
chmod +x "$CLI_PATH"

# Run the CLI with provided arguments
"$CLI_PATH" "$@"
EOF

chmod +x "$INTERFACE_DIR/ai-agency"

# Start a local web server for the auth mock page
echo "Setting up mock web authentication page..."
mkdir -p "$AUTH_MODULE_DIR/web"

# Create a simple server script to serve the auth page
cat > "$AUTH_MODULE_DIR/serve_auth_page.js" << 'EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8000;
const WEB_DIR = path.join(__dirname, 'web');

const server = http.createServer((req, res) => {
  let filePath = path.join(WEB_DIR, req.url === '/' ? 'index.html' : req.url);
  
  const extname = path.extname(filePath);
  let contentType = 'text/html';
  
  switch(extname) {
    case '.js':
      contentType = 'text/javascript';
      break;
    case '.css':
      contentType = 'text/css';
      break;
    case '.json':
      contentType = 'application/json';
      break;
    case '.png':
      contentType = 'image/png';
      break;
    case '.jpg':
      contentType = 'image/jpg';
      break;
  }
  
  fs.readFile(filePath, (err, content) => {
    if(err) {
      if(err.code === 'ENOENT') {
        // Page not found
        fs.readFile(path.join(WEB_DIR, '404.html'), (err, content) => {
          res.writeHead(404, { 'Content-Type': 'text/html' });
          res.end(content, 'utf8');
        });
      } else {
        // Server error
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`);
      }
    } else {
      // Success
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf8');
    }
  });
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
  console.log(`Open your browser to view the auth page`);
});
EOF

# Create script to start the auth server
cat > "$AUTH_MODULE_DIR/start_auth_server.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
node "$SCRIPT_DIR/serve_auth_page.js"
EOF
chmod +x "$AUTH_MODULE_DIR/start_auth_server.sh"

# Create documentation for the auth module
cat > "$AUTH_MODULE_DIR/README.md" << 'EOF'
# AI Agency Authentication Module

This module provides web-based authentication for the AI Agency CLI, similar to GitHub's approach. It allows users to authenticate with domain-specific admin portals directly from the command line.

## Features

- Device authorization flow with web-based authentication
- Domain-specific authorization
- Secure token storage
- Token refresh and revocation
- Command-line interface for authentication management

## Usage

```bash
# Login to AI Agency
ai-agency auth login

# Login and request domain authorization in one step
ai-agency auth login <domain>

# Check authentication status
ai-agency auth status

# Check domain authorization status
ai-agency auth status <domain>

# Request authorization for a specific domain
ai-agency auth request-domain <domain>

# List authorized domains
ai-agency auth domains

# Logout and revoke tokens
ai-agency auth logout
```

## Authentication Flow

1. Run `ai-agency auth login`
2. The CLI generates a device code and displays a verification URL
3. Open the URL in your browser (or it may open automatically)
4. Enter the displayed code to link your browser session
5. Sign in with your HMS-API credentials
6. Authorize the domains you want to access
7. Return to the CLI, which should now be authenticated

## Integration with AI Agency Interface

The authentication module is integrated with the AI Agency Interface. When launching a domain-specific interface, the CLI will check if you are authenticated and authorized for that domain.

```bash
# Launch a domain-specific interface (checks auth)
ai-agency launch <domain>
```

If you are not authenticated or authorized, the CLI will prompt you to authenticate first.

## Testing

For testing purposes, a mock web authentication page is included. To start the mock auth server:

```bash
./auth/start_auth_server.sh
```

Then open http://localhost:8000/ in your browser to view the mock auth page.
EOF

# Update README with auth module information
if [ -f "$INTERFACE_DIR/AI_DOMAIN_USAGE_GUIDE.md" ]; then
  # Add auth section to the existing guide
  sed -i.bak '/^## Using the Agency Interface/i \
## Authentication\n\
\n\
The AI Domain Interface now supports web-based authentication similar to GitHub:\n\
\n\
```bash\n\
# Login to AI Agency\n\
./ai-agency auth login\n\
\n\
# Login with domain authorization\n\
./ai-agency auth login <domain.ai>\n\
\n\
# Check authentication status\n\
./ai-agency auth status\n\
\n\
# Request domain authorization\n\
./ai-agency auth request-domain <domain.ai>\n\
\n\
# List authorized domains\n\
./ai-agency auth domains\n\
\n\
# Logout\n\
./ai-agency auth logout\n\
```\n\
\n\
When launching a domain-specific interface, the CLI will automatically check if you are authenticated and authorized for that domain.\n\
\n\
' "$INTERFACE_DIR/AI_DOMAIN_USAGE_GUIDE.md"
fi

echo "Authentication module has been integrated with AI Agency CLI"
echo
echo "To enable authentication for your agency interface, run:"
echo "  cd $INTERFACE_DIR"
echo "  npm install"
echo
echo "To test the auth module, run:"
echo "  ./ai-agency auth login"
echo
echo "To start the mock auth server, run:"
echo "  ./auth/start_auth_server.sh"
echo