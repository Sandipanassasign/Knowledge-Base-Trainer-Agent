"""
Seed Data — Sample defect records to populate the knowledge base.
Run: python seed_data.py
"""
from models import DefectRecord, Severity
from qdrant_store import QdrantStore


SAMPLE_DEFECTS = [
    DefectRecord(
        title="Login fails intermittently on slow networks",
        description="Users experience login failures when network latency exceeds 200ms. The authentication token request times out before the server responds. This affects mobile users more than desktop users due to higher average latency.",
        severity=Severity.HIGH,
        module_id="authentication",
        root_cause_category="timeout",
        release_version="v2.3.0",
        resolution="Increased timeout threshold from 5s to 15s and added retry logic with exponential backoff.",
        test_type="e2e",
    ),
    DefectRecord(
        title="Payment processing returns null response",
        description="The payment gateway returns a null response object when processing refunds over $500. The null check was missing in the response handler, causing a NullPointerException in the transaction logger.",
        severity=Severity.CRITICAL,
        module_id="payment",
        root_cause_category="null_pointer",
        release_version="v2.3.0",
        resolution="Added null safety checks and fallback handling for payment gateway responses. Added unit tests for edge cases.",
        test_type="integration",
    ),
    DefectRecord(
        title="Search results not updating after filter change",
        description="When users apply a new filter on the search page, the results list does not refresh. The state management store is not detecting the filter change because the object reference comparison fails for deep-nested filter objects.",
        severity=Severity.MEDIUM,
        module_id="search",
        root_cause_category="state_management",
        release_version="v2.2.0",
        resolution="Switched to deep comparison for filter objects and added a dedicated filter change event listener.",
        test_type="unit",
    ),
    DefectRecord(
        title="Database connection pool exhaustion under load",
        description="During peak traffic (>1000 concurrent users), the database connection pool runs out of connections. New requests queue up and eventually timeout. The connection pool size was set to a default of 10.",
        severity=Severity.CRITICAL,
        module_id="database",
        root_cause_category="resource_exhaustion",
        release_version="v2.1.0",
        resolution="Increased pool size to 50, added connection recycling, and implemented circuit breaker pattern for graceful degradation.",
        test_type="performance",
    ),
    DefectRecord(
        title="User profile image upload corrupts HEIF files",
        description="When users upload HEIF format images (common on iPhones), the image processing pipeline corrupts the file. The image resizer library does not support HEIF format and silently produces a corrupted output.",
        severity=Severity.MEDIUM,
        module_id="user_profile",
        root_cause_category="format_incompatibility",
        release_version="v2.3.0",
        resolution="Added HEIF to JPEG conversion step before resizing. Added format validation at upload time.",
        test_type="integration",
    ),
    DefectRecord(
        title="Race condition in cart item quantity update",
        description="Rapid clicks on the +/- quantity buttons cause race conditions. Two concurrent API calls update the quantity simultaneously, resulting in incorrect final values. The optimistic UI update conflicts with the server response.",
        severity=Severity.HIGH,
        module_id="cart",
        root_cause_category="race_condition",
        release_version="v2.2.0",
        resolution="Implemented debouncing on quantity buttons and added server-side idempotency keys for cart operations.",
        test_type="e2e",
    ),
    DefectRecord(
        title="Email notifications sent with wrong timezone",
        description="Scheduled email notifications display times in UTC instead of the user's local timezone. The timezone conversion logic in the notification service uses the server timezone instead of the user's preference.",
        severity=Severity.LOW,
        module_id="notifications",
        root_cause_category="timezone_handling",
        release_version="v2.1.0",
        resolution="Updated notification service to resolve user timezone from profile settings before formatting timestamps.",
        test_type="unit",
    ),
    DefectRecord(
        title="API rate limiting not applied to internal services",
        description="Internal microservices bypass the API rate limiter because they use a different authentication path. A misbehaving internal service caused a cascade failure by flooding the order service with requests.",
        severity=Severity.CRITICAL,
        module_id="api_gateway",
        root_cause_category="missing_validation",
        release_version="v2.3.0",
        resolution="Extended rate limiting to all service-to-service communication. Added per-service quotas and monitoring alerts.",
        test_type="integration",
    ),
    DefectRecord(
        title="Memory leak in WebSocket connection handler",
        description="The WebSocket handler does not properly clean up disconnected client references. Over time, the server's memory usage grows linearly. After ~48 hours, the service runs out of memory and crashes.",
        severity=Severity.HIGH,
        module_id="real_time",
        root_cause_category="memory_leak",
        release_version="v2.2.0",
        resolution="Added proper cleanup in the disconnect handler and implemented a periodic garbage collection sweep for stale connections.",
        test_type="performance",
    ),
    DefectRecord(
        title="CSV export generates incorrect column mapping",
        description="When exporting user data to CSV, the column headers do not match the data columns. The export function uses a dictionary which does not guarantee insertion order in older Python versions.",
        severity=Severity.MEDIUM,
        module_id="reporting",
        root_cause_category="data_mapping",
        release_version="v2.1.0",
        resolution="Switched to OrderedDict and added explicit column ordering. Added CSV validation tests.",
        test_type="unit",
    ),
    DefectRecord(
        title="OAuth token refresh fails silently",
        description="When the OAuth access token expires, the refresh token flow fails silently, logging the user out without any warning. The error handler catches the refresh exception but does not propagate it to the UI layer.",
        severity=Severity.HIGH,
        module_id="authentication",
        root_cause_category="error_handling",
        release_version="v2.3.0",
        resolution="Added proper error propagation from token refresh to UI, showing a re-login prompt instead of silent logout.",
        test_type="e2e",
    ),
    DefectRecord(
        title="Inventory count becomes negative after concurrent orders",
        description="When multiple users order the last item simultaneously, the inventory count goes negative. The inventory check and decrement are not atomic, allowing a TOCTOU race condition.",
        severity=Severity.CRITICAL,
        module_id="inventory",
        root_cause_category="race_condition",
        release_version="v2.2.0",
        resolution="Implemented database-level atomic decrement with CHECK constraint. Added pessimistic locking for inventory operations.",
        test_type="integration",
    ),
    DefectRecord(
        title="Dashboard charts render with stale data after navigation",
        description="Navigating away from the dashboard and back causes charts to display stale cached data. The chart component mounts with old state from the previous render cycle.",
        severity=Severity.LOW,
        module_id="dashboard",
        root_cause_category="caching",
        release_version="v2.3.0",
        resolution="Added cache invalidation on component mount and implemented stale-while-revalidate pattern.",
        test_type="unit",
    ),
    DefectRecord(
        title="File upload endpoint allows oversized files",
        description="The file upload endpoint accepts files exceeding the 10MB limit. The size validation only checks the Content-Length header, which can be spoofed. Actual file size is not validated during streaming.",
        severity=Severity.HIGH,
        module_id="file_service",
        root_cause_category="missing_validation",
        release_version="v2.1.0",
        resolution="Added streaming size validation that aborts the upload if the actual bytes exceed the limit. Added integration tests with large file payloads.",
        test_type="integration",
    ),
    DefectRecord(
        title="Push notifications not delivered on Android 13+",
        description="Push notifications fail on Android 13+ devices because the app does not request the POST_NOTIFICATIONS runtime permission introduced in API level 33. The notification token is registered but deliveries are silently blocked by the OS.",
        severity=Severity.HIGH,
        module_id="notifications",
        root_cause_category="platform_compatibility",
        release_version="v2.3.0",
        resolution="Added POST_NOTIFICATIONS permission request flow during onboarding. Added Android API level checks for graceful fallback.",
        test_type="e2e",
    ),
]


def seed_database():
    """Seed the Qdrant database with sample defect data."""
    print("🌱 Seeding the DKI knowledge base...")
    store = QdrantStore()
    ids = store.ingest_batch(SAMPLE_DEFECTS)
    print(f"✅ Successfully ingested {len(ids)} defect records.")
    print(f"   Collection: {store.client.get_collection('defect_knowledge_base').points_count} total points.")
    return ids


if __name__ == "__main__":
    seed_database()
