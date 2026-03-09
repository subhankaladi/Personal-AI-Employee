#!/usr/bin/env python3

"""
Business Audit Script for Personal AI Employee
Analyzes business performance, revenue, tasks, and bottlenecks
Generates CEO briefing input for Claude processing

Phase 3 Implementation
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - BusinessAudit - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BusinessAudit:
    """
    Weekly business audit that analyzes:
    - Revenue tracking vs goals
    - Completed tasks
    - Project status
    - Bottlenecks and delays
    - Subscription audit
    - Recommendations
    """

    def __init__(self, vault_path, odoo_config=None):
        """Initialize audit system"""
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.briefings_dir = self.vault_path / 'Briefings'
        self.done_dir = self.vault_path / 'Done'
        self.accounting_dir = self.vault_path / 'Accounting'

        # Create directories if they don't exist
        for directory in [self.logs_dir, self.briefings_dir, self.accounting_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self.odoo_config = odoo_config or {}
        logger.info('BusinessAudit initialized')

    def run_weekly_audit(self):
        """Main audit runner - called every Sunday 11 PM"""
        logger.info('Starting weekly business audit...')

        try:
            audit_data = {
                'timestamp': datetime.now().isoformat(),
                'period_start': self.get_week_start(),
                'period_end': self.get_week_end(),
                'revenue': self.calculate_revenue(),
                'completed_tasks': self.count_completed_tasks(),
                'bottlenecks': self.identify_bottlenecks(),
                'subscriptions': self.audit_subscriptions(),
                'recommendations': self.generate_recommendations()
            }

            logger.info(f'Audit complete: Revenue=${audit_data["revenue"]["this_week"]:.2f}')
            return audit_data

        except Exception as e:
            logger.error(f'Audit failed: {e}')
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_week_start(self):
        """Get start of current week (Monday)"""
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        return monday.date().isoformat()

    def get_week_end(self):
        """Get end of current week (Sunday)"""
        today = datetime.now()
        sunday = today + timedelta(days=6 - today.weekday())
        return sunday.date().isoformat()

    def calculate_revenue(self):
        """Calculate revenue from completed tasks and invoices"""
        logger.info('Calculating revenue...')

        revenue_data = {
            'this_week': 0,
            'mtd': 0,
            'target': 10000,
            'projects': {}
        }

        # Check if accounting file exists
        accounting_file = self.accounting_dir / 'Current_Month.md'
        if accounting_file.exists():
            content = accounting_file.read_text()
            # Parse revenue from accounting file
            # Format: ### Revenue: $XXXX
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Revenue' in line and '$' in line:
                    try:
                        amount = float(line.split('$')[1].split()[0].replace(',', ''))
                        if 'This Week' in lines[max(0, i-1):i+2]:
                            revenue_data['this_week'] += amount
                        elif 'MTD' in lines[max(0, i-1):i+2]:
                            revenue_data['mtd'] += amount
                    except (ValueError, IndexError):
                        pass

        # Check Done folder for task files with revenue
        if self.done_dir.exists():
            for task_file in self.done_dir.glob('*.md'):
                content = task_file.read_text()
                if 'revenue' in content.lower() or 'amount' in content.lower():
                    # Try to extract amount
                    try:
                        for line in content.split('\n'):
                            if '$' in line or 'amount' in line.lower():
                                parts = line.split('$')
                                if len(parts) > 1:
                                    try:
                                        amount = float(parts[1].split()[0].replace(',', ''))
                                        revenue_data['this_week'] += amount
                                    except ValueError:
                                        pass
                    except Exception:
                        pass

        revenue_data['percentage_of_target'] = (revenue_data['mtd'] / revenue_data['target']) * 100 if revenue_data['target'] else 0

        logger.info(f"Revenue calculated: ${revenue_data['this_week']:.2f} this week")
        return revenue_data

    def count_completed_tasks(self):
        """Count tasks completed this week"""
        logger.info('Counting completed tasks...')

        if not self.done_dir.exists():
            return {'count': 0, 'tasks': []}

        files = list(self.done_dir.glob('*.md'))
        week_ago = (datetime.now() - timedelta(days=7)).timestamp()

        recent_files = []
        for f in files:
            try:
                if f.stat().st_mtime > week_ago:
                    recent_files.append(f)
            except OSError:
                pass

        tasks = []
        for task_file in recent_files[:10]:  # Get last 10 tasks
            try:
                content = task_file.read_text()
                # Extract title from first line or frontmatter
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines else task_file.name
                tasks.append({
                    'name': title,
                    'file': task_file.name,
                    'completed': task_file.stat().st_mtime
                })
            except Exception:
                pass

        logger.info(f'Found {len(recent_files)} tasks completed this week')
        return {'count': len(recent_files), 'tasks': tasks}

    def identify_bottlenecks(self):
        """Identify tasks that took longer than expected"""
        logger.info('Identifying bottlenecks...')

        bottlenecks = []
        plans_folder = self.vault_path / 'Plans'

        if not plans_folder.exists():
            return bottlenecks

        for plan_file in plans_folder.glob('*.md'):
            try:
                content = plan_file.read_text()

                # Parse frontmatter
                if content.startswith('---'):
                    lines = content.split('\n')
                    frontmatter_end = next(
                        (i for i in range(1, len(lines)) if lines[i] == '---'),
                        None
                    )

                    if frontmatter_end:
                        frontmatter = '\n'.join(lines[1:frontmatter_end])

                        # Check for duration fields
                        if 'duration_expected' in frontmatter and 'duration_actual' in frontmatter:
                            try:
                                expected = float(
                                    [l.split(':')[1].strip() for l in frontmatter.split('\n')
                                     if 'duration_expected' in l][0]
                                )
                                actual = float(
                                    [l.split(':')[1].strip() for l in frontmatter.split('\n')
                                     if 'duration_actual' in l][0]
                                )

                                # If actual > 50% more than expected, flag as bottleneck
                                if actual > expected * 1.5:
                                    task_name = plan_file.name.replace('PLAN_', '').replace('.md', '')
                                    bottlenecks.append({
                                        'task': task_name,
                                        'expected_hours': expected,
                                        'actual_hours': actual,
                                        'delay_hours': actual - expected,
                                        'delay_percent': ((actual - expected) / expected) * 100
                                    })
                            except (ValueError, IndexError):
                                pass
            except Exception as e:
                logger.debug(f'Error parsing plan {plan_file.name}: {e}')
                pass

        logger.info(f'Found {len(bottlenecks)} bottlenecks')
        return bottlenecks

    def audit_subscriptions(self):
        """Check for unused subscriptions"""
        logger.info('Auditing subscriptions...')

        subscriptions = []
        subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'github.com': 'GitHub Pro',
            'aws.amazon.com': 'AWS',
            'stripe.com': 'Stripe',
            'dropbox.com': 'Dropbox',
            'microsoft.com': 'Microsoft 365'
        }

        # Check accounting file for transactions
        accounting_file = self.accounting_dir / 'Current_Month.md'
        if accounting_file.exists():
            content = accounting_file.read_text()
            lines = content.split('\n')

            for line in lines:
                for pattern, name in subscription_patterns.items():
                    if pattern in line.lower():
                        try:
                            # Try to extract amount
                            amount = 0
                            for part in line.split():
                                if '$' in part:
                                    amount = float(part.replace('$', '').replace(',', ''))
                                    break

                            subscriptions.append({
                                'name': name,
                                'amount': amount,
                                'pattern': pattern,
                                'usage': 'Unknown',
                                'action': 'Review'
                            })
                        except ValueError:
                            pass

        logger.info(f'Found {len(subscriptions)} subscriptions')
        return subscriptions

    def generate_recommendations(self):
        """Generate proactive suggestions"""
        logger.info('Generating recommendations...')

        recommendations = []

        # Cost optimization recommendations
        for sub in self.audit_subscriptions():
            if sub['amount'] > 0:
                recommendations.append({
                    'type': 'cost_optimization',
                    'priority': 'medium',
                    'title': f'Review {sub["name"]} subscription',
                    'description': f'Subscription costs ${sub["amount"]:.2f}/month. Consider if usage justifies cost.',
                    'action': f'Cancel or reduce {sub["name"]} plan',
                    'savings': sub['amount']
                })

        # Bottleneck recommendations
        bottlenecks = self.identify_bottlenecks()
        if bottlenecks:
            total_delay = sum(b['delay_hours'] for b in bottlenecks)
            recommendations.append({
                'type': 'efficiency',
                'priority': 'high',
                'title': f'{len(bottlenecks)} tasks exceeded timeline',
                'description': f'Total delay: {total_delay:.1f} hours. Investigate root causes.',
                'action': 'Review delayed tasks for common patterns',
                'details': bottlenecks[:3]  # Top 3
            })

        # Revenue tracking
        revenue = self.calculate_revenue()
        if revenue['percentage_of_target'] < 50:
            recommendations.append({
                'type': 'revenue',
                'priority': 'high',
                'title': 'Revenue below target',
                'description': f"Only {revenue['percentage_of_target']:.0f}% of monthly target achieved.",
                'action': 'Focus on closing new deals',
                'target': revenue['target'],
                'current': revenue['mtd']
            })

        logger.info(f'Generated {len(recommendations)} recommendations')
        return recommendations

    def save_audit_report(self):
        """Save audit report to JSON file"""
        audit_data = self.run_weekly_audit()

        # Save to JSON log
        log_file = self.logs_dir / 'audit_log.json'
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        else:
            logs = []

        logs.append(audit_data)

        # Keep only last 52 weeks (1 year)
        logs = logs[-52:]

        log_file.write_text(json.dumps(logs, indent=2))
        logger.info(f'Audit report saved to {log_file}')

        return audit_data

    def get_briefing_input(self):
        """Get formatted input for CEO briefing generation"""
        audit_data = self.run_weekly_audit()

        briefing_input = {
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': audit_data['period_start'],
                'end': audit_data['period_end']
            },
            'executive_summary': self._format_summary(audit_data),
            'revenue': audit_data['revenue'],
            'completed_tasks': audit_data['completed_tasks'],
            'bottlenecks': audit_data['bottlenecks'],
            'subscriptions': audit_data['subscriptions'],
            'recommendations': audit_data['recommendations']
        }

        return briefing_input

    def _format_summary(self, audit_data):
        """Format executive summary text"""
        revenue = audit_data['revenue']
        tasks = audit_data['completed_tasks']
        bottlenecks = audit_data['bottlenecks']

        summary = f"""
Week Performance:
- Revenue: ${revenue['this_week']:.2f} ({revenue['percentage_of_target']:.0f}% of target)
- Tasks Completed: {tasks['count']}
- Bottlenecks: {len(bottlenecks)}
        """.strip()

        return summary


def main():
    """Run audit manually"""
    import sys

    vault_path = sys.argv[1] if len(sys.argv) > 1 else './AI_Employee_Vault'

    audit = BusinessAudit(vault_path)

    # Get briefing input
    briefing_input = audit.get_briefing_input()

    # Save report
    audit.save_audit_report()

    # Print summary
    print('\n' + '='*60)
    print('BUSINESS AUDIT REPORT')
    print('='*60)
    print(briefing_input['executive_summary'])
    print(f"\nRevenue: ${briefing_input['revenue']['this_week']:.2f}")
    print(f"Tasks: {briefing_input['completed_tasks']['count']}")
    print(f"Bottlenecks: {len(briefing_input['bottlenecks'])}")
    print(f"Recommendations: {len(briefing_input['recommendations'])}")
    print('='*60 + '\n')

    # Save input for Claude
    input_file = Path(vault_path) / 'Briefings' / 'audit_input.json'
    input_file.write_text(json.dumps(briefing_input, indent=2))
    print(f'Audit input saved to {input_file}')


if __name__ == '__main__':
    main()
