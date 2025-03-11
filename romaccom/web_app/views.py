from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout 
from .models import Accommodation
# from django.contrib.auth.models import User
from .models import User

GLASGOW_POSTCODES = ["G1", "G2", "G3", "G4", "G5", "G11", "G12", "G13", "G14", "G15", "G20", "G21", "G22", "G23", "G31", "G32", "G33", "G34", "G40", "G41", "G42", "G43", "G44", "G45", "G46", "G51", "G52", "G53", "G61", "G62", "G64", "G65", "G66", "G67", "G68", "G69", "G70"]

# Home Page
def index(request):
    trending_accommodations = Accommodation.objects.order_by('-view_count')[:5]
    top_rated_accommodations = Accommodation.objects.order_by('-average_rating')[:5]
    return render(request, 'romaccom/home.html', {
        'trending_accommodations': trending_accommodations,
        'top_rated_accommodations': top_rated_accommodations
    })

# Home Page
def home_view(request):
    trending_accommodations = Accommodation.objects.order_by('-view_count')[:5]
    top_rated_accommodations = Accommodation.objects.order_by('-average_rating')[:5]
    return render(request, 'romaccom/home.html', {
        'trending_accommodations': trending_accommodations,
        'top_rated_accommodations': top_rated_accommodations,
        'glasgow_postcodes' : GLASGOW_POSTCODES,
    })

def search_results_view(request):
    query = request.GET.get('query', '').strip()
    postcode_prefix = request.GET.get('postcode', '').strip()

    results = Accommodation.objects.all()

    if postcode_prefix in GLASGOW_POSTCODES:
        results = results.filter(postcode__startswith=postcode_prefix)

    if query:
        results = results.filter(name__icontains=query)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        html = render(request, 'romaccom/search_results_partial.html', {'results': results}).content.decode('utf-8')
        return JsonResponse({'html': html})

    return render(request, 'romaccom/search_results.html', {
        'results': results,
        'query': query,
        'postcode_prefix': postcode_prefix,
        'glasgow_postcodes': GLASGOW_POSTCODES,
    })

# Trending Accommodations
def trending_view(request):
    trending_accommodations = Accommodation.objects.order_by('-view_count')[:10]
    return render(request, 'romaccom/trending.html', {'trending_accommodations': trending_accommodations})

# Top Rated Accommodations
def top_rated_view(request):
    top_rated_accommodations = Accommodation.objects.order_by('-average_rating')[:10]
    return render(request, 'romaccom/toprated.html', {'top_rated_accommodations': top_rated_accommodations})

# Contact Page
def contact_view(request):
    return render(request, 'romaccom/contact.html')

# About Page
def about_view(request):
    return render(request, 'romaccom/about.html')

# User Registration
def user_register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'romaccom/register.html')

# Operator Registration
def operator_register_view(request):
    if request.method == "POST":
        property_name = request.POST.get('property_name')
        password = request.POST.get('password')
        operator = User.objects.create_user(username=property_name, password=password)
        return redirect('operator_dashboard')
    return render(request, 'romaccom/register.html')

# User Login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'romaccom/login.html', {'error': 'Invalid username or password'})
    return render(request, 'romaccom/login.html')

# User Logout
def logout_view(request):
    logout(request)
    return redirect('home')

# User Account
def my_account_view(request):
    return render(request, 'romaccom/myaccount.html')

# User Reviews
def my_reviews_view(request):
    return render(request, 'romaccom/myreviews.html')

# Accommodation Search
def search_view(request):
    query = request.GET.get('query', '')
    results = Accommodation.objects.filter(name__icontains=query)
    return render(request, 'romaccom/search.html', {'results': results})

# Accommodation List
def accom_list_view(request):
    accommodations = Accommodation.objects.all()
    return render(request, 'romaccom/accomlist.html', {'accommodations': accommodations})

# Accommodation Details Page
def accom_page_view(request, accom_id):
    accommodation = Accommodation.objects.get(id=accom_id)
    return render(request, 'romaccom/accomdetail.html', {'accommodation': accommodation})

# Accommodation Reviews
def accom_reviews_view(request, accom_id):
    accommodation = Accommodation.objects.get(id=accom_id)
    return render(request, 'romaccom/reviews.html', {'accommodation': accommodation})

# Accommodation Map
def accom_map_view(request, accom_id):
    accommodation = Accommodation.objects.get(id=accom_id)
    return render(request, 'romaccom/map.html', {'accommodation': accommodation})

# Write a Review
def write_review_view(request, accom_id):
    accommodation = Accommodation.objects.get(id=accom_id)
    
    # Handle form submission if it's a POST request
    if request.method == 'POST':
        # Process form data
        # Create a new review
        # Redirect to accommodation detail page
        pass
        
    return render(request, 'romaccom/write-review.html', {'accommodation': accommodation})

# Operator Login
#The accommodation ID is properly passed from the accommodation detail page
#The operator login page gracefully handles cases where the accommodation might not exist
#The back link works properly in all cases
def operator_login_view(request):
    # Get accommodation ID from the URL parameters
    accom_id = request.GET.get('accommodation_id')
    error = None
    accommodation = None
    
    if accom_id:
        try:
            accommodation = Accommodation.objects.get(id=accom_id)
        except Accommodation.DoesNotExist:
            error = "Accommodation not found"
    
    if request.method == "POST":
        password = request.POST.get('password')
        post_accom_id = request.POST.get('accommodation_id')
        
        if post_accom_id:
            try:
                accommodation = Accommodation.objects.get(id=post_accom_id)
                # Check if the operator with this password owns this accommodation
                operator = Operator.objects.filter(accommodations=accommodation, password=password).first()
                
                if operator:
                    # Store operator info in session
                    request.session['operator_id'] = operator.id
                    request.session['operator_name'] = operator.name
                    return redirect('operator_dashboard')
                else:
                    error = "Invalid password for this accommodation operator"
            except Accommodation.DoesNotExist:
                error = "Accommodation not found"
        else:
            error = "No accommodation selected"
    
    return render(request, 'romaccom/operator-login.html', {
        'accommodation': accommodation,
        'error': error
    })

# Operator Dashboard
def operator_dashboard_view(request):
    return render(request, 'romaccom/operator-dashboard.html')

# My Listings
def my_listings_view(request):
    return render(request, 'romaccom/mylistings.html')

# Add New Accommodation
def add_accommodation_view(request):
    return render(request, 'romaccom/addnewaccommodation.html')

# Manage Accommodation Info
def manage_accom_info_view(request):
    return render(request, 'romaccom/manageaccommodationinfo.html')
