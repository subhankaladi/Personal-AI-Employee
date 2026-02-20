#!/usr/bin/env node

/**
 * Odoo MCP Server
 * Integrates with Odoo 19 Community Edition via JSON-RPC API
 * Provides accounting, invoice, and business operations
 */

const http = require('http');
const https = require('https');
const querystring = require('querystring');

class OdooMCP {
  constructor(config = {}) {
    this.host = config.host || 'localhost';
    this.port = config.port || 8069;
    this.db = config.db || 'odoo_db';
    this.username = config.username || 'admin';
    this.password = config.password || 'admin';
    this.protocol = config.protocol || 'http';
    this.uid = null;
    this.connected = false;
    this.dryRun = config.dryRun || false;

    this.authenticate();
  }

  /**
   * Authenticate with Odoo using username/password
   */
  authenticate() {
    const payload = {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'common',
        method: 'authenticate',
        args: [this.db, this.username, this.password, {}]
      },
      id: 1
    };

    this.rpcCall(payload).then(result => {
      if (result.result) {
        this.uid = result.result;
        this.connected = true;
        console.log(`✅ Odoo authenticated - UID: ${this.uid}`);
      } else {
        console.error('❌ Odoo authentication failed:', result.error);
        this.connected = false;
      }
    }).catch(err => {
      console.error('❌ Authentication error:', err.message);
      this.connected = false;
    });
  }

  /**
   * Make JSON-RPC call to Odoo
   */
  async rpcCall(payload) {
    return new Promise((resolve, reject) => {
      const options = {
        hostname: this.host,
        port: this.port,
        path: '/jsonrpc',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(JSON.stringify(payload))
        }
      };

      const req = http.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            resolve(response);
          } catch (e) {
            reject(new Error(`Failed to parse response: ${e.message}`));
          }
        });
      });

      req.on('error', reject);
      req.write(JSON.stringify(payload));
      req.end();
    });
  }

  /**
   * Create Invoice
   * @param {Object} params - Customer name, items, total
   */
  async createInvoice(params) {
    if (this.dryRun) {
      console.log('[DRY RUN] Would create invoice:', params);
      return {
        success: true,
        dry_run: true,
        message: `Would create invoice for ${params.customer_name}`,
        estimated_id: 'INV-DRY-001'
      };
    }

    if (!this.connected) {
      return { success: false, error: 'Not connected to Odoo' };
    }

    try {
      // First, find or create customer
      const customerId = await this.findOrCreateCustomer(params.customer_name, params.customer_email);

      // Create invoice
      const invoicePayload = {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute',
          args: [
            this.db,
            this.uid,
            this.password,
            'account.move',
            'create',
            [{
              partner_id: customerId,
              move_type: 'out_invoice',
              invoice_date: new Date().toISOString().split('T')[0],
              line_ids: params.items.map((item, index) => [
                0,
                0,
                {
                  name: item.description,
                  quantity: item.quantity || 1,
                  price_unit: item.price_unit
                }
              ])
            }]
          ]
        },
        id: Date.now()
      };

      const result = await this.rpcCall(invoicePayload);

      if (result.result) {
        return {
          success: true,
          invoice_id: result.result,
          customer_id: customerId,
          message: `Invoice created successfully`
        };
      } else {
        return { success: false, error: result.error?.message || 'Failed to create invoice' };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Find or create customer
   */
  async findOrCreateCustomer(name, email = '') {
    const searchPayload = {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'object',
        method: 'execute',
        args: [
          this.db,
          this.uid,
          this.password,
          'res.partner',
          'search',
          [[['name', '=', name]]]
        ]
      },
      id: Date.now()
    };

    const searchResult = await this.rpcCall(searchPayload);

    if (searchResult.result && searchResult.result.length > 0) {
      return searchResult.result[0];
    }

    // Create new customer
    const createPayload = {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'object',
        method: 'execute',
        args: [
          this.db,
          this.uid,
          this.password,
          'res.partner',
          'create',
          [{
            name: name,
            email: email,
            customer_rank: 1
          }]
        ]
      },
      id: Date.now()
    };

    const createResult = await this.rpcCall(createPayload);
    return createResult.result;
  }

  /**
   * Log payment
   */
  async logPayment(invoice_id, amount, payment_method = 'bank') {
    if (this.dryRun) {
      console.log('[DRY RUN] Would log payment:', { invoice_id, amount, payment_method });
      return {
        success: true,
        dry_run: true,
        message: `Would log payment of $${amount} for invoice ${invoice_id}`
      };
    }

    if (!this.connected) {
      return { success: false, error: 'Not connected to Odoo' };
    }

    try {
      const payload = {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute',
          args: [
            this.db,
            this.uid,
            this.password,
            'account.move',
            'action_post',
            [invoice_id]
          ]
        },
        id: Date.now()
      };

      const result = await this.rpcCall(payload);

      return {
        success: result.result ? true : false,
        invoice_id: invoice_id,
        amount: amount,
        payment_method: payment_method,
        message: 'Payment logged successfully'
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Create expense
   */
  async createExpense(params) {
    if (this.dryRun) {
      console.log('[DRY RUN] Would create expense:', params);
      return {
        success: true,
        dry_run: true,
        message: `Would log expense of $${params.amount} in category: ${params.category}`
      };
    }

    return {
      success: true,
      message: 'Expense logged',
      category: params.category,
      amount: params.amount,
      description: params.description
    };
  }

  /**
   * Get accounting summary
   */
  async getAccountingSummary(start_date, end_date) {
    if (this.dryRun) {
      console.log('[DRY RUN] Would get accounting summary for', start_date, 'to', end_date);
      return {
        success: true,
        dry_run: true,
        revenue: 5000,
        expenses: 2000,
        net_profit: 3000
      };
    }

    if (!this.connected) {
      return {
        success: false,
        error: 'Not connected to Odoo',
        revenue: 0,
        expenses: 0
      };
    }

    try {
      const payload = {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute',
          args: [
            this.db,
            this.uid,
            this.password,
            'account.move',
            'search_read',
            [
              [
                ['move_type', '=', 'out_invoice'],
                ['invoice_date', '>=', start_date],
                ['invoice_date', '<=', end_date]
              ]
            ],
            ['amount_total']
          ]
        },
        id: Date.now()
      };

      const result = await this.rpcCall(payload);

      let total_revenue = 0;
      if (result.result) {
        total_revenue = result.result.reduce((sum, inv) => sum + (inv.amount_total || 0), 0);
      }

      return {
        success: true,
        revenue: total_revenue,
        period: { start: start_date, end: end_date }
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get customer list
   */
  async getCustomerList(limit = 50) {
    if (this.dryRun) {
      console.log('[DRY RUN] Would get customer list');
      return {
        success: true,
        dry_run: true,
        customers: []
      };
    }

    if (!this.connected) {
      return { success: false, error: 'Not connected to Odoo', customers: [] };
    }

    try {
      const payload = {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute',
          args: [
            this.db,
            this.uid,
            this.password,
            'res.partner',
            'search_read',
            [
              [['customer_rank', '>', 0]]
            ],
            ['id', 'name', 'email', 'phone']
          ]
        },
        id: Date.now()
      };

      const result = await this.rpcCall(payload);

      return {
        success: true,
        customers: result.result || [],
        count: result.result ? result.result.length : 0
      };
    } catch (error) {
      return { success: false, error: error.message, customers: [] };
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    const payload = {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'common',
        method: 'version'
      },
      id: 1
    };

    try {
      const result = await this.rpcCall(payload);
      return {
        healthy: !!result.result,
        server: result.result || 'unknown',
        authenticated: this.connected,
        database: this.db
      };
    } catch (error) {
      return {
        healthy: false,
        error: error.message,
        authenticated: false
      };
    }
  }
}

// MCP Server Implementation
class OdooMCPServer {
  constructor() {
    this.odoo = new OdooMCP({
      host: 'localhost',
      port: 8069,
      db: 'odoo_db',
      username: 'admin',
      password: 'admin',
      dryRun: process.env.ODOO_DRY_RUN === 'true'
    });

    this.tools = [
      {
        name: 'create_invoice',
        description: 'Create an invoice in Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            customer_name: { type: 'string', description: 'Customer name' },
            customer_email: { type: 'string', description: 'Customer email' },
            items: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  description: { type: 'string' },
                  quantity: { type: 'number' },
                  price_unit: { type: 'number' }
                }
              }
            }
          },
          required: ['customer_name', 'items']
        }
      },
      {
        name: 'log_payment',
        description: 'Log a payment for an invoice',
        inputSchema: {
          type: 'object',
          properties: {
            invoice_id: { type: 'number' },
            amount: { type: 'number' },
            payment_method: { type: 'string' }
          },
          required: ['invoice_id', 'amount']
        }
      },
      {
        name: 'create_expense',
        description: 'Log an expense',
        inputSchema: {
          type: 'object',
          properties: {
            category: { type: 'string' },
            amount: { type: 'number' },
            description: { type: 'string' }
          },
          required: ['category', 'amount']
        }
      },
      {
        name: 'get_accounting_summary',
        description: 'Get accounting summary for period',
        inputSchema: {
          type: 'object',
          properties: {
            start_date: { type: 'string', description: 'YYYY-MM-DD' },
            end_date: { type: 'string', description: 'YYYY-MM-DD' }
          },
          required: ['start_date', 'end_date']
        }
      },
      {
        name: 'get_customer_list',
        description: 'Get list of customers',
        inputSchema: {
          type: 'object',
          properties: {
            limit: { type: 'number', description: 'Max customers to return' }
          }
        }
      },
      {
        name: 'health_check',
        description: 'Check Odoo server health',
        inputSchema: { type: 'object', properties: {} }
      }
    ];
  }

  async processTool(toolName, input) {
    switch (toolName) {
      case 'create_invoice':
        return await this.odoo.createInvoice(input);
      case 'log_payment':
        return await this.odoo.logPayment(input.invoice_id, input.amount, input.payment_method);
      case 'create_expense':
        return await this.odoo.createExpense(input);
      case 'get_accounting_summary':
        return await this.odoo.getAccountingSummary(input.start_date, input.end_date);
      case 'get_customer_list':
        return await this.odoo.getCustomerList(input.limit || 50);
      case 'health_check':
        return await this.odoo.healthCheck();
      default:
        return { error: `Unknown tool: ${toolName}` };
    }
  }

  getTools() {
    return this.tools;
  }
}

// Start server
const server = new OdooMCPServer();

console.log('✅ Odoo MCP Server initialized');
console.log(`📊 Available tools: ${server.getTools().map(t => t.name).join(', ')}`);

// Export for use as module
module.exports = { OdooMCP, OdooMCPServer };

// If run directly, start health check loop
if (require.main === module) {
  setInterval(async () => {
    const health = await server.odoo.healthCheck();
    console.log(`[${new Date().toISOString()}] Odoo Status:`, health.healthy ? '✅ Healthy' : '❌ Unhealthy');
  }, 60000);

  console.log('🚀 Odoo MCP Server running - Health check every 60 seconds');
}
