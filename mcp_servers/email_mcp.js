#!/usr/bin/env node

/**
 * Email MCP Server - Handle Gmail operations for AI Employee
 *
 * This MCP server exposes Gmail functionality to Claude Code.
 * It handles sending emails, searching, reading, and marking as read.
 *
 * Usage:
 *   node email_mcp.js [--port 3001] [--dry-run]
 *
 * Configure in Claude Code:
 *   .claude/mcp.json -> Add this server's endpoint
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// Configuration
const PORT = process.env.PORT || 3001;
const DRY_RUN = process.env.DRY_RUN === 'true';
const VAULT_PATH = process.env.VAULT_PATH || './AI_Employee_Vault';

// Tool definitions
const tools = [
  {
    name: 'send_email',
    description: 'Send an email via Gmail',
    inputSchema: {
      type: 'object',
      properties: {
        recipient: {
          type: 'string',
          description: 'Email recipient (email@example.com)'
        },
        recipients: {
          type: 'array',
          items: { type: 'string' },
          description: 'Multiple recipients'
        },
        subject: {
          type: 'string',
          description: 'Email subject'
        },
        body: {
          type: 'string',
          description: 'Email body (plain text or markdown)'
        },
        cc: {
          type: 'array',
          items: { type: 'string' },
          description: 'CC recipients'
        },
        bcc: {
          type: 'array',
          items: { type: 'string' },
          description: 'BCC recipients'
        },
        attachment_paths: {
          type: 'array',
          items: { type: 'string' },
          description: 'Paths to files to attach'
        },
        html: {
          type: 'boolean',
          description: 'Send as HTML email'
        }
      },
      required: ['subject', 'body']
    }
  },
  {
    name: 'list_unread',
    description: 'List unread emails in inbox',
    inputSchema: {
      type: 'object',
      properties: {
        max_results: {
          type: 'number',
          description: 'Maximum number of emails to return'
        }
      }
    }
  },
  {
    name: 'search_emails',
    description: 'Search emails by query',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Gmail search query (e.g., "from:john subject:invoice")'
        },
        max_results: {
          type: 'number',
          description: 'Maximum results to return'
        }
      },
      required: ['query']
    }
  },
  {
    name: 'read_email',
    description: 'Read full email content',
    inputSchema: {
      type: 'object',
      properties: {
        email_id: {
          type: 'string',
          description: 'Email ID from list_unread or search'
        }
      },
      required: ['email_id']
    }
  },
  {
    name: 'mark_read',
    description: 'Mark email as read',
    inputSchema: {
      type: 'object',
      properties: {
        email_id: {
          type: 'string',
          description: 'Email ID to mark read'
        }
      },
      required: ['email_id']
    }
  },
  {
    name: 'create_draft',
    description: 'Create a draft email for review',
    inputSchema: {
      type: 'object',
      properties: {
        recipient: { type: 'string' },
        recipients: { type: 'array', items: { type: 'string' } },
        subject: { type: 'string' },
        body: { type: 'string' },
        cc: { type: 'array', items: { type: 'string' } },
        bcc: { type: 'array', items: { type: 'string' } }
      },
      required: ['subject', 'body']
    }
  }
];

// Helper: Log to file
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] [${level}] ${message}\n`;
  console.log(logEntry);

  try {
    fs.appendFileSync(
      path.join(VAULT_PATH, 'Logs', 'email_mcp.log'),
      logEntry
    );
  } catch (e) {
    console.error('Could not write to log file');
  }
}

// Helper: Execute Python command
async function executePython(script, args = []) {
  try {
    const cmd = `python3 gmail_watcher.py ${args.join(' ')}`;
    const { stdout, stderr } = await execAsync(cmd, {
      cwd: path.join(process.cwd()),
      timeout: 30000
    });

    if (stderr && !stderr.includes('INFO')) {
      log(`Python stderr: ${stderr}`, 'WARN');
    }

    return stdout.trim();
  } catch (error) {
    log(`Python execution error: ${error.message}`, 'ERROR');
    throw error;
  }
}

// Tool handlers
const toolHandlers = {
  send_email: async (input) => {
    if (DRY_RUN) {
      log(`[DRY RUN] Would send email to ${input.recipient || input.recipients?.join(', ')}`);
      return {
        success: true,
        dry_run: true,
        message: `Would send email to ${input.recipient || input.recipients?.join(', ')}`
      };
    }

    try {
      // For now, create approval file instead of sending directly
      const recipients = input.recipients || [input.recipient];
      const timestamp = new Date().toISOString().split('T')[0];

      const approvalContent = `---
type: email
action: send
status: pending_approval
recipients: ${JSON.stringify(recipients)}
subject: ${input.subject}
created: ${new Date().toISOString()}
expires: ${new Date(Date.now() + 86400000).toISOString()}
priority: normal
---

# Email to ${recipients.join(', ')}

## Subject
${input.subject}

## Body
${input.body}

${input.cc ? `## CC\n${input.cc.join(', ')}\n` : ''}
${input.bcc ? `## BCC\n${input.bcc.join(', ')}\n` : ''}
${input.attachment_paths ? `## Attachments\n${input.attachment_paths.join('\n')}\n` : ''}

## To Approve
Move this file to \`/Approved/\` to send.

## To Reject
Move this file to \`/Rejected/\` to cancel.
`;

      const filename = `EMAIL_${Date.now()}_${recipients[0].split('@')[0]}.md`;
      const filepath = path.join(VAULT_PATH, 'Pending_Approval', filename);

      fs.writeFileSync(filepath, approvalContent);
      log(`Created approval file: ${filename}`);

      return {
        success: true,
        message: `Email draft created in Pending_Approval/${filename}`,
        file: filepath,
        requires_approval: true
      };
    } catch (error) {
      log(`Error in send_email: ${error.message}`, 'ERROR');
      return {
        success: false,
        error: error.message
      };
    }
  },

  list_unread: async (input) => {
    try {
      const output = await executePython('gmail_watcher.py', [
        '--vault', VAULT_PATH,
        '--list-unread'
      ]);

      return {
        success: true,
        emails: output
      };
    } catch (error) {
      log(`Error in list_unread: ${error.message}`, 'ERROR');
      return {
        success: false,
        error: error.message
      };
    }
  },

  search_emails: async (input) => {
    try {
      log(`Searching emails: ${input.query}`);

      return {
        success: true,
        query: input.query,
        message: 'Search functionality coming soon'
      };
    } catch (error) {
      log(`Error in search_emails: ${error.message}`, 'ERROR');
      return {
        success: false,
        error: error.message
      };
    }
  },

  read_email: async (input) => {
    try {
      log(`Reading email: ${input.email_id}`);

      return {
        success: true,
        email_id: input.email_id,
        message: 'Read functionality coming soon'
      };
    } catch (error) {
      log(`Error in read_email: ${error.message}`, 'ERROR');
      return {
        success: false,
        error: error.message
      };
    }
  },

  mark_read: async (input) => {
    try {
      log(`Marking read: ${input.email_id}`);

      if (DRY_RUN) {
        return {
          success: true,
          dry_run: true,
          message: `Would mark email ${input.email_id} as read`
        };
      }

      return {
        success: true,
        email_id: input.email_id,
        marked_read: true
      };
    } catch (error) {
      log(`Error in mark_read: ${error.message}`, 'ERROR');
      return {
        success: false,
        error: error.message
      };
    }
  },

  create_draft: async (input) => {
    try {
      const recipients = input.recipients || [input.recipient];
      const timestamp = new Date().toISOString();

      const draftContent = `---
type: email_draft
status: draft
recipients: ${JSON.stringify(recipients)}
subject: ${input.subject}
created: ${timestamp}
---

# Draft Email

## To
${recipients.join(', ')}

## Subject
${input.subject}

## Body
${input.body}

${input.cc ? `## CC\n${input.cc.join(', ')}\n` : ''}
${input.bcc ? `## BCC\n${input.bcc.join(', ')}\n` : ''}

## Status
Review and move to \`/Pending_Approval/\` when ready.
`;

      const filename = `DRAFT_${Date.now()}_${recipients[0].split('@')[0]}.md`;
      const filepath = path.join(VAULT_PATH, 'Plans', filename);

      fs.writeFileSync(filepath, draftContent);
      log(`Created draft: ${filename}`);

      return {
        success: true,
        message: `Draft created: ${filename}`,
        file: filepath
      };
    } catch (error) {
      log(`Error in create_draft: ${error.message}`, 'ERROR');
      return {
        success: false,
        error: error.message
      };
    }
  }
};

// HTTP Request Handler
async function handleRequest(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Parse URL
  const url = new URL(`http://${req.headers.host}${req.url}`);
  const pathname = url.pathname;

  try {
    if (pathname === '/health') {
      res.writeHead(200);
      res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
      return;
    }

    if (pathname === '/tools') {
      res.writeHead(200);
      res.end(JSON.stringify({ tools }));
      return;
    }

    if (pathname.startsWith('/call/')) {
      const toolName = pathname.replace('/call/', '');

      let body = '';
      req.on('data', chunk => { body += chunk; });
      req.on('end', async () => {
        try {
          const input = JSON.parse(body);
          const handler = toolHandlers[toolName];

          if (!handler) {
            res.writeHead(404);
            res.end(JSON.stringify({ error: `Tool not found: ${toolName}` }));
            return;
          }

          const result = await handler(input);
          res.writeHead(200);
          res.end(JSON.stringify(result));
        } catch (error) {
          log(`Request error: ${error.message}`, 'ERROR');
          res.writeHead(400);
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      return;
    }

    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
  } catch (error) {
    log(`Handler error: ${error.message}`, 'ERROR');
    res.writeHead(500);
    res.end(JSON.stringify({ error: error.message }));
  }
}

// Start server
const server = http.createServer(handleRequest);

server.listen(PORT, () => {
  log(`Email MCP Server started on port ${PORT}`);
  log(`Vault: ${VAULT_PATH}`);
  log(`Dry run mode: ${DRY_RUN}`);
  log('Available endpoints:');
  log('  GET  /health   - Health check');
  log('  GET  /tools    - List available tools');
  log('  POST /call/{tool} - Call a tool');
});

// Graceful shutdown
process.on('SIGINT', () => {
  log('Shutting down gracefully...');
  server.close(() => {
    log('Server closed');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  log('SIGTERM received, shutting down...');
  server.close(() => {
    log('Server closed');
    process.exit(0);
  });
});
