from Shares.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def _create_tags(self):
        faqs = {
            "What is Stock Vault?": "Stock Vault is a portfolio management tool that helps users track and analyze their stock investments with ease.",
            "Who can use Stock Vault?": "Anyone interested in tracking stocks—from beginners to experienced investors—can use Stock Vault.",
            "Is Stock Vault free to use?": "Yes, Stock Vault is completely free for all users.",
            "How many portfolios can I create?": "You can create and manage unlimited portfolios inside Stock Vault.",
            "Does Stock Vault show real-time stock prices?": "Stock Vault displays near real-time prices depending on your data source configuration.",
            "Can I track historical performance?": "Yes, Stock Vault provides historical charts and performance insights.",
            "Is Stock Vault mobile-friendly?": "Yes, Stock Vault works smoothly on both desktop and mobile browsers.",
            "Can I export my portfolio data?": "Yes, you can export your data to CSV or Excel for offline use.",
            "Does Stock Vault support multiple currencies?": "Yes, Stock Vault supports multiple currencies for global users.",
            "Is my data secure?": "Absolutely. Stock Vault uses encryption and secure storage practices to keep your data safe.",
            "Can beginners use Stock Vault?": "Yes, Stock Vault is designed to be simple and intuitive for beginners while still powerful for advanced users.",
            "Can I share my portfolio with others?": "Yes, you can generate shareable links to showcase your portfolio performance.",
            "Does Stock Vault support mutual funds or ETFs?": "Yes, Stock Vault supports stocks, ETFs, and mutual funds depending on your market region.",
            "Do I need to install anything?": "No installation is required—Stock Vault runs directly in your browser.",
            "How often is data updated?": "Data updates depend on your stock market region but typically refresh every few minutes.",
            "Can I analyze my profit and loss?": "Yes, Stock Vault calculates gains, losses, and overall performance for your investments.",
            "Can students use Stock Vault for learning?": "Yes, many students use Stock Vault to understand investing concepts and track mock portfolios.",
            "Is there a limit to the number of stocks I can track?": "No, you can add as many stocks as you want in your portfolio.",
            "How do I get started?": "Simply sign up, add your stocks, and Stock Vault will handle the rest.",
            "Who built Stock Vault?": "Stock Vault was built by a BCA student to simplify stock tracking and now serves hundreds of users."
        }

        for question, answer in faqs.items():
            faq = FAQs(question=question, answer=answer)
            faq.save()

    def handle(self, *args, **options):
        self._create_tags()
