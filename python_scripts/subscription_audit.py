#!/usr/bin/env python3

"""
Subscription Audit Script
Analyzes recurring charges to identify unused services

Phase 3 Implementation
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SubscriptionAudit - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SubscriptionAudit:
    """
    Audit subscriptions and recurring charges
    Identifies unused services for cost optimization
    """

    # Pattern matching for known subscriptions
    SUBSCRIPTION_PATTERNS = {
        # SaaS
        'netflix': {'name': 'Netflix', 'category': 'Entertainment'},
        'spotify': {'name': 'Spotify', 'category': 'Entertainment'},
        'adobe': {'name': 'Adobe Creative Cloud', 'category': 'Software'},
        'notion': {'name': 'Notion', 'category': 'Productivity'},
        'slack': {'name': 'Slack', 'category': 'Communication'},
        'github': {'name': 'GitHub', 'category': 'Development'},
        'aws': {'name': 'AWS', 'category': 'Cloud'},
        'dropbox': {'name': 'Dropbox', 'category': 'Storage'},
        'icloud': {'name': 'iCloud+', 'category': 'Storage'},
        'google one': {'name': 'Google One', 'category': 'Storage'},
        'microsoft': {'name': 'Microsoft 365', 'category': 'Software'},
        'subscribestar': {'name': 'SubscribeStar', 'category': 'Creator'},
        'patreon': {'name': 'Patreon', 'category': 'Creator'},
        'atlassian': {'name': 'Atlassian', 'category': 'Development'},
        'figma': {'name': 'Figma', 'category': 'Design'},
        'sketch': {'name': 'Sketch', 'category': 'Design'},
        'getresponse': {'name': 'GetResponse', 'category': 'Marketing'},
        'mailchimp': {'name': 'Mailchimp', 'category': 'Marketing'},
        'stripe': {'name': 'Stripe', 'category': 'Payments'},
        'chatgpt': {'name': 'ChatGPT Plus', 'category': 'AI'},
    }

    def __init__(self, vault_path):
        """Initialize subscription audit"""
        self.vault_path = Path(vault_path)
        self.accounting_dir = self.vault_path / 'Accounting'
        self.alerts_dir = self.vault_path / 'Alerts'
        self.alerts_dir.mkdir(parents=True, exist_ok=True)

        logger.info('SubscriptionAudit initialized')

    def audit_subscriptions(self):
        """Main audit function"""
        logger.info('Starting subscription audit...')

        subscriptions = []
        charges_to_review = []

        # Check accounting file
        accounting_file = self.accounting_dir / 'Current_Month.md'
        if accounting_file.exists():
            content = accounting_file.read_text()
            subscriptions, charges_to_review = self._parse_transactions(content)
        else:
            logger.warning(f'Accounting file not found: {accounting_file}')

        # Identify unused subscriptions
        unused = self._identify_unused(subscriptions)

        # Generate recommendations
        recommendations = self._generate_recommendations(unused, subscriptions)

        audit_result = {
            'timestamp': datetime.now().isoformat(),
            'subscriptions_found': len(subscriptions),
            'subscriptions': subscriptions,
            'unused_subscriptions': unused,
            'recommendations': recommendations,
            'total_monthly_cost': sum(s.get('amount', 0) for s in subscriptions),
            'potential_savings': sum(s.get('amount', 0) for s in unused)
        }

        logger.info(f'Audit complete: {len(subscriptions)} subscriptions found')
        logger.info(f'Potential savings: ${audit_result["potential_savings"]:.2f}')

        return audit_result

    def _parse_transactions(self, content):
        """Parse transactions from accounting markdown"""
        logger.info('Parsing transaction data...')

        subscriptions = []
        charges_to_review = []

        # Look for transaction lines with amounts and dates
        lines = content.split('\n')

        for line in lines:
            if '$' in line or '€' in line or '£' in line:
                # Try to match subscription patterns
                for pattern, info in self.SUBSCRIPTION_PATTERNS.items():
                    if pattern.lower() in line.lower():
                        try:
                            # Extract amount
                            amount_match = re.search(r'[\$€£]\s*([\d,]+\.?\d*)', line)
                            if amount_match:
                                amount = float(amount_match.group(1).replace(',', ''))

                                # Extract date if available
                                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                                date_str = date_match.group(1) if date_match else None

                                subscription = {
                                    'name': info['name'],
                                    'pattern': pattern,
                                    'category': info['category'],
                                    'amount': amount,
                                    'date': date_str,
                                    'description': line.strip(),
                                    'activity_status': self._check_activity(info['name']),
                                    'usage_score': self._estimate_usage(info['name'])
                                }

                                # Check if already in list (avoid duplicates)
                                if not any(s['name'] == subscription['name'] for s in subscriptions):
                                    subscriptions.append(subscription)
                                    logger.debug(f'Found: {subscription["name"]} - ${amount:.2f}')

                        except (ValueError, AttributeError):
                            charges_to_review.append(line)

        return subscriptions, charges_to_review

    def _check_activity(self, subscription_name):
        """Check if subscription has recent activity"""
        # In production, this would check logs, browser history, etc.
        # For now, return "unknown" and flag for review

        inactive_keywords = ['old', 'unused', 'inactive', 'deprecated']
        name_lower = subscription_name.lower()

        if any(keyword in name_lower for keyword in inactive_keywords):
            return 'inactive'

        return 'unknown'

    def _estimate_usage(self, subscription_name):
        """Estimate usage frequency (0-100)"""
        # In production, this would analyze actual usage data
        # For demo, return unknown

        return 50  # Default: unknown/needs review

    def _identify_unused(self, subscriptions):
        """Identify subscriptions that appear unused"""
        logger.info('Identifying unused subscriptions...')

        unused = []

        for sub in subscriptions:
            # Flag if:
            # 1. Activity status is inactive, OR
            # 2. Usage score is very low
            # 3. Pattern hasn't appeared in recent transactions

            if (sub['activity_status'] == 'inactive' or
                    sub['usage_score'] < 20):

                unused.append({
                    'name': sub['name'],
                    'amount': sub['amount'],
                    'category': sub['category'],
                    'activity': sub['activity_status'],
                    'usage_score': sub['usage_score'],
                    'reason': self._get_cancellation_reason(sub)
                })

        return unused

    def _get_cancellation_reason(self, subscription):
        """Determine why subscription might be unused"""
        if subscription['activity_status'] == 'inactive':
            return 'No recent activity detected'
        elif subscription['usage_score'] < 20:
            return 'Very low usage detected'
        else:
            return 'Marked for review'

    def _generate_recommendations(self, unused, all_subscriptions):
        """Generate recommendations for action"""
        logger.info('Generating recommendations...')

        recommendations = []

        # For each unused subscription, create a recommendation
        for sub in unused:
            rec = {
                'type': 'cost_optimization',
                'priority': 'medium',
                'subscription': sub['name'],
                'monthly_cost': sub['amount'],
                'annual_savings': sub['amount'] * 12,
                'action': f"Cancel {sub['name']} subscription",
                'reason': sub['reason'],
                'approval_needed': True,
                'approval_file': f"CANCEL_{sub['name'].replace(' ', '_').lower()}.md"
            }
            recommendations.append(rec)

        return recommendations

    def create_approval_requests(self, audit_result):
        """Create approval request files for recommendations"""
        logger.info('Creating approval requests...')

        for rec in audit_result['recommendations']:
            approval_file = self.alerts_dir / rec['approval_file']

            content = f"""---
type: approval_request
action: cancel_subscription
subscription: {rec['subscription']}
monthly_cost: ${rec['monthly_cost']:.2f}
annual_savings: ${rec['annual_savings']:.2f}
reason: {rec['reason']}
created: {datetime.now().isoformat()}
---

# Cancel {rec['subscription']}

## Details
- Monthly Cost: ${rec['monthly_cost']:.2f}
- Annual Savings: ${rec['annual_savings']:.2f}
- Reason: {rec['reason']}

## Action
Move this file to `/Approved/` to approve cancellation.
Move to `/Rejected/` to keep this subscription.

## Timeline
- Approval expires: {(datetime.now() + timedelta(days=7)).isoformat()}
"""

            approval_file.write_text(content)
            logger.info(f'Created approval request: {approval_file.name}')

    def generate_report(self):
        """Generate detailed audit report"""
        audit_result = self.audit_subscriptions()

        # Create approval requests
        self.create_approval_requests(audit_result)

        # Format report
        report = f"""
# Subscription Audit Report

**Generated:** {audit_result['timestamp']}

## Summary
- Total Subscriptions: {audit_result['subscriptions_found']}
- Potentially Unused: {len(audit_result['unused_subscriptions'])}
- Total Monthly Cost: ${audit_result['total_monthly_cost']:.2f}
- Potential Savings: ${audit_result['potential_savings']:.2f} ({(audit_result['potential_savings']/audit_result['total_monthly_cost']*100 if audit_result['total_monthly_cost'] > 0 else 0):.0f}%)

## Subscriptions
"""

        for sub in audit_result['subscriptions']:
            report += f"- {sub['name']}: ${sub['amount']:.2f}/month\n"

        report += f"\n## Recommendations\n"

        for rec in audit_result['recommendations']:
            report += f"- Cancel {rec['subscription']}: Save ${rec['annual_savings']:.2f}/year\n"

        return report, audit_result


def main():
    """Run subscription audit"""
    import sys

    vault_path = sys.argv[1] if len(sys.argv) > 1 else './AI_Employee_Vault'

    audit = SubscriptionAudit(vault_path)
    report, result = audit.generate_report()

    print(report)

    # Save result
    result_file = Path(vault_path) / 'Briefings' / 'subscription_audit.json'
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(json.dumps(result, indent=2))

    print(f'\nReport saved to {result_file}')


if __name__ == '__main__':
    main()
