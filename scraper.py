from bs4 import BeautifulSoup
import requests
import time
import datetime
import models
import lxml

def log_exception(url, exception_type):
	models.ScrapeException.create(
		url=url,
		exception_type=exception_type
	)

def get_all_recipes_urls(query):
	try:
		search_url = "https://www.allrecipes.com/search/results"
		payload = {"wt": query}
		search_response = requests.get(search_url, payload)
		search_soup = BeautifulSoup(search_response.text, "lxml")
		recipe_urls = search_soup.find_all("div", class_="fixed-recipe-card__info")
		recipe_urls = [url.find("a")["href"] for url in recipe_urls]
		return recipe_urls
	except AttributeError:
		log_exception(search_url + payload, "AttributeError")
		return []
	except KeyError:
		log_exception(search_url + payload, "KeyError")
		return []


def scrape_all_recipes_recipe(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "lxml")
	try:
		soup.find("body")["class"]
		title = str(soup.find("h1", class_="headline").string)
		ingredients = soup.find_all("span", class_="ingredients-item-name")
		ingredients = [str(ingredient.string).strip() for ingredient in ingredients]
		instruction_section = soup.find("ul", class_="instructions-section")
		instructions = [str(p.string) for p in instruction_section.find_all("p")]
	except KeyError:
		try:
			title = str(soup.find("h1", id="recipe-main-content").string)
			ingredients = soup.find_all("span", itemprop="recipeIngredient")
			ingredients = [str(ingredient.string).strip() for ingredient in ingredients]
			instructions = soup.find_all("span", class_="recipe-directions__list--item")
			instructions = [str(instruction.string) for instruction in instructions if instruction.string]
		except AttributeError:
			log_exception(url, "AttributeError")
			return False
		except KeyError:
			log_exception(url, "KeyError")
			return False
	except AttributeError:
		log_exception(url, "AttributeError")
		return False
	finally:
		return {
			"url": url,
			"title": title,
			"ingredients": ingredients,
			"instructions": instructions,
		}

def get_food_network_urls(query):
	try:
		food_nw_query = query.replace(" ", "-") + "-"
		search_url = "https://foodnetwork.com/search/" + food_nw_query
		search_response = requests.get(search_url, verify=False)
		soup = BeautifulSoup(search_response.text, "lxml")
		recipe_urls = soup.find_all("h3", class_="m-MediaBlock__a-Headline")
		recipe_urls = ["https:" + url.find("a")["href"] for url in recipe_urls]
		return recipe_urls
	except AttributeError:
		log_exception(search_url, "AttributeError")
		return []
	except KeyError:
		log_exception(search_url, "KeyError")
		return []


def scrape_food_network_recipe(url):
	try:
		response = requests.get(url)
		soup = BeautifulSoup(response.text, "lxml")
		title = str(soup.find("span", class_="o-AssetTitle__a-HeadlineText").string)
		print(title)
		ingredients = soup.find_all("p", class_="o-Ingredients__a-Ingredient")
		ingredients = [str(ingredient.string) for ingredient in ingredients]
		instructions = soup.find_all("li", class_="o-Method__m-Step")
		instructions = [str(instruction.string).strip() for instruction in instructions]
		return {
			"url": url,
			"title": title,
			"ingredients": ingredients,
			"instructions": instructions
		}
	except AttributeError:
		log_exception(url, "AttributeError")
		return False
	except KeyError:
		log_exception(url, "KeyError")
		return False


def scrape_recipes(query, recipes_per_site):
	all_recipe_urls = get_all_recipes_urls(query)
	food_network_urls = get_food_network_urls(query)
	recipes = []
	for i in range(0, recipes_per_site):
		# time.sleep(1)
		if len(all_recipe_urls) >= i + 1:
			new_all_recipes_recipe = scrape_all_recipes_recipe(all_recipe_urls[i])
			if new_all_recipes_recipe:
				recipes.append(new_all_recipes_recipe)
		if len(food_network_urls) >= i + 1:
			new_food_network_recipe = scrape_food_network_recipe(food_network_urls[i])
			if new_food_network_recipe:
				recipes.append(new_food_network_recipe)
	return recipes


