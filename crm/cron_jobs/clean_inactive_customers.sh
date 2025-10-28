#!/bin/bash
# Define the log file
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Navigate to the Django project directory
cd "$(dirname "$0")/../.." || exit

# Run the Django shell command
DELETED_COUNT=$(python manage.py shell -c "
from datetime import datetime, timedelta
from crm.models import Customer, Order

one_year_ago = datetime.now() - timedelta(days=365)

# Filter customers with no orders in the past year
inactive_customers = Customer.objects.exclude(order__order_date__gte=one_year_ago)
deleted_count, _ = inactive_customers.delete()
print(deleted_count)
")

# Log the result with timestamp
echo \"$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers\" >> \"$LOG_FILE\"
