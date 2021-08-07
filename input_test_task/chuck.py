import requests
import re

def random_joke():
   
    """ 
Function "random_joke()" prints to the console one random fact about Chuck Norris by each category (sorted by date of creation).
Source: api.chucknorris.io.
Format:
Date: <creation date>
Category: <category name>
Text: <text>
    """

    #get a list of all categories - json_category
    category_url = "https://api.chucknorris.io/jokes/categories"
    category_result = requests.get(category_url)
    json_category = category_result.json()
    
    #create blank list for result
    res_list =[]
    
    for category in json_category:
        #get a dictionary consisting of one joke for one category
        joke_url = f"https://api.chucknorris.io/jokes/random?category={category}"
        result = requests.get(joke_url)
        json_result = result.json()
        
        #create a list for key values: "created_at", "categories", "value" for one joke for one category
        joke_list=[]

        #get values from keys: "created_at", "categories", "value"
        res_date = json_result["created_at"]
        res_category = json_result["categories"]
        res_text = json_result["value"]

        #add values from keys: "created_at", "categories", "value" to a joke_list
        joke_list.append(res_date)
        joke_list.append(res_category)
        joke_list.append(res_text)

        #add one joke for one category to a list for result
        res_list.append(joke_list)

    #create list for sorted list for results by first element (Date)
    sort_res_list=sorted(res_list, key=lambda k: k[0])
    
    for i in range(len(sort_res_list)):
        #organize strings for output by format
        Date = f"Date: {sort_res_list[i][0]} \n"
        Category = f"Category: {sort_res_list[i][1]} \n"
        Text = f"Text: {sort_res_list[i][2]} \n"

        #change format of value of key "categories" from ['category'] to category (without characters [''])
        re_category = re.sub('\[|\]|\'', '', Category) 

        #final output
        print(Date + re_category + Text) 
                
random_joke()

