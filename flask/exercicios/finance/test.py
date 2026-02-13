from datetime import datetime, timezone

date = datetime.now(timezone.utc)
date = str(date)[:19]
print(date)
