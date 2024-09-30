# how to use the functions.



# loans
to post loan: 
{
    "cust_id": 1,
    "book_id": 2,
    "loan_date": "2024-09-28"
}
add book:
{
    "name": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "year_published": 1925,
    "type": 1
}


add book: 
{
    "name": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "year_published": 1925,
    "type": 1
}


find book by name:
GET http://127.0.0.1:5000/books/search/The%20Great%20Gatsby
in the url we need to put the name of the book and if we have space we need to replace it with %20




to do: 
return book
Remove book  
Remover customer 