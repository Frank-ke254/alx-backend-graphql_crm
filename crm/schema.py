import re
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello from CRM GraphQL!")
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.String())
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.String())
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.String())

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        return qs.order_by(order_by) if order_by else qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        return qs.order_by(order_by) if order_by else qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        return qs.order_by(order_by) if order_by else qs


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        if phone and not re.match(r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$', phone):
            raise Exception("Invalid phone format")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.NonNull(graphene.JSONString), required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []

        for record in input:
            try:
                name = record.get("name")
                email = record.get("email")
                phone = record.get("phone")

                if not name or not email:
                    raise ValidationError("Name and email are required")

                if Customer.objects.filter(email=email).exists():
                    raise ValidationError(f"Duplicate email: {email}")

                if phone and not re.match(r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$', phone):
                    raise ValidationError(f"Invalid phone: {phone}")

                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise Exception("No valid products found")

        total_amount = sum([p.price for p in products])

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date or timezone.now()
        )
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)


class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)

        message = f"{len(updated)} products updated." if updated else "No low-stock products found."
        return UpdateLowStockProducts(success=True, message=message, updated_products=updated)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
