#!/usr/bin/env node
/**
 * AI Agency Authentication CLI
 * 
 * Command-line interface for authenticating with AI Agency domains
 */

const authModule = require('./auth_module');
const chalk = require('chalk');
const { program } = require('commander');

// Formatting helpers
const success = msg => console.log(chalk.green('✓ ') + msg);
const error = msg => console.log(chalk.red('✗ ') + msg);
const info = msg => console.log(chalk.blue('ℹ ') + msg);
const highlight = text => chalk.cyan(text);
const bold = text => chalk.bold(text);

// Format dates in a user-friendly way
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

/**
 * Login command
 */
async function login(domain, options) {
  info(`Starting authentication process${domain ? ` for ${highlight(domain)}` : ''}...`);
  
  const result = await authModule.startDeviceFlow(domain);
  
  if (result.success) {
    success(result.message);
    
    // Show next steps if not domain-specific
    if (!domain) {
      info('\nTo authorize for specific domains, run:');
      console.log(`  ${highlight('ai-agency auth request-domain <domain.ai>')}`);
    }
  } else {
    error(result.message);
    process.exit(1);
  }
}

/**
 * Status command
 */
function status(domain, options) {
  const status = authModule.checkStatus(domain);
  
  if (!status.authenticated) {
    info('Not authenticated.');
    info('Run the following command to login:');
    console.log(`  ${highlight('ai-agency auth login')}`);
    return;
  }
  
  success('You are authenticated to AI Agency CLI');
  
  // Show token expiration
  if (status.expires_at) {
    info(`Token expires at: ${formatDate(status.expires_at)}`);
  }
  
  // Show last used
  if (status.last_used) {
    info(`Last used: ${formatDate(status.last_used)}`);
  }
  
  // Domain-specific status
  if (domain) {
    if (status.domain_authorized) {
      success(`Authorized for domain: ${highlight(domain)}`);
    } else {
      error(`Not authorized for domain: ${highlight(domain)}`);
      info('Run the following command to request domain access:');
      console.log(`  ${highlight(`ai-agency auth request-domain ${domain}`)}`);
    }
    return;
  }
  
  // Show authorized domains
  if (status.authorized_domains && status.authorized_domains.length > 0) {
    info('\nAuthorized domains:');
    status.authorized_domains.forEach(domain => {
      console.log(`  ${highlight(domain.domain)}`);
      console.log(`    Scopes: ${domain.scopes.join(', ')}`);
      console.log(`    Expires: ${formatDate(domain.expires_at)}`);
    });
  } else {
    info('\nNo domain authorizations.');
    info('Run the following command to request domain access:');
    console.log(`  ${highlight('ai-agency auth request-domain <domain.ai>')}`);
  }
}

/**
 * Request domain authorization
 */
async function requestDomain(domain, options) {
  if (!domain) {
    error('Domain name is required');
    console.log(`  ${highlight('ai-agency auth request-domain <domain.ai>')}`);
    return;
  }
  
  info(`Requesting authorization for domain: ${highlight(domain)}...`);
  
  const result = await authModule.requestDomainAuthorization(domain);
  
  if (result.success) {
    success(result.message);
  } else {
    error(result.message);
    
    // If not authenticated, show login instructions
    if (result.message.includes('Not authenticated')) {
      info('Run the following command to login first:');
      console.log(`  ${highlight('ai-agency auth login')}`);
    }
    
    process.exit(1);
  }
}

/**
 * List authorized domains
 */
function listDomains(options) {
  const domains = authModule.getAuthorizedDomains();
  
  if (domains.length === 0) {
    info('No authorized domains.');
    info('Run the following command to request domain access:');
    console.log(`  ${highlight('ai-agency auth request-domain <domain.ai>')}`);
    return;
  }
  
  success(`You have access to ${domains.length} domains:`);
  
  // Group domains by category
  const categories = {};
  
  domains.forEach(domain => {
    let category = 'Other';
    
    // Determine category from domain name
    if (domain.domain.includes('cber') || domain.domain.includes('cder') || 
        domain.domain.includes('hrsa') || domain.domain.includes('niddk') ||
        domain.domain.includes('crohns') || domain.domain.includes('nccih') ||
        domain.domain.includes('oash') || domain.domain.includes('phm')) {
      category = 'Healthcare';
    } else if (domain.domain.includes('aphis') || domain.domain.includes('nhtsa') ||
               domain.domain.includes('cpsc') || domain.domain.includes('bsee') ||
               domain.domain.includes('ntsb')) {
      category = 'Safety';
    } else if (domain.domain.includes('fhfa') || domain.domain.includes('usitc') ||
               domain.domain.includes('ustda') || domain.domain.includes('usich')) {
      category = 'Economic';
    } else if (domain.domain.includes('doed') || domain.domain.includes('nslp') ||
               domain.domain.includes('cnpp')) {
      category = 'Education';
    } else if (domain.domain.includes('hsin') || domain.domain.includes('csfc') ||
               domain.domain.includes('ondcp')) {
      category = 'Security';
    }
    
    if (!categories[category]) {
      categories[category] = [];
    }
    
    categories[category].push(domain);
  });
  
  // Display domains by category
  Object.keys(categories).sort().forEach(category => {
    console.log(`\n${bold(category)} Domains:`);
    
    categories[category].forEach(domain => {
      console.log(`  ${highlight(domain.domain)}`);
      console.log(`    Scopes: ${domain.scopes.join(', ')}`);
      console.log(`    Expires: ${formatDate(domain.expires_at)}`);
    });
  });
}

/**
 * Logout command
 */
async function logout(options) {
  info('Logging out from AI Agency CLI...');
  
  const result = await authModule.logout();
  
  if (result.success) {
    success(result.message);
  } else {
    error(result.message);
    process.exit(1);
  }
}

// Configure CLI
program
  .name('ai-agency auth')
  .description('AI Agency authentication commands')
  .version('1.0.0');

program
  .command('login')
  .description('Authenticate with AI Agency web interface')
  .argument('[domain]', 'Optional domain to request authorization for')
  .action(login);

program
  .command('status')
  .description('Check authentication status')
  .argument('[domain]', 'Optional domain to check authorization for')
  .action(status);

program
  .command('request-domain')
  .description('Request authorization for a specific domain')
  .argument('<domain>', 'Domain to request authorization for')
  .action(requestDomain);

program
  .command('domains')
  .description('List authorized domains')
  .action(listDomains);

program
  .command('logout')
  .description('Logout and revoke access tokens')
  .action(logout);

// Execute CLI
program.parse();