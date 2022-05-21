import csv
from operator import itemgetter
import requests


def fetch_data(api_url):
    try:
        response = requests.get(f"{api_url}", timeout=3)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()['entries']
        else:
            print(
                f"There's a {response.status_code} error with the request")

    except requests.ConnectionError as error:
        return error


def extract_images(image_list):
    if len(image_list) == 0:
        return

    images = []
    for image in image_list:
        images.append(image['url'])
    return ''.join(images) if len(image_list) == 1 else ','.join(images)


def map_data(api_url):
    mapped_list = []
    api_data = fetch_data(api_url)
    for article in api_data:
        article_content = article['content']
        mapped_list.append(
            dict(guid=article_content['guid'], title=article_content['title'], related_image_urls=extract_images(article_content['images']), publish_date=article_content['published_at'], creation_date=article_content['created_at'], recurrence_count_sum=0))
    return mapped_list


def create_recurrence_data_set(article_data):
    word_count_weight = {}

    for article in article_data:
        for word in article['title'].split():
            if word in word_count_weight:
                word_count_weight[word] = word_count_weight[word] + 1
            else:
                word_count_weight[word] = 1

    # ommiting all the values that are less than 1
    word_count_weight = {key: val for key,
                         val in word_count_weight.items() if val > 1}

    return word_count_weight


def text_weight_distribution(api_url):
    article_data = map_data(api_url)
    # making a weight dataset out of the articles that we found
    recurrence_dataset = create_recurrence_data_set(article_data)

    # adding incremental weight to the title. 
    # If there is more words the weight will be greater
    for article in article_data:
        for word in article['title'].split():
            if word in recurrence_dataset:
                article['recurrence_count_sum'] = article['recurrence_count_sum'] + \
                    recurrence_dataset[word]

    return article_data


def sort_recurrence_article(api_url, max_count):
    pick_max_article = max_count

    # assinging text title weight
    article_with_weight = text_weight_distribution(api_url)

    # sort the article by their weight
    article_with_weight = sorted(
        article_with_weight, key=itemgetter('recurrence_count_sum'), reverse=True)
    
    total_article_length = len(article_with_weight)
    if pick_max_article >= total_article_length:
        return article_with_weight

    # if there is tie picking them up and increasing pick count
    tie_value = article_with_weight[pick_max_article-1]['recurrence_count_sum']
    for article in article_with_weight[pick_max_article:]:
        if tie_value == article['recurrence_count_sum']:
            pick_max_article = pick_max_article + 1
        else:
            break

    return article_with_weight[:pick_max_article]


def print_sorted_article(output_file):
    api_url, print_max = "https://api.welcomesoftware.com/v2/feed/49e82ccda46544ff4e48a5fc3f04e343?format=json", 3
    json_output = sort_recurrence_article(api_url, print_max)

    # writing json file
    if len(json_output):
        headers = json_output[0].keys()

        with open(output_file, 'w', newline='') as json_file:
            dict_writer = csv.DictWriter(json_file, headers)
            dict_writer.writeheader()
            dict_writer.writerows(json_output)
            json_file.close()

    return json_output


if __name__ == "__main__":
    print(print_sorted_article('output.csv'))
