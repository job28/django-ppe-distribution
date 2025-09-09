# items/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Order
from .forms import OrderForm, SignupForm  # if you already added SignupForm; else keep OrderForm import only
from django.contrib import messages
from django.core.mail import EmailMessage
from .utils import generate_ics
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator


# NEW imports for Stripe Checkout
import stripe
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# Configure Stripe
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")

def _amount_cents(eur_amount: Decimal) -> int:
    """Convert a Decimal EUR amount to integer cents safely."""
    return int((eur_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100))


def index(request):
    qs = Item.objects.all().order_by('-id')  # newest first

    # Optional filters the template already supports
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(name__icontains=q)

    in_stock = request.GET.get('in_stock') == '1'
    if in_stock:
        qs = qs.filter(stock__gt=0)

    sort = request.GET.get('sort') or ''
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'name':
        qs = qs.order_by('name')

    paginator = Paginator(qs, 8)  # cards per page
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'index.html', {
        'page_obj': page_obj,
        'q': q,
        'in_stock': in_stock,
        'sort': sort,
    })


def buy_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if item.stock < quantity:
                messages.error(request, f"Only {item.stock} of {item.name} left in stock.")
                return render(request, 'order_form.html', {'form': form, 'item': item})

            order = form.save(commit=False)

            # For logged-in users, assign user + autofill details
            if request.user.is_authenticated:
                order.user = request.user
                order.customer_name = request.user.get_full_name() or request.user.username
                # Prefer the account email; fallback to form email if user.email is empty
                order.customer_email = request.user.email or form.cleaned_data.get('customer_email')

            # Ensure we have an email for everyone (guest or logged-in without email)
            if not order.customer_email:
                messages.error(request, "Please provide a valid email to receive your confirmation.")
                return render(request, 'order_form.html', {'form': form, 'item': item})

            order.item = item
            order.save()

            # Create Stripe Checkout Session (fulfillment happens in webhook)
            if not stripe.api_key:
                messages.error(request, "Payments are not configured yet. Missing STRIPE_SECRET_KEY.")
                return render(request, 'order_form.html', {'form': form, 'item': item})

            success_url = request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = request.build_absolute_uri(reverse('payment_cancel', args=[order.id]))

            session = stripe.checkout.Session.create(
                mode='payment',
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {'name': item.name},
                        'unit_amount': _amount_cents(Decimal(str(item.price))),
                    },
                    'quantity': quantity,
                }],
                customer_email=order.customer_email,
                metadata={'order_id': str(order.id)},
                success_url=success_url,
                cancel_url=cancel_url,
            )

            # Redirect user to Stripe-hosted payment page
            return redirect(session.url, code=303)

    else:
        # Prefill for convenience
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['customer_name'] = request.user.get_full_name() or request.user.username
            initial_data['customer_email'] = request.user.email
        form = OrderForm(user=request.user, initial=initial_data)

    return render(request, 'order_form.html', {'form': form, 'item': item})


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def signup(request):
    # keep your existing implementation if you customized it
    # shown here only for completeness
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Please log in.")
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'my_orders.html', {'orders': orders})


def custom_logout(request):
    logout(request)
    messages.success(request, "You’ve been logged out.")
    return redirect('home')  # or use 'items_index' if that's your items list


# ===== NEW: payment success/cancel (UX only) =====
def payment_success(request):
    messages.success(request, "Payment received! We’ll email your pickup details shortly.")
    return render(request, 'home.html')  # or a dedicated success template


def payment_cancel(request, order_id):
    messages.info(request, "Payment canceled. Your order was not completed.")
    order = get_object_or_404(Order, id=order_id)
    return redirect('buy_item', item_id=order.item.id)


# ===== NEW: Stripe webhook to finalize the order =====
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')

        try:
            order = Order.objects.select_related('item', 'pickup_hub').get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponse(status=200)  # idempotent no-op

        # ⚠️ Minimal version (no payment_status field):
        # Fulfill once. In production, add a 'paid' flag on Order to guarantee idempotency.
        item = order.item
        if item.stock >= order.quantity:
            item.stock -= order.quantity
            item.save()

            # Send confirmation email + ICS
            ics_file = generate_ics(order)
            email = EmailMessage(
                subject=f"PPE Pickup Confirmation - {order.item.name}",
                body=(
                    f"Hi {order.customer_name},\n\n"
                    f"Thanks for your donation and order!\n\n"
                    f"Item: {order.item.name} x {order.quantity}\n"
                    f"Pickup Location: {order.pickup_hub.name}\n"
                    f"Address: {order.pickup_hub.address}\n"
                    f"Date/Time: {order.pickup_datetime.strftime('%Y-%m-%d %H:%M')}\n\n"
                    "Attached is a calendar invite for your convenience.\n"
                    "Your contribution supports low-income community areas!\n\n"
                    "Thank you!"
                ),
                from_email=None,
                to=[order.customer_email],
            )
            try:
                email.attach(f"ppe_pickup_order_{order.id}.ics", ics_file.read(), 'text/calendar')
                email.send()
            except Exception:
                pass  # don’t fail the webhook on email issues

    return HttpResponse(status=200)
