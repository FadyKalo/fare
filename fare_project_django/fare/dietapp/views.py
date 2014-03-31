from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, loader
from dietapp.models import Recipe, Diet
from django.contrib.auth import logout

from yummly import *
import json
from helpFunc import fetch_meals, getRecipeInfo

# needed in the register() view
from dietapp.forms import UserForm, UserProfileForm


def recipes(request):
	recipe_list = Recipe.objects.order_by('name')[:5]
	template = 'dietapp/recipes.html'
	context = {
	'recipe_list': recipe_list,
	}
	return render(request, template, context)


def recipe(request, recipe_id):
	try:
		recipe = Recipe.objects.get(pk=recipe_id)
	except Recipe.DoesNotExist:
		raise Http404
	return render(request, 'dietapp/recipe.html', {'recipe': recipe})


def diets(request):
	diet_list = Diet.objects.order_by('name')[:5]
	template = loader.get_template('dietapp/diets.html')
	context = RequestContext(request, {
	'diet_list': diet_list,
	})
	return HttpResponse(template.render(context))


def diet(request, diet_id):
	try:
		diet = Diet.objects.get(pk=diet_id)
	except Recipe.DoesNotExist:
		raise Http404
	return render(request, 'dietapp/diet.html', {'diet': diet})


# get_recipes --> view function where we have a second parameter ( i.e: breakfast, dinner, lunch) and we call the yummly Api.
@login_required
def get_recipes(request, meal):
	myDiet = request.GET.get('diet', '')
	mealList = fetch_meals(meal, myDiet)
	return HttpResponse(json.dumps(mealList), content_type="application/json")


@login_required
def diets_v2(request):
	diet_list = Diet.objects.order_by('name')[:5]
	template = loader.get_template('dietapp/diets_v2.html')
	context = RequestContext(request, {
	'diet_list': diet_list,
	})
	return HttpResponse(template.render(context))


@login_required
def recipes_v2(request):
	diet_list = Diet.objects.order_by('name')[:5]
	template = loader.get_template('dietapp/recipes_v2.html')
	context = RequestContext(request, {
	'diet_list': diet_list,
	})
	return HttpResponse(template.render(context))


@login_required
def recipeInfo(request):
	recipe_id = request.GET.get('recipe_id', '')
	if recipe_id != '':
		# info is a list of 2 lists where the first list is Ingredients and the second is nutrition
		info = getRecipeInfo(recipe_id)
	else:
		# handle errors
		info = {'error': 'Recipe Id field is required!'}
	return HttpResponse(json.dumps(info), content_type="application/json")


def register(request):
	# Like before, get the request's context.
	context = RequestContext(request)

	# A boolean value for telling the template whether the registration was successful.
	# Set to False initially. Code changes value to True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		# If the two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile instance.
			# Since we need to set the user attribute ourselves, we set commit=False.
			# This delays saving the model until we're ready to avoid integrity problems.
			profile = profile_form.save(commit=False)
			profile.user = user

			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now we save the UserProfile model instance.
			profile.save()

			# Update our variable to tell the template registration was successful.
			registered = True

		# Invalid form or forms - mistakes or something else?
		# Print problems to the terminal.
		# They'll also be shown to the user.
		else:
			print user_form.errors, profile_form.errors

	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	# Render the template depending on the context.
	return render_to_response('dietapp/register.html',
							  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}, context)


def user_login(request):
	# Like before, obtain the context for the user's request.
	context = RequestContext(request)

	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
		username = request.POST['username']
		password = request.POST['password']

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credentials was found.
		if user is not None:
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect('/dietapp/')
			else:
				# An inactive account was used - no logging in!
				return HttpResponse("Your Dietapp account is disabled.")
		else:
			# Bad login details were provided. So we can't log the user in.
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")

	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render_to_response('dietapp/login.html', {}, context)


@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)

	# Take the user back to the homepage.
	return HttpResponseRedirect('/dietapp/')