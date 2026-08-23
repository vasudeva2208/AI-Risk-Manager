export function formatCurrency(
  amount: number,
  currency: string = 'INR',
  options: { minimumFractionDigits?: number; maximumFractionDigits?: number } = { minimumFractionDigits: 2, maximumFractionDigits: 2 }
): string {
  if (currency === 'INR') {
    return `₹${amount.toLocaleString('en-IN', options)}`;
  }
  return `$${amount.toLocaleString('en-US', options)}`;
}

export function formatPercent(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatDate(isoString: string): string {
  try {
    const d = new Date(isoString);
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (e) {
    return isoString;
  }
}

export function formatTimeAgo(isoString: string): string {
  try {
    const diffMs = Date.now() - new Date(isoString).getTime();
    const mins = Math.floor(diffMs / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  } catch (e) {
    return isoString;
  }
}
