from flask import Flask, render_template, request, jsonify

import pandas
import numpy as np

popular_df = pandas.read_pickle('popular.pkl')

pt = pandas.read_pickle('pt.pkl')
print(pt)
books = pandas.read_pickle('books.pkl')
print(popular_df)
similarity_scores = pandas.read_pickle('similarity_scores.pkl')
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           book_name=popular_df['Book-Title'].to_list(),
                           author=popular_df['Book-Author'].to_list(),
                           image=popular_df['Image-URL-M'].to_list(),
                           votes=popular_df['num_ratings'].to_list(),
                           rating=popular_df['avg_rating'].to_list()
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    # Get the user input from the form
    user_input = request.form.get('user_input')

    # Check if the user input is in the index
    if user_input in pt.index:
        # Find the index of the book in the index dataframe
        index = np.where(pt.index == user_input)[0][0]

        user_input_image_url = popular_df.loc[popular_df['Book-Title'] == user_input, 'Image-URL-M'].iloc[0]
        user_input_author = popular_df.loc[popular_df['Book-Title'] == user_input, 'Book-Author'].iloc[0]
        user_input_ratings = popular_df.loc[popular_df['Book-Title'] == user_input, 'avg_rating'].iloc[0]

        # round up the ratings to the nearest two digits
        user_input_ratings = int(user_input_ratings * 100 + 0.5) / 100

        # Find similar items based on the similarity scores
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(temp_df.drop_duplicates('Book-Title')['Book-Title'].to_list())
            item.extend(temp_df.drop_duplicates('Book-Title')['Book-Author'].to_list())
            item.extend(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].to_list())

            data.append(item)

        # Render the recommend.html template with the data
        return render_template('recommend.html', data=data, user_input=user_input,
                               user_input_image_url=user_input_image_url, user_input_author=user_input_author,
                               user_input_ratings=user_input_ratings)
    else:
        # If the book is not found in the index, return an error message
        return render_template('error.html', message="Book not found in the index. Please enter a valid book name.")


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    term = request.form['term'].lower()
    matching_books = popular_df.loc[popular_df['Book-Title'].str.lower().str.contains(term)]
    suggestions = []
    for index, row in matching_books.iterrows():
        suggestion = {
            'title': row['Book-Title'],
            'image_url': row['Image-URL-M']
        }
        suggestions.append(suggestion)
    return jsonify(suggestions[:10])


@app.route('/aboutus')
def aboutus_ui():
    return render_template('aboutus.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
