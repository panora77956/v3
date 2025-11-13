# -*- coding: utf-8 -*-
"""
Vertex AI Credit Checker
Provides utilities to check and monitor Vertex AI credit usage and quotas
"""

import webbrowser
from typing import Dict


class VertexCreditChecker:
    """
    Utility for checking Vertex AI credit usage and providing billing information

    Note: Google Cloud does not expose promotional credits via API.
    This module provides helper methods to access billing information via Console.
    """

    @staticmethod
    def get_billing_console_url(project_id: str) -> str:
        """
        Get the GCP Console billing URL for a project

        Args:
            project_id: GCP project ID

        Returns:
            URL to the billing page for the project
        """
        return f"https://console.cloud.google.com/billing/projects/{project_id}"

    @staticmethod
    def get_vertex_ai_console_url(project_id: str, location: str = "us-central1") -> str:
        """
        Get the Vertex AI console URL for a project

        Args:
            project_id: GCP project ID
            location: GCP region

        Returns:
            URL to the Vertex AI dashboard
        """
        return f"https://console.cloud.google.com/vertex-ai/generative/language?project={project_id}"

    @staticmethod
    def get_quotas_console_url(project_id: str) -> str:
        """
        Get the GCP Console quotas URL for a project

        Args:
            project_id: GCP project ID

        Returns:
            URL to the quotas page
        """
        return f"https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas?project={project_id}"

    @staticmethod
    def open_billing_console(project_id: str):
        """
        Open the billing console in the default browser

        Args:
            project_id: GCP project ID
        """
        url = VertexCreditChecker.get_billing_console_url(project_id)
        webbrowser.open(url)

    @staticmethod
    def open_vertex_console(project_id: str, location: str = "us-central1"):
        """
        Open the Vertex AI console in the default browser

        Args:
            project_id: GCP project ID
            location: GCP region
        """
        url = VertexCreditChecker.get_vertex_ai_console_url(project_id, location)
        webbrowser.open(url)

    @staticmethod
    def open_quotas_console(project_id: str):
        """
        Open the quotas console in the default browser

        Args:
            project_id: GCP project ID
        """
        url = VertexCreditChecker.get_quotas_console_url(project_id)
        webbrowser.open(url)

    @staticmethod
    def get_estimated_cost_info() -> Dict[str, any]:
        """
        Get estimated cost information for Vertex AI usage

        Returns:
            Dictionary with pricing information
        """
        return {
            "gemini_2_5_flash": {
                "input_price_per_1m_chars": 0.075,  # $0.075 per 1M characters input
                "output_price_per_1m_chars": 0.30,   # $0.30 per 1M characters output
                "free_tier": "$300 credit (new accounts)",
                "note": "Prices for gemini-2.5-flash model in Vertex AI"
            },
            "gemini_1_5_pro": {
                "input_price_per_1m_chars": 1.25,   # $1.25 per 1M characters input
                "output_price_per_1m_chars": 5.00,   # $5.00 per 1M characters output
                "free_tier": "$300 credit (new accounts)",
                "note": "Prices for gemini-1.5-pro model in Vertex AI"
            },
            "free_tier_info": {
                "amount": "$300",
                "duration": "90 days",
                "new_accounts": True,
                "applies_to": "All GCP services including Vertex AI"
            }
        }

    @staticmethod
    def format_pricing_info() -> str:
        """
        Format pricing information as human-readable text

        Returns:
            Formatted pricing information string
        """
        info = VertexCreditChecker.get_estimated_cost_info()

        text = "💰 Vertex AI Pricing Information:\n\n"

        # Gemini 2.5 Flash
        flash = info["gemini_2_5_flash"]
        text += "📱 Gemini 2.5 Flash (Recommended):\n"
        text += f"   • Input: ${flash['input_price_per_1m_chars']} per 1M characters\n"
        text += f"   • Output: ${flash['output_price_per_1m_chars']} per 1M characters\n"
        text += f"   • {flash['free_tier']}\n\n"

        # Gemini 1.5 Pro
        pro = info["gemini_1_5_pro"]
        text += "🚀 Gemini 1.5 Pro:\n"
        text += f"   • Input: ${pro['input_price_per_1m_chars']} per 1M characters\n"
        text += f"   • Output: ${pro['output_price_per_1m_chars']} per 1M characters\n"
        text += f"   • {pro['free_tier']}\n\n"

        # Free tier
        free = info["free_tier_info"]
        text += "🎁 Free Tier:\n"
        text += f"   • {free['amount']} credit for {free['duration']}\n"
        text += "   • New GCP accounts only\n"
        text += "   • Applies to all GCP services\n\n"

        text += "💡 Tip: Mỗi GCP project mới = $300 credit mới!\n"
        text += "   Thêm nhiều service accounts = nhiều project = nhiều credit!"

        return text

    @staticmethod
    def get_account_info_text(project_id: str, location: str = "us-central1") -> str:
        """
        Get formatted account information text

        Args:
            project_id: GCP project ID
            location: GCP region

        Returns:
            Formatted account information
        """
        text = f"📊 Project: {project_id}\n"
        text += f"📍 Region: {location}\n\n"
        text += "🔗 Quick Links:\n"
        billing_url = VertexCreditChecker.get_billing_console_url(project_id)
        text += f"   • Billing: {billing_url}\n"
        vertex_url = VertexCreditChecker.get_vertex_ai_console_url(project_id, location)
        text += f"   • Vertex AI: {vertex_url}\n"
        quotas_url = VertexCreditChecker.get_quotas_console_url(project_id)
        text += f"   • Quotas: {quotas_url}\n\n"
        text += "💡 Để xem credit còn lại:\n"
        text += "   1. Mở link Billing ở trên\n"
        text += "   2. Xem phần 'Credits' hoặc 'Promotional credits'\n"
        text += "   3. Kiểm tra 'Current balance' và 'Usage to date'\n"

        return text


# Global instance
_credit_checker = None


def get_credit_checker() -> VertexCreditChecker:
    """Get global credit checker instance"""
    global _credit_checker
    if _credit_checker is None:
        _credit_checker = VertexCreditChecker()
    return _credit_checker
