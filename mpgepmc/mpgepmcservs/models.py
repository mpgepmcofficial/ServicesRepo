from django.db import models
from django.template.defaultfilters import slugify
from decimal import Decimal # Import Decimal for comparison

# --- Choices ---
DURATION_UNITS = [
    ('ONETIME', 'One-Time'),
    ('MONTH', 'Month(s)'),
    ('QUARTER', 'Quarterly'),
    ('HALFYR', 'Half-Yearly'),
    ('YEAR', 'Yearly'),
    ('PROJECT', 'Project'),
]

BUTTON_TYPES = [
    ('PRICE', 'Display Price Button'),
    ('CART', 'Add to Cart Button'),
    ('CONTACT', 'Contact to Sale Button'),
]

# --- Service Hierarchy Models ---

class ServiceClass(models.Model):
    """Corresponds to the main service categories (e.g., AI Services)."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, editable=False)
    description = models.TextField(blank=True, help_text="A brief summary for the index page.")
    order = models.IntegerField(default=0, help_text="Display order on the index page.")

    class Meta:
        verbose_name_plural = "1. Service Classes (Categories)"
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Service(models.Model):
    """Individual services within a class (e.g., AI Strategy & Consulting)."""
    service_class = models.ForeignKey(ServiceClass, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, editable=False)
    short_description = models.CharField(max_length=255, help_text="A short teaser for the class detail page.")
    detailed_description = models.TextField(blank=True, help_text="Full details for the service page.")

    class Meta:
        verbose_name_plural = "2. Services (Under Classes)"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.service_class.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Package(models.Model):
    """The specific package options with pricing and button configuration."""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='packages')
    package_type = models.CharField(max_length=100, help_text="E.g., Bronze, Standard, Enterprise.")
    
    # Duration Fields
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNITS, help_text="The frequency of the service.")
    duration_value = models.CharField(max_length=50, help_text="E.g., 'Project', '1 Month', '12 Months'.")

    # Pricing
    min_price_usd = models.DecimalField(max_digits=10, decimal_places=2, help_text="Minimum price.")
    max_price_usd = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum price (Set same as min if fixed price).")

    # Frontend Configuration
    button_type = models.CharField(max_length=10, choices=BUTTON_TYPES, default='CART', 
                                   help_text="Controls the button text/action on the frontend.")
    
    is_active = models.BooleanField(default=True, help_text="If unchecked, this package will not appear on the website.")

    class Meta:
        verbose_name_plural = "3. Packages (Under Services)"
        ordering = ['min_price_usd']

    def __str__(self):
        return f"{self.package_type} - {self.service.name}"
    
    def get_display_price(self):
        """Displays the price range, handling None values for the Admin add form."""
        if self.min_price_usd is None or self.max_price_usd is None:
            # Return a string instead of trying to format None
            return "N/A (Enter Prices)" 
            
        if self.min_price_usd == self.max_price_usd:
            return f"${self.min_price_usd:,.2f}"
        return f"${self.min_price_usd:,.0f} - ${self.max_price_usd:,.0f}"

class PackageFeature(models.Model):
    """Individual features that belong to a package."""
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='features')
    feature_text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "4. Package Features"
        ordering = ['order']

    def __str__(self):
        return self.feature_text

# --- Payment & Order Models ---

class PaymentMethod(models.Model):
    """Payment methods configurable from the admin."""
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=50, unique=True, help_text="Internal code (e.g., DBT, PAYPAL, STRIPE).")
    is_enabled = models.BooleanField(default=False, help_text="If true, users can select this option at checkout.")
    is_visible = models.BooleanField(default=True, help_text="If true, the method is shown on the payment page (even if disabled).")
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "5. Payment Methods"
        ordering = ['sort_order']

    def __str__(self):
        status = "ENABLED" if self.is_enabled else "DISABLED"
        return f"{self.name} ({status})"

class Order(models.Model):
    """A simple model to represent a finalized order."""
    session_key = models.CharField(max_length=32, editable=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "6. Orders"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order #{self.id} - ${self.total_amount}"
