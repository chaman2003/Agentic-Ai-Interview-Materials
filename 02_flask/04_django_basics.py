"""
DJANGO BASICS - Models, ORM, Migrations, Views, URLs, DRF Serializers
For: Python GenAI Developer Interview
Compare with Flask: Flask is micro-framework, Django is batteries-included

Install: pip install django djangorestframework
Create project: django-admin startproject myproject
Create app: python manage.py startapp cases
Run: python manage.py runserver
"""

# ============================================================
# 1. PROJECT STRUCTURE
# ============================================================
"""
myproject/
├── manage.py                  # CLI tool (runserver, migrate, createsuperuser)
├── myproject/
│   ├── settings.py            # All config (DB, INSTALLED_APPS, middleware)
│   ├── urls.py                # Root URL config
│   └── wsgi.py                # Production server entry point
└── cases/                     # Your app
    ├── models.py              # DB models (ORM)
    ├── views.py               # Request handlers
    ├── urls.py                # App-level URL config
    ├── serializers.py         # DRF serializers (like Pydantic for Django)
    ├── admin.py               # Register models for admin panel
    └── migrations/            # Auto-generated DB migrations
        └── 0001_initial.py
"""

# ============================================================
# 2. SETTINGS.PY - Key Config
# ============================================================
"""
# myproject/settings.py (key parts)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'rest_framework',          # DRF
    'corsheaders',              # django-cors-headers
    'cases',                   # Your app
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'casedb',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
"""

# ============================================================
# 3. MODELS.PY - Database Models (ORM)
# ============================================================
"""
# cases/models.py

from django.db import models
from django.contrib.auth.models import User  # Built-in User model


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Set on create

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']  # Default ordering

    def __str__(self):
        return self.name


class Case(models.Model):
    # Field types
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    # Text fields
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)  # blank=True means form allows empty

    # Number fields
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    priority = models.IntegerField(default=1)

    # Choice field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    # Boolean
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Set once on creation
    updated_at = models.DateTimeField(auto_now=True)       # Updated every save

    # Relationships
    # ForeignKey = many-to-one (many cases, one category)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # If category deleted, set to NULL
        null=True,
        blank=True,
        related_name='cases'        # category.cases.all() reverse access
    )

    # ForeignKey to built-in User
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cases'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Delete cases if user deleted
        related_name='created_cases'
    )

    class Meta:
        ordering = ['-created_at']  # Newest first
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_by', 'status']),
        ]

    def __str__(self):
        return f"Case #{self.id}: {self.title}"


# ManyToMany example
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    cases = models.ManyToManyField(Case, blank=True, related_name='tags')

    def __str__(self):
        return self.name
"""

# ============================================================
# 4. MIGRATIONS - Version-controlled DB schema changes
# ============================================================
"""
# Generate migration after changing models:
python manage.py makemigrations

# Apply migrations to DB:
python manage.py migrate

# Show migration status:
python manage.py showmigrations

# Generated migration file looks like:
# cases/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=20, default='open')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

# IMPORTANT: Always run makemigrations + migrate after changing models!
"""

# ============================================================
# 5. DJANGO ORM - Querying the Database
# ============================================================
"""
# Django ORM - never write raw SQL (usually)
# All examples would run in django shell: python manage.py shell

# ── CREATE ──
case = Case.objects.create(
    title="Billing Dispute",
    status="open",
    amount=1500.00
)

# ── READ ──
# Get all
cases = Case.objects.all()

# Get one (raises DoesNotExist if not found)
case = Case.objects.get(id=1)

# Filter (returns QuerySet - lazy, not executed until iterated)
open_cases = Case.objects.filter(status='open')
high_priority = Case.objects.filter(priority__gt=3)   # priority > 3
recent = Case.objects.filter(created_at__date=today)

# Double underscore (__) for lookups:
# __gt, __gte, __lt, __lte    → comparison
# __contains, __icontains    → LIKE '%value%' (i = case-insensitive)
# __startswith, __endswith   → LIKE 'value%'
# __in                       → IN (list)
# __isnull                   → IS NULL / IS NOT NULL
# __date, __year, __month    → date parts

# Chain filters
results = Case.objects.filter(
    status='open',
    amount__gte=1000,
    title__icontains='billing'
).order_by('-created_at')[:10]  # ORDER BY DESC, LIMIT 10

# Exclude
active = Case.objects.exclude(status='closed')

# get_or_create
case, created = Case.objects.get_or_create(
    title="Test Case",
    defaults={"status": "open", "amount": 0}
)

# ── UPDATE ──
# Update single object
case = Case.objects.get(id=1)
case.status = 'resolved'
case.save()

# Bulk update (one SQL query - efficient!)
Case.objects.filter(status='open').update(priority=2)

# ── DELETE ──
Case.objects.get(id=1).delete()         # Delete one
Case.objects.filter(status='closed').delete()  # Bulk delete

# ── AGGREGATIONS ──
from django.db.models import Count, Sum, Avg, Max, Min

Case.objects.count()  # Total count
Case.objects.filter(status='open').count()

# Aggregate (single result)
from django.db.models import Avg
result = Case.objects.aggregate(avg_amount=Avg('amount'))
# result = {'avg_amount': 1250.0}

# Annotate (per-row calculation)
from django.db.models import Count
categories = Category.objects.annotate(
    case_count=Count('cases')
).order_by('-case_count')
# Each category object now has .case_count attribute

# ── RELATED OBJECTS ──
# Forward access (ForeignKey)
case = Case.objects.get(id=1)
category = case.category  # Access related object

# Reverse access (related_name)
category = Category.objects.get(id=1)
cases = category.cases.all()  # All cases for this category

# Select related (JOIN - avoids N+1 queries!)
cases = Case.objects.select_related('category', 'created_by').filter(status='open')
# Now accessing case.category does NOT hit DB again

# Prefetch related (for ManyToMany or reverse ForeignKey)
cases = Case.objects.prefetch_related('tags').filter(status='open')
"""

# ============================================================
# 6. VIEWS.PY - Request Handlers (Two approaches)
# ============================================================
"""
# Approach 1: Function-Based Views (FBV) - simple
# cases/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["GET"])
def case_list(request):
    cases = Case.objects.filter(is_active=True).values(
        'id', 'title', 'status', 'amount', 'created_at'
    )
    return JsonResponse(list(cases), safe=False)


# Approach 2: Class-Based Views (CBV)
from django.views import View

class CaseDetailView(View):
    def get(self, request, case_id):
        try:
            case = Case.objects.get(id=case_id)
            return JsonResponse({'id': case.id, 'title': case.title})
        except Case.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

    def put(self, request, case_id):
        data = json.loads(request.body)
        Case.objects.filter(id=case_id).update(**data)
        return JsonResponse({'message': 'Updated'})
"""

# ============================================================
# 7. URLS.PY - URL Routing
# ============================================================
"""
# cases/urls.py (app-level)
from django.urls import path
from . import views

urlpatterns = [
    path('cases/', views.case_list, name='case-list'),
    path('cases/<int:case_id>/', views.CaseDetailView.as_view(), name='case-detail'),
]

# myproject/urls.py (root)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),         # Built-in admin panel
    path('api/v1/', include('cases.urls')),  # Include app URLs
    path('api/auth/', include('rest_framework.urls')),
]
"""

# ============================================================
# 8. DRF SERIALIZERS - Like Pydantic for Django REST Framework
# ============================================================
"""
# cases/serializers.py
from rest_framework import serializers
from .models import Case, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']  # Which fields to expose
        read_only_fields = ['id']

class CaseSerializer(serializers.ModelSerializer):
    # Nested serializer (read)
    category = CategorySerializer(read_only=True)
    # Write-only FK (for creating/updating)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        allow_null=True
    )

    class Meta:
        model = Case
        fields = [
            'id', 'title', 'description', 'status', 'amount',
            'priority', 'category', 'category_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    # Custom validation
    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount cannot be negative")
        return value

    def validate(self, data):
        # Cross-field validation
        if data.get('status') == 'resolved' and not data.get('amount'):
            raise serializers.ValidationError(
                "Resolved cases must have an amount"
            )
        return data
"""

# ============================================================
# 9. DRF VIEWS (ViewSet) - Full CRUD with minimal code
# ============================================================
"""
# cases/views.py (DRF version)
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Case
from .serializers import CaseSerializer

class CaseViewSet(viewsets.ModelViewSet):
    # ModelViewSet auto-provides: list, create, retrieve, update, destroy
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter by current user + optional status filter
        queryset = Case.objects.select_related('category').filter(
            created_by=self.request.user
        )
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        # Auto-set created_by to current user
        serializer.save(created_by=self.request.user)

    # Custom action: /api/cases/{id}/resolve/
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        case = self.get_object()
        case.status = 'resolved'
        case.save()
        return Response({'message': f'Case {case.id} resolved'})

    # Custom list action: /api/cases/my_open/
    @action(detail=False, methods=['get'])
    def my_open(self, request):
        cases = self.get_queryset().filter(status='open')
        serializer = self.get_serializer(cases, many=True)
        return Response(serializer.data)


# Register with Router in urls.py:
# from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'cases', CaseViewSet, basename='case')
# urlpatterns += router.urls
# This auto-generates:
# GET    /api/cases/         → list
# POST   /api/cases/         → create
# GET    /api/cases/{id}/    → retrieve
# PUT    /api/cases/{id}/    → update
# PATCH  /api/cases/{id}/    → partial_update
# DELETE /api/cases/{id}/    → destroy
# POST   /api/cases/{id}/resolve/  → custom action
"""

# ============================================================
# 10. ADMIN.PY - Register models for the admin panel
# ============================================================
"""
# cases/admin.py
from django.contrib import admin
from .models import Case, Category

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'amount', 'created_by', 'created_at']
    list_filter = ['status', 'category', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

# Create superuser: python manage.py createsuperuser
# Visit: http://localhost:8000/admin/
"""

# ============================================================
# FLASK VS DJANGO COMPARISON
# ============================================================
"""
| Feature            | Flask                        | Django                          |
|--------------------|------------------------------|---------------------------------|
| Type               | Micro-framework              | Full-stack / batteries included |
| ORM                | SQLAlchemy (3rd party)       | Built-in Django ORM             |
| Admin Panel        | Flask-Admin (plugin)         | Built-in                        |
| Auth               | Flask-Login (plugin)         | Built-in                        |
| Forms              | WTForms (plugin)             | Built-in forms                  |
| REST API           | Flask-RESTX (plugin)         | Django REST Framework (DRF)     |
| Migrations         | Flask-Migrate/Alembic        | Built-in                        |
| Project Size       | Small to medium APIs         | Medium to large apps            |
| Learning Curve     | Easy                         | Steeper (more concepts)         |
| Flexibility        | High (choose your own stack) | Lower (opinionated)             |
| Use case           | Microservices, ML APIs       | E-commerce, CMS, complex apps   |

When to choose Django:
- Need admin panel quickly
- Complex relational data with lots of models
- Full-featured web app (auth, sessions, etc)
- Team is familiar with Django patterns

When to choose Flask (or FastAPI):
- Simple REST API
- ML/AI microservices (document AI use case)
- Need async (use FastAPI instead)
- Maximum flexibility
"""

# ============================================================
# QUICK REFERENCE - Management Commands
# ============================================================
"""
django-admin startproject myproject   # Create project
python manage.py startapp cases       # Create app
python manage.py runserver            # Dev server (port 8000)
python manage.py runserver 0.0.0.0:8080  # Custom host/port

python manage.py makemigrations       # Generate migration files
python manage.py migrate              # Apply migrations to DB
python manage.py showmigrations       # List migration status
python manage.py sqlmigrate cases 0001  # Show SQL for migration

python manage.py createsuperuser      # Create admin user
python manage.py shell                # Python shell with Django loaded
python manage.py dbshell              # Raw DB shell

python manage.py test cases           # Run tests for 'cases' app
python manage.py collectstatic        # Gather static files for production
"""
