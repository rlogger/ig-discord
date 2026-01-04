import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from io import BytesIO
from typing import Optional
import numpy as np


# Set style
plt.style.use('seaborn-v0_8-darkgrid')


def create_follower_trend_plot(snapshots: list[dict]) -> BytesIO:
    """
    Create a line plot showing follower count over time.

    Args:
        snapshots: List of snapshot dicts with 'uploaded_at' and 'total_followers'

    Returns:
        BytesIO buffer containing the plot image
    """
    if not snapshots:
        return create_empty_plot("No data available yet")

    dates = []
    counts = []

    for s in snapshots:
        uploaded_at = s['uploaded_at']
        if isinstance(uploaded_at, str):
            uploaded_at = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
        dates.append(uploaded_at)
        counts.append(s['total_followers'])

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(dates, counts, marker='o', linewidth=2, markersize=8, color='#5865F2')
    ax.fill_between(dates, counts, alpha=0.3, color='#5865F2')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Follower Count', fontsize=12)
    ax.set_title('Follower Count Over Time', fontsize=14, fontweight='bold')

    # Format x-axis dates
    if len(dates) > 1:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45)

    # Add annotations for each point
    for i, (date, count) in enumerate(zip(dates, counts)):
        ax.annotate(
            str(count),
            (date, count),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center',
            fontsize=9
        )

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def create_comparison_pie_chart(
    mutual: int,
    fans: int,
    non_followers: int
) -> BytesIO:
    """
    Create a pie chart showing follow relationship breakdown.

    Args:
        mutual: Count of mutual follows
        fans: Count of people who follow you but you don't follow back
        non_followers: Count of people you follow who don't follow you back

    Returns:
        BytesIO buffer containing the plot image
    """
    labels = []
    sizes = []
    colors = []

    if mutual > 0:
        labels.append(f'Mutual ({mutual})')
        sizes.append(mutual)
        colors.append('#57F287')  # Green

    if fans > 0:
        labels.append(f'Fans ({fans})')
        sizes.append(fans)
        colors.append('#5865F2')  # Blurple

    if non_followers > 0:
        labels.append(f"Don't follow back ({non_followers})")
        sizes.append(non_followers)
        colors.append('#ED4245')  # Red

    if not sizes:
        return create_empty_plot("No relationship data available")

    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        explode=[0.02] * len(sizes)
    )

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    ax.set_title('Follow Relationship Breakdown', fontsize=14, fontweight='bold')

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def create_change_bar_chart(comparison: dict) -> BytesIO:
    """
    Create a bar chart showing gained/lost followers.

    Args:
        comparison: Dict with 'gained_count', 'lost_count', 'net_change'

    Returns:
        BytesIO buffer containing the plot image
    """
    gained = comparison.get('gained_count', 0)
    lost = comparison.get('lost_count', 0)
    net = comparison.get('net_change', 0)

    fig, ax = plt.subplots(figsize=(8, 6))

    categories = ['Gained', 'Lost', 'Net Change']
    values = [gained, -lost, net]
    colors = ['#57F287', '#ED4245', '#5865F2' if net >= 0 else '#FEE75C']

    bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=2)

    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f'{value:+d}' if value != 0 else '0',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5 if height >= 0 else -15),
            textcoords="offset points",
            ha='center',
            va='bottom' if height >= 0 else 'top',
            fontsize=12,
            fontweight='bold'
        )

    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Follower Changes Since Last Upload', fontsize=14, fontweight='bold')

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def create_growth_rate_plot(snapshots: list[dict]) -> BytesIO:
    """
    Create a plot showing growth rate between snapshots.

    Args:
        snapshots: List of snapshot dicts

    Returns:
        BytesIO buffer containing the plot image
    """
    if len(snapshots) < 2:
        return create_empty_plot("Need at least 2 uploads to show growth rate")

    dates = []
    growth_rates = []

    for i in range(1, len(snapshots)):
        prev = snapshots[i - 1]
        curr = snapshots[i]

        uploaded_at = curr['uploaded_at']
        if isinstance(uploaded_at, str):
            uploaded_at = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
        dates.append(uploaded_at)

        prev_count = prev['total_followers']
        curr_count = curr['total_followers']

        if prev_count > 0:
            rate = ((curr_count - prev_count) / prev_count) * 100
        else:
            rate = 0

        growth_rates.append(rate)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['#57F287' if r >= 0 else '#ED4245' for r in growth_rates]

    bars = ax.bar(range(len(dates)), growth_rates, color=colors, edgecolor='white', linewidth=1)

    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([d.strftime('%b %d') for d in dates], rotation=45)

    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8)
    ax.set_ylabel('Growth Rate (%)', fontsize=12)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_title('Follower Growth Rate Between Uploads', fontsize=14, fontweight='bold')

    # Add value labels
    for bar, rate in zip(bars, growth_rates):
        height = bar.get_height()
        ax.annotate(
            f'{rate:+.1f}%',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5 if height >= 0 else -15),
            textcoords="offset points",
            ha='center',
            va='bottom' if height >= 0 else 'top',
            fontsize=9
        )

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def create_empty_plot(message: str) -> BytesIO:
    """Create an empty plot with a message."""
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.text(
        0.5, 0.5,
        message,
        horizontalalignment='center',
        verticalalignment='center',
        transform=ax.transAxes,
        fontsize=14,
        color='gray'
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def create_summary_dashboard(
    snapshots: list[dict],
    current_analysis: dict,
    comparison: Optional[dict] = None
) -> BytesIO:
    """
    Create a comprehensive dashboard with multiple plots.

    Args:
        snapshots: List of historical snapshots
        current_analysis: Analysis of current upload
        comparison: Optional comparison with previous upload

    Returns:
        BytesIO buffer containing the dashboard image
    """
    fig = plt.figure(figsize=(14, 10))

    # 2x2 grid
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # Plot 1: Follower trend (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    if snapshots:
        dates = []
        counts = []
        for s in snapshots:
            uploaded_at = s['uploaded_at']
            if isinstance(uploaded_at, str):
                uploaded_at = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
            dates.append(uploaded_at)
            counts.append(s['total_followers'])

        ax1.plot(dates, counts, marker='o', linewidth=2, color='#5865F2')
        ax1.fill_between(dates, counts, alpha=0.3, color='#5865F2')
        if len(dates) > 1:
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    ax1.set_title('Follower Trend', fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Followers')

    # Plot 2: Relationship breakdown (top right)
    ax2 = fig.add_subplot(gs[0, 1])
    mutual = len(current_analysis.get('mutual', []))
    fans = len(current_analysis.get('fans', []))
    not_following = len(current_analysis.get('you_dont_follow_back', []))

    if mutual + fans > 0:
        labels = ['Mutual', 'Fans']
        sizes = [mutual, fans]
        colors = ['#57F287', '#5865F2']
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Follow Relationships', fontweight='bold')

    # Plot 3: Changes (bottom left)
    ax3 = fig.add_subplot(gs[1, 0])
    if comparison:
        categories = ['Gained', 'Lost', 'Net']
        values = [
            comparison['gained_count'],
            -comparison['lost_count'],
            comparison['net_change']
        ]
        colors = ['#57F287', '#ED4245', '#5865F2' if values[2] >= 0 else '#FEE75C']
        ax3.bar(categories, values, color=colors)
        ax3.axhline(y=0, color='gray', linestyle='-', linewidth=0.8)
    else:
        ax3.text(0.5, 0.5, 'No previous data', ha='center', va='center',
                 transform=ax3.transAxes, color='gray')
    ax3.set_title('Recent Changes', fontweight='bold')
    ax3.set_ylabel('Count')

    # Plot 4: Stats summary (bottom right)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')

    stats_text = f"""
    📊 Current Stats
    ━━━━━━━━━━━━━━━━━━
    Total Followers: {len(current_analysis.get('followers', []))}
    Mutual Follows: {mutual}
    Fans (don't follow back): {fans}
    Uploads: {len(snapshots)}
    """

    if comparison:
        stats_text += f"""
    📈 Since Last Upload
    ━━━━━━━━━━━━━━━━━━
    Gained: +{comparison['gained_count']}
    Lost: -{comparison['lost_count']}
    Net Change: {comparison['net_change']:+d}
    """

    ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes,
             fontsize=11, verticalalignment='top', fontfamily='monospace')

    plt.suptitle('Instagram Follower Dashboard', fontsize=16, fontweight='bold', y=0.98)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf
