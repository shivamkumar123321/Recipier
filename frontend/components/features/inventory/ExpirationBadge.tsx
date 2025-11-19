/**
 * ExpirationBadge Component
 *
 * Color-coded badge showing expiration status
 */

import { differenceInDays, parseISO, format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface ExpirationBadgeProps {
  expirationDate?: string;
  className?: string;
  showDate?: boolean;
}

export function ExpirationBadge({
  expirationDate,
  className,
  showDate = false,
}: ExpirationBadgeProps) {
  if (!expirationDate) {
    return null;
  }

  const expDate = parseISO(expirationDate);
  const today = new Date();
  const daysUntilExpiration = differenceInDays(expDate, today);

  // Determine status and styling
  const getExpirationStatus = () => {
    if (daysUntilExpiration < 0) {
      return {
        label: 'Expired',
        variant: 'destructive' as const,
        className: 'bg-red-100 text-red-800 border-red-200',
      };
    }
    if (daysUntilExpiration === 0) {
      return {
        label: 'Expires today',
        variant: 'destructive' as const,
        className: 'bg-red-100 text-red-800 border-red-200',
      };
    }
    if (daysUntilExpiration <= 3) {
      return {
        label: `${daysUntilExpiration}d left`,
        variant: 'destructive' as const,
        className: 'bg-orange-100 text-orange-800 border-orange-200',
      };
    }
    if (daysUntilExpiration <= 7) {
      return {
        label: `${daysUntilExpiration}d left`,
        variant: 'secondary' as const,
        className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      };
    }
    if (daysUntilExpiration <= 14) {
      return {
        label: `${daysUntilExpiration}d left`,
        variant: 'secondary' as const,
        className: 'bg-blue-100 text-blue-800 border-blue-200',
      };
    }
    return {
      label: `${daysUntilExpiration}d left`,
      variant: 'outline' as const,
      className: 'bg-green-100 text-green-800 border-green-200',
    };
  };

  const status = getExpirationStatus();
  const formattedDate = format(expDate, 'MMM d, yyyy');

  return (
    <Badge
      variant={status.variant}
      className={cn(status.className, className)}
      title={`Expires: ${formattedDate}`}
    >
      {showDate ? formattedDate : status.label}
    </Badge>
  );
}

/**
 * Get expiration status for filtering/sorting
 */
export function getExpirationStatus(expirationDate?: string): {
  status: 'expired' | 'expiring_soon' | 'expiring' | 'fresh' | 'none';
  daysUntilExpiration: number | null;
} {
  if (!expirationDate) {
    return { status: 'none', daysUntilExpiration: null };
  }

  const expDate = parseISO(expirationDate);
  const today = new Date();
  const daysUntilExpiration = differenceInDays(expDate, today);

  if (daysUntilExpiration < 0) {
    return { status: 'expired', daysUntilExpiration };
  }
  if (daysUntilExpiration <= 3) {
    return { status: 'expiring_soon', daysUntilExpiration };
  }
  if (daysUntilExpiration <= 7) {
    return { status: 'expiring', daysUntilExpiration };
  }
  return { status: 'fresh', daysUntilExpiration };
}
