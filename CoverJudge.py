# Cover Judge
# Import flask, render_template and request
from flask import Flask, render_template, request, redirect
# Import csv module to work with csv files
import csv
# Import requests module to make HTTP requests
import requests
import os

# Create an instance of the Flask class
app = Flask(__name__)

#create or open csv file for storing book cover reviews
fields = ['book_name', 'book_author', 'cover_review', 'cover_score', 'isbn', 'book_cover','review_id']

if not os.path.isfile('bookCoverReviews.csv'):
    with open('bookCoverReviews.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
else:
    with open('bookCoverReviews.csv', 'a') as csvfile:
        pass

# Define the route for the index page
@app.route('/')
def index():
    # Define an empty list to store the book names
    books = []
    # Open the bookCoverReviews.csv file in read mode
    with open('bookCoverReviews.csv', 'r') as csvfile:
        # Create a csv dictionary reader object
        reader = csv.DictReader(csvfile)
        # Loop through each row in the csv file
        for row in reader:
            # Append a dictionary representing a book to the books list
            book = {'book_name': row['book_name'], 'book_author': row['book_author'], 'isbn': row['isbn'], 'book_cover': row['book_cover'], 'review_id': row['review_id']}
            books.append(book)
    # Return the index.html template with title and books as keyword arguments
    return render_template('index.html', title='Cover Judge: book cover reviews', books=books)  

    
# Define the route for the post-review page
@app.route('/post-review', methods=['GET', 'POST'])
def post_review():
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the form data from the request object
        book_name = request.form.get('book_name')
        book_author = request.form.get('book_author')
        cover_review = request.form.get('cover_review')
        cover_score = request.form.get('cover_score')

        # Validate the form data
        if book_name and book_author and cover_review and cover_score:
            # Convert the cover_score to an integer
            try:
                cover_score = int(cover_score)
            except ValueError:
                # Return an error message if the cover_score is not an integer
                return 'Invalid cover score. Please enter an integer between 1 and 10.'

            # Check if the cover_score is between 1 and 10
            if cover_score < 1 or cover_score > 10:
                # Return an error message if the cover_score is out of range
                return 'Invalid cover score. Please enter an integer between 1 and 10.'

            # Use openlibrary.org API to get ISBN by book name and author name
            # Construct a query string with book name and author name parameters
            query = f'q={book_name}+{book_author}'
            # Construct a URL for the books API with json format and query string
            url = f'https://openlibrary.org/search.json?{query}'
            # Make a GET request to the URL and get the response as json data
            response = requests.get(url).json()
            # Check if there are any docs in the response data
            if response['docs']:
                # Get the first doc from the response data
                doc = response['docs'][0]
                # Check if there is an isbn field in the doc
                if 'isbn' in doc:
                    # Get the first isbn from the doc as a string
                    isbn = str(doc['isbn'][0])
                    # Use openlibrary.org API to get book cover image source url by ISBN
                    # Construct a URL for the covers API with json format and ISBN parameter
                    url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'
                    # Make a GET request to the URL and get the response as json data
                    response = requests.get(url).json()
                    # Check if there is any data in the response for the ISBN key
                    if f'ISBN:{isbn}' in response:
                        # Get the data for the ISBN key from the response 
                        data = response[f'ISBN:{isbn}']
                        # Check if there is a cover field in the data 
                        if 'cover' in data:
                            # Get the medium size cover image source url from the data 
                            book_cover = data['cover']['medium']
                        else:
                            # Set book_cover to default if no cover field is found 
                            book_cover = 'https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg'
                    else:
                        # Set book_cover to a default if no data is found for the ISBN key
                        book_cover = 'https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg'
                else:
                    # Set isbn to a default string if no isbn field is found
                    isbn = f'No ISBN found for {book_name} by {book_author}'
            else:
                # Set isbn to a default string if no docs are found
                isbn = f'No ISBN found for {book_name} by {book_author}'
            #creates a unique review id number to avoid issues with multiple reviews for the same book cover.
            review_id = f'{len(book_name)}{len(book_author)}{len(book_cover)}{len(book_name)*len(book_author)*len(cover_review)*(cover_score)}{len(isbn)}{len(cover_review)}{cover_score}{len(cover_review)*(cover_score)}'

            # Open the csv file in append mode
            with open('bookCoverReviews.csv', 'a') as f:
                # Create a csv writer object
                writer = csv.writer(f)
                # Write a row with the form data and isbn
                writer.writerow([book_name, book_author, cover_review, cover_score, isbn, book_cover,review_id])
                return redirect ('/')
        else:
            # Return an error message if any of the form data is missing
            return 'Please fill in all the fields.'
    else:
        # Render the post-review.html template and pass the title as a variable
        return render_template('post-review.html', title='Post a review')

@app.route('/book/<review_id>')
def view_review(review_id):
     # Open the bookCoverReviews.csv file in read mode
    with open('bookCoverReviews.csv', 'r') as f:
        # Create a csv dictionary reader object
        reader = csv.DictReader(f)
        # Loop through each row in the csv file
        for row in reader:
            # Check if the review_id in the row matches the isbn in the URL parameter
            if row['review_id'] == review_id:
                # Return the book-page.html template with row as a keyword argument
                return render_template('book-page.html', book=row)
        else:
            # Return an error message if no matching book name is found in the csv file
            return redirect ('/')
        
if __name__ == '__main__':
    app.run(debug=True) # Start the server listening for requests